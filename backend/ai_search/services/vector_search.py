"""
DocUni - Vector Search Service
Tìm kiếm tương đồng ngữ nghĩa (Semantic Vector Search) kết hợp Full-Text Keyword Search (Hybrid Retrieval)
trên cơ sở dữ liệu PostgreSQL.
Tích hợp phân quyền truy cập đa cấp (RBAC & Document Permissions ACL) cho ADMIN, LECTURER, STUDENT và GUEST.
"""

import math
from typing import List, Dict, Any, Optional
from django.db import connection
from documents.models import Document
from accounts.models import User
from permissions.services import can_user_access_document


class VectorSearchService:
    """Dịch vụ tìm kiếm vector ngữ nghĩa với bộ lọc phân quyền nghiêm ngặt."""

    DEFAULT_TOP_K = 4
    DEFAULT_THRESHOLD = 0.12

    @classmethod
    def search(
        cls,
        query_text: str,
        query_vector: List[float],
        user: Optional[User] = None,
        subject_id: Optional[int] = None,
        document_id: Optional[int] = None,
        top_k: int = DEFAULT_TOP_K,
        threshold: float = DEFAULT_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Thực hiện tìm kiếm ngữ cảnh:
        1. Lọc tài liệu theo quyền truy cập của người dùng
        2. Tính Cosine Similarity và Keyword Relevance trên PostgreSQL
        3. Áp dụng ngưỡng liên quan (similarity threshold)
        4. Trả về top K đoạn văn bản (chunks) phù hợp nhất
        """
        query_words = [w.lower() for w in query_text.split() if len(w) > 2]

        # 1. Truy vấn các chunk embedding từ PostgreSQL kèm metadata tài liệu
        sql = """
            SELECT 
                e.embedding_id,
                e.document_id,
                e.chunk_index,
                e.chunk_text,
                e.embedding_array,
                d.title,
                d.status,
                d.is_public,
                d.uploader_id,
                d.subject_id,
                s.subject_name,
                dep.department_id,
                dep.department_name
            FROM document_embeddings e
            JOIN documents d ON e.document_id = d.document_id
            LEFT JOIN subjects s ON d.subject_id = s.subject_id
            LEFT JOIN departments dep ON s.department_id = dep.department_id
            WHERE 1=1
        """
        params = []
        if subject_id:
            sql += " AND d.subject_id = %s"
            params.append(subject_id)
        if document_id:
            sql += " AND d.document_id = %s"
            params.append(document_id)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        if not rows:
            return []

        # 2. Đánh giá quyền truy cập và tính điểm từng chunk
        scored_chunks = []
        for r in rows:
            (emb_id, doc_id, chunk_idx, chunk_text, emb_arr,
             title, doc_status, is_pub, uploader_id, subj_id,
             subj_name, dep_id, dep_name) = r

            # A. Kiểm tra phân quyền truy cập (RBAC / ACL)
            has_access = cls._check_access(
                user=user,
                doc_id=doc_id,
                uploader_id=uploader_id,
                doc_status=doc_status,
                is_public=is_pub,
                dep_id=dep_id
            )
            if not has_access:
                continue

            # B. Tính Cosine Similarity giữa query_vector và emb_arr
            sim = 0.0
            if emb_arr and query_vector and len(emb_arr) == len(query_vector):
                dot = sum(a * b for a, b in zip(emb_arr, query_vector))
                norm_a = math.sqrt(sum(a * a for a in emb_arr))
                norm_b = math.sqrt(sum(b * b for b in query_vector))
                if norm_a > 0 and norm_b > 0:
                    sim = max(0.0, dot / (norm_a * norm_b))

            # C. Tính điểm khớp từ khóa (Keyword matching)
            lower_chunk = chunk_text.lower()
            keyword_hits = sum(1.5 for w in query_words if w in lower_chunk)
            if any(w in title.lower() for w in query_words):
                keyword_hits += 2.0

            # Điểm tổng hợp Hybrid (60% Vector Cosine + 40% Keyword)
            combined_score = (sim * 0.60) + min(1.0, (keyword_hits * 0.15)) * 0.40

            # Lọc theo ngưỡng liên quan
            if combined_score >= threshold or (keyword_hits > 0 and sim > 0.05):
                # Ước lượng số trang từ chunk_index
                page_estimate = max(1, (chunk_idx // 3) + 1)

                scored_chunks.append({
                    'embedding_id': emb_id,
                    'document_id': doc_id,
                    'chunk_index': chunk_idx,
                    'chunk_text': chunk_text,
                    'page_number': page_estimate,
                    'title': title,
                    'subject_name': subj_name or 'Chung',
                    'department_name': dep_name or '',
                    'similarity_score': round(sim, 4),
                    'relevance_score': round(min(1.0, combined_score), 4),
                    'relevance_percentage': int(round(min(1.0, combined_score) * 100)),
                })

        # Sắp xếp theo độ liên quan giảm dần
        scored_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)

        return scored_chunks[:top_k]

    @classmethod
    def _check_access(
        cls,
        user: Optional[User],
        doc_id: int,
        uploader_id: int,
        doc_status: str,
        is_public: bool,
        dep_id: Optional[int]
    ) -> bool:
        """Kiểm tra quyền xem tài liệu của user."""
        # 1. Khách vãng lai (chưa đăng nhập) -> chỉ xem tài liệu APPROVED và Public
        if not user or not user.is_authenticated:
            return (doc_status == Document.APPROVED and is_public)

        # 2. Quản trị viên (ADMIN) -> có toàn quyền xem tất cả tài liệu
        if getattr(user, 'is_admin', False) or (user.role and user.role.role_name == 'ADMIN'):
            return True

        # 3. Người tải lên (Uploader) -> luôn xem được tài liệu của chính mình
        if uploader_id == user.id:
            return True

        # 4. Tài liệu chưa duyệt (PENDING, REJECTED) -> chỉ uploader hoặc admin thấy
        if doc_status != Document.APPROVED:
            return False

        # 5. Tài liệu công khai (Public) đã được duyệt -> mọi tài khoản đăng nhập đều xem được
        if is_public:
            return True

        # 6. Giảng viên (LECTURER) -> xem được tài liệu cùng khoa / bộ môn
        if getattr(user, 'is_lecturer', False):
            if user.department_id and dep_id and user.department_id == dep_id:
                return True

        # 7. Kiểm tra phân quyền chi tiết trong bảng document_permissions
        try:
            doc_obj = Document.objects.filter(pk=doc_id).first()
            if doc_obj:
                return can_user_access_document(user, doc_obj)
        except Exception:
            pass

        return False
