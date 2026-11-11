"""
DocUni - Central RAG Coordinator Service
Điều phối toàn diện quy trình Retrieval-Augmented Generation:
1. Ingestion: Document -> Text Extraction -> Chunking -> Vector Embedding -> Lưu PostgreSQL (document_embeddings)
2. Query / Chat: User Query -> Query Embedding -> Vector Search (kèm RBAC ACL) -> LLM Answer Synthesis -> Citation Formatting -> Lưu Lịch sử (ai_queries, ai_query_sources)
"""

import os
from typing import List, Dict, Any, Optional
from django.db import connection, transaction
from documents.models import Document, DocumentActivityLog
from .processor import DocumentProcessor
from .chunker import TextChunker
from .embedding import EmbeddingService
from .vector_search import VectorSearchService
from .llm_service import LLMService
from .citation_service import CitationService
from ..models import AIQuery, AIQuerySource, DocumentEmbedding


class RAGService:
    """Bộ điều phối trung tâm cho toàn bộ nghiệp vụ AI RAG DocUni."""

    @classmethod
    def process_and_index_document(cls, document: Document, user=None) -> Dict[str, Any]:
        """
        Quy trình nạp và lập chỉ mục (Document Ingestion Pipeline):
        Trích xuất văn bản từng trang -> Chia đoạn gối đầu -> Sinh vector L2 -> Ghi vào document_embeddings.
        """
        doc_id = document.id
        latest = document.latest_version

        # 1. Trích xuất các trang
        pages = []
        if latest and latest.file:
            fpath = str(latest.file)
            if not os.path.exists(fpath):
                from django.conf import settings
                alt = os.path.join(settings.BASE_DIR, 'media', fpath)
                if os.path.exists(alt):
                    fpath = alt
            pages = DocumentProcessor.extract_pages(fpath, os.path.basename(fpath))

        # Nếu không có nội dung file, tạo trang từ metadata tiêu đề và mô tả
        if not pages:
            subj_name = document.subject.subject_name if document.subject else "Chung"
            meta_text = (
                f"Tài liệu môn học: {document.title}.\n"
                f"Môn học: {subj_name}.\n"
                f"Mô tả tóm tắt: {document.description or 'Tài liệu học tập chính quy.'}"
            )
            pages = [{'page_number': 1, 'text': meta_text}]

        # 2. Phân đoạn văn bản (Text Chunking)
        chunks = TextChunker.chunk_pages(pages, chunk_size=120, chunk_overlap=25)
        if not chunks:
            chunks = [{'chunk_index': 0, 'page_number': 1, 'chunk_text': document.title, 'word_count': 5}]

        # 3. Ghi vào cơ sở dữ liệu PostgreSQL
        with connection.cursor() as cursor:
            # Lấy danh sách chunk hiện có của tài liệu
            cursor.execute("SELECT chunk_index, embedding_id FROM document_embeddings WHERE document_id = %s", [doc_id])
            existing_chunks = {row[0]: row[1] for row in cursor.fetchall()}

            for chunk_data in chunks:
                c_idx = chunk_data['chunk_index']
                c_text = chunk_data['chunk_text']
                emb_vec = EmbeddingService.get_embedding(c_text, dim=16)

                if c_idx in existing_chunks:
                    cursor.execute(
                        """
                        UPDATE document_embeddings
                        SET chunk_text = %s, embedding_array = %s, created_at = CURRENT_TIMESTAMP
                        WHERE embedding_id = %s
                        """,
                        [c_text, emb_vec, existing_chunks[c_idx]]
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO document_embeddings (document_id, chunk_index, chunk_text, embedding_array, created_at)
                        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                        """,
                        [doc_id, c_idx, c_text, emb_vec]
                    )

        # 4. Ghi nhận log hoạt động
        DocumentActivityLog.objects.create(
            document=document,
            user=user,
            action='UPDATE',
            description=f"AI Ingestion hoàn tất: {len(chunks)} đoạn văn bản (chunks) được lập chỉ mục vector vào PostgreSQL.",
        )

        return {
            'status': 'success',
            'document_id': doc_id,
            'title': document.title,
            'chunks_count': len(chunks),
            'pages_count': len(pages),
        }

    @classmethod
    def query(
        cls,
        query_text: str,
        user=None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        subject_id: Optional[int] = None,
        document_id: Optional[int] = None,
        top_k: int = 4
    ) -> Dict[str, Any]:
        """
        Quy trình hỏi đáp ngữ cảnh (RAG Question Answering Pipeline):
        1. Tạo vector embedding cho câu hỏi
        2. Tìm kiếm vector kết hợp RBAC ACL trên PostgreSQL
        3. Tổng hợp câu trả lời qua LLMService
        4. Định dạng citations
        5. Lưu lịch sử câu hỏi vào ai_queries & ai_query_sources
        """
        query_clean = query_text.strip()
        if not query_clean:
            return {'status': 'error', 'message': 'Vui lòng nhập nội dung câu hỏi.'}

        # 1. Sinh vector câu hỏi
        query_vec = EmbeddingService.get_embedding(query_clean, dim=16)

        # 2. Tìm kiếm các chunks ngữ cảnh phù hợp theo phân quyền
        matched_chunks = VectorSearchService.search(
            query_text=query_clean,
            query_vector=query_vec,
            user=user,
            subject_id=subject_id,
            document_id=document_id,
            top_k=top_k,
            threshold=0.10
        )

        # 3. Tổng hợp câu trả lời
        ai_response = LLMService.generate_answer(
            query=query_clean,
            context_chunks=matched_chunks,
            conversation_history=conversation_history
        )

        # 4. Định dạng nguồn trích dẫn
        citations = CitationService.format_citations(matched_chunks)

        # 5. Lưu lịch sử vào bảng ai_queries & ai_query_sources trong PostgreSQL
        auth_user = user if (user and getattr(user, 'is_authenticated', False)) else None
        
        with transaction.atomic():
            ai_query = AIQuery.objects.create(
                user=auth_user,
                query_text=query_clean,
                ai_response=ai_response
            )

            # Lưu các nguồn vào ai_query_sources
            for c in matched_chunks:
                try:
                    emb_id = c.get('embedding_id')
                    d_id = c.get('document_id')
                    if emb_id and d_id:
                        doc_ref = Document.objects.filter(pk=d_id).first()
                        emb_ref = DocumentEmbedding.objects.filter(pk=emb_id).first()
                        if doc_ref and emb_ref:
                            AIQuerySource.objects.create(
                                query=ai_query,
                                document=doc_ref,
                                embedding=emb_ref
                            )
                except Exception:
                    pass

        # Gom danh sách các tài liệu nguồn độc nhất
        unique_docs = {}
        for c in citations:
            did = c['document_id']
            if did not in unique_docs:
                unique_docs[did] = {
                    'document_id': did,
                    'title': c['title'],
                    'subject_name': c['subject_name'],
                    'department_name': c['department_name'],
                    'page_number': c['page_number'],
                    'relevant_snippet': c['relevant_snippet'],
                    'relevance_score': c['relevance_score'],
                    'relevance_percentage': c['relevance_percentage'],
                }

        return {
            'status': 'success',
            'query_id': ai_query.query_id,
            'query': query_clean,
            'answer': ai_response,
            'citations': citations,
            'sources': list(unique_docs.values()),
            'chunks_found': len(matched_chunks),
            'created_at': ai_query.created_at.strftime('%Y-%m-%d %H:%M:%S') if ai_query.created_at else None,
        }
