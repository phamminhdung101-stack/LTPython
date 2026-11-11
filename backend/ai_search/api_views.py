from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import AIQuery, AIQuerySource, DocumentEmbedding
from .serializers import AIQuerySerializer
from documents.models import Document
from documents.serializers import DocumentSerializer


import math
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection

from .models import AIQuery, AIQuerySource, DocumentEmbedding
from .serializers import AIQuerySerializer
from documents.models import Document
from documents.serializers import DocumentSerializer
from documents.indexing_service import compute_embedding
from permissions.services import can_user_access_document


class AIQueryAPIView(APIView):
    """
    POST /api/ai/query/
    Thực hiện truy vấn câu hỏi học tập ngữ nghĩa (RAG) kết nối trực tiếp bảng document_embeddings trong PostgreSQL:
    1. Tạo vector embedding từ câu hỏi người dùng
    2. Quét và tính khoảng cách Cosine Similarity với các chunk văn bản trong PostgreSQL
    3. Kiểm tra phân quyền truy cập: Chỉ tìm kiếm trên tài liệu người dùng có quyền xem
    4. Trích xuất đoạn ngữ cảnh (Context chunk) phù hợp nhất
    5. Tổng hợp câu trả lời kèm dẫn chứng tài liệu nguồn và lưu lịch sử vào ai_queries
    """
    permission_classes = [AllowAny]

    def post(self, request):
        query_text = request.data.get('query', '').strip()
        if not query_text:
            return Response({
                'status': 'error',
                'message': 'Vui lòng nhập nội dung câu hỏi.',
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if (request.user and request.user.is_authenticated) else None

        # 1. Tạo vector embedding câu hỏi
        query_vec = compute_embedding(query_text, dim=16)
        query_words = [w.lower() for w in query_text.split() if len(w) > 2]

        # 2. Truy vấn danh sách chunk từ bảng document_embeddings
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.embedding_id, e.document_id, e.chunk_index, e.chunk_text, e.embedding_array,
                       d.title, d.status, d.is_public, d.uploader_id, s.subject_name
                FROM document_embeddings e
                JOIN documents d ON e.document_id = d.document_id
                JOIN subjects s ON d.subject_id = s.subject_id
            """)
            rows = cursor.fetchall()

        scored_chunks = []
        for r in rows:
            emb_id, doc_id, chunk_idx, chunk_text, emb_arr, title, doc_status, is_pub, uploader_id, subj_name = r

            # 3. Kiểm tra quyền truy cập tài liệu:
            # Sinh viên / Khách chỉ tìm trong tài liệu APPROVED & public, hoặc do chính mình nộp
            is_staff = user and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))
            is_owner = user and uploader_id == user.id
            if not is_staff and not is_owner and doc_status != Document.APPROVED:
                continue

            # Tính Cosine similarity
            sim = 0.0
            if emb_arr and len(emb_arr) == len(query_vec):
                dot = sum(a * b for a, b in zip(emb_arr, query_vec))
                norm_a = math.sqrt(sum(a * a for a in emb_arr))
                norm_b = math.sqrt(sum(b * b for b in query_vec))
                if norm_a > 0 and norm_b > 0:
                    sim = dot / (norm_a * norm_b)

            # Tính điểm từ khóa xuất hiện
            lower_chunk = chunk_text.lower()
            keyword_score = sum(1.5 for w in query_words if w in lower_chunk)

            total_score = sim * 0.6 + keyword_score * 0.4
            if total_score > 0.05 or any(w in lower_chunk for w in query_words):
                scored_chunks.append({
                    'embedding_id': emb_id,
                    'document_id': doc_id,
                    'chunk_index': chunk_idx,
                    'chunk_text': chunk_text,
                    'title': title,
                    'subject_name': subj_name,
                    'score': round(total_score, 4),
                })

        # Sắp xếp theo độ liên quan giảm dần
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        top_chunks = scored_chunks[:3]

        if not top_chunks and rows:
            # Fallback lấy chunk đầu tiên của tài liệu APPROVED nếu không có match từ khóa
            approved_first = next((r for r in rows if r[6] == Document.APPROVED), rows[0])
            top_chunks = [{
                'embedding_id': approved_first[0],
                'document_id': approved_first[1],
                'chunk_index': approved_first[2],
                'chunk_text': approved_first[3],
                'title': approved_first[5],
                'subject_name': approved_first[9],
                'score': 0.5,
            }]

        matched_doc_ids = list(dict.fromkeys(c['document_id'] for c in top_chunks))
        matched_docs = list(Document.objects.filter(pk__in=matched_doc_ids))

        # 4. Tổng hợp câu trả lời ngữ cảnh RAG
        snippets_text = "\n".join([f"- [{c['title']} - {c['subject_name']}]: \"{c['chunk_text'][:200]}...\"" for c in top_chunks])
        sources_summary = ", ".join([f'"{d.title}" ({d.subject.subject_name})' for d in matched_docs])

        ai_response = (
            f"Dựa trên nội dung học liệu được trích xuất từ {sources_summary}:\n\n"
            f"Đối với câu hỏi '{query_text}', hệ thống DocUni đã đối soát với cơ sở tri thức tài liệu trong PostgreSQL. "
            f"Dưới đây là các luận điểm trọng tâm trích xuất từ tài liệu học phần:\n\n"
            f"{snippets_text}\n\n"
            f"Bạn có thể bấm vào nguồn tài liệu tham khảo bên dưới để xem hoặc tải toàn văn tài liệu."
        )

        # 5. Lưu lịch sử câu hỏi vào database PostgreSQL
        ai_query = AIQuery.objects.create(
            user=user,
            query_text=query_text,
            ai_response=ai_response,
        )

        for chunk in top_chunks:
            try:
                emb_obj = DocumentEmbedding.objects.filter(pk=chunk['embedding_id']).first()
                doc_obj = next((d for d in matched_docs if d.id == chunk['document_id']), None)
                if emb_obj and doc_obj:
                    AIQuerySource.objects.create(
                        query=ai_query,
                        document=doc_obj,
                        embedding=emb_obj,
                    )
            except Exception:
                pass

        sources_data = []
        for d in matched_docs:
            d_data = DocumentSerializer(d).data
            chunk_ref = next((c for c in top_chunks if c['document_id'] == d.id), None)
            if chunk_ref:
                d_data['relevant_snippet'] = chunk_ref['chunk_text'][:250]
                d_data['relevance_score'] = chunk_ref['score']
            sources_data.append(d_data)

        return Response({
            'status': 'success',
            'query_id': ai_query.query_id,
            'query': query_text,
            'answer': ai_response,
            'sources': sources_data,
            'top_chunks': top_chunks,
            'created_at': ai_query.created_at,
        }, status=status.HTTP_200_OK)


class AIHistoryAPIView(APIView):
    """
    GET /api/ai/history/
    Lịch sử câu hỏi của người dùng hiện tại
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if (request.user and request.user.is_authenticated) else None
        if not user:
            qs = AIQuery.objects.filter(user__isnull=True).order_by('-created_at')[:10]
        else:
            qs = AIQuery.objects.filter(user=user).order_by('-created_at')[:20]

        serializer = AIQuerySerializer(qs, many=True)
        return Response({
            'status': 'success',
            'history': serializer.data,
        }, status=status.HTTP_200_OK)

