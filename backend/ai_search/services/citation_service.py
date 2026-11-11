"""
DocUni - Citation Service
Định dạng nguồn trích dẫn học liệu (Citations) cho câu trả lời RAG:
Hiển thị tên tài liệu, môn học, khoa, số trang/slide, đoạn văn bản trích dẫn (snippet), và điểm tương đồng %.
"""

from typing import List, Dict, Any


class CitationService:
    """Dịch vụ định dạng và tổng hợp nguồn trích dẫn cho câu trả lời."""

    @classmethod
    def format_citations(cls, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chuẩn hóa danh sách các trích dẫn nguồn từ danh sách chunks.
        """
        citations = []
        seen = set()

        for c in chunks:
            doc_id = c.get('document_id')
            chunk_idx = c.get('chunk_index', 0)
            key = (doc_id, chunk_idx)
            if key in seen:
                continue
            seen.add(key)

            chunk_text = c.get('chunk_text', '').strip()
            # Cắt ngắn snippet liên quan
            snippet = chunk_text[:280] + ("..." if len(chunk_text) > 280 else "")

            score = c.get('relevance_score', 0.5)
            pct = c.get('relevance_percentage')
            if pct is None:
                pct = int(round(score * 100))

            citations.append({
                'document_id': doc_id,
                'embedding_id': c.get('embedding_id'),
                'title': c.get('title', 'Tài liệu không tên'),
                'subject_name': c.get('subject_name', 'Chung'),
                'department_name': c.get('department_name', ''),
                'page_number': c.get('page_number', 1),
                'chunk_index': chunk_idx,
                'relevant_snippet': snippet,
                'similarity_score': c.get('similarity_score', score),
                'relevance_score': score,
                'relevance_percentage': pct,
            })

        return citations
