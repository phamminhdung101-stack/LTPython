"""
DocUni - AI Search & RAG API Views
Tập trung toàn bộ các endpoint REST API phục vụ:
1. POST /api/ai/chat/ & POST /api/ai/query/ (Hỏi đáp ngữ cảnh học tập RAG)
2. GET  /api/ai/history/ (Lịch sử hỏi đáp)
3. GET  /api/ai/history/<int:query_id>/ (Chi tiết một câu hỏi và nguồn trích dẫn)
4. POST /api/ai/documents/<int:pk>/process/ (Lập chỉ mục và nạp vector tài liệu)
5. GET  /api/ai/documents/<int:pk>/status/ (Trạng thái embedding tài liệu)
6. POST /api/ai/documents/<int:pk>/summary/ (Tóm tắt tài liệu bằng AI)
7. POST /api/ai/documents/<int:pk>/suggest-tags/ (Đề xuất nhãn tài liệu)
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import connection

from .models import AIQuery, AIQuerySource, DocumentEmbedding
from .serializers import AIQuerySerializer
from documents.models import Document
from documents.serializers import DocumentSerializer
from .services import (
    RAGService,
    SummaryService,
    TagSuggestionService,
    VectorSearchService,
    EmbeddingService,
)


class AIChatAPIView(APIView):
    """
    POST /api/ai/chat/ hoặc POST /api/ai/query/
    Endpoint hỏi đáp thông minh RAG:
    Nhận:
    {
        "query": "Hệ quản trị cơ sở dữ liệu là gì?",
        "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
        "subject_id": 1,   // (Tùy chọn) giới hạn theo môn học
        "document_id": 5   // (Tùy chọn) giới hạn theo tài liệu
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        query_text = request.data.get('query', '') or request.data.get('message', '')
        query_text = str(query_text).strip()
        if not query_text:
            return Response({
                'status': 'error',
                'message': 'Vui lòng cung cấp nội dung câu hỏi (tham số "query").',
            }, status=status.HTTP_400_BAD_REQUEST)

        history = request.data.get('history', [])
        subject_id = request.data.get('subject_id')
        document_id = request.data.get('document_id')
        top_k = int(request.data.get('top_k', 4))

        user = request.user if (request.user and request.user.is_authenticated) else None

        result = RAGService.query(
            query_text=query_text,
            user=user,
            conversation_history=history,
            subject_id=subject_id,
            document_id=document_id,
            top_k=top_k
        )

        return Response(result, status=status.HTTP_200_OK)


# Giữ alias AIQueryAPIView để bảo toàn tính tương thích ngược 100% với các client cũ
AIQueryAPIView = AIChatAPIView


class AIHistoryListAPIView(APIView):
    """
    GET /api/ai/history/
    Lấy danh sách các câu hỏi gần đây của người dùng hiện tại (hoặc người dùng ẩn danh).
    Quản trị viên (ADMIN) có thể xem toàn bộ lịch sử nếu truyền ?all=true.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if (request.user and request.user.is_authenticated) else None
        show_all = request.query_params.get('all', 'false').lower() == 'true'

        if user and (getattr(user, 'is_admin', False) or (user.role and user.role.role_name == 'ADMIN')) and show_all:
            qs = AIQuery.objects.all().order_by('-created_at')[:50]
        elif user:
            qs = AIQuery.objects.filter(user=user).order_by('-created_at')[:30]
        else:
            qs = AIQuery.objects.filter(user__isnull=True).order_by('-created_at')[:15]

        serializer = AIQuerySerializer(qs, many=True)
        return Response({
            'status': 'success',
            'count': qs.count(),
            'history': serializer.data,
        }, status=status.HTTP_200_OK)


# Giữ alias AIHistoryAPIView
AIHistoryAPIView = AIHistoryListAPIView


class AIHistoryDetailAPIView(APIView):
    """
    GET /api/ai/history/<int:query_id>/
    Chi tiết một phiên hỏi đáp kèm danh sách tài liệu và chunk nguồn đã được sử dụng.
    """
    permission_classes = [AllowAny]

    def get(self, request, query_id):
        user = request.user if (request.user and request.user.is_authenticated) else None
        ai_query = AIQuery.objects.filter(pk=query_id).first()
        if not ai_query:
            return Response({'status': 'error', 'message': 'Không tìm thấy câu hỏi.'}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra quyền: Người dùng chỉ được xem câu hỏi của chính mình (trừ Admin)
        if ai_query.user and user != ai_query.user and not getattr(user, 'is_admin', False):
            return Response({'status': 'error', 'message': 'Bạn không có quyền xem câu hỏi này.'}, status=status.HTTP_403_FORBIDDEN)

        # Lấy danh sách nguồn từ ai_query_sources
        sources_qs = AIQuerySource.objects.filter(query=ai_query).select_related('document', 'embedding')
        sources_data = []
        for s in sources_qs:
            doc = s.document
            emb = s.embedding
            sources_data.append({
                'document_id': doc.id if doc else None,
                'title': doc.title if doc else 'Tài liệu',
                'subject_name': doc.subject.subject_name if (doc and doc.subject) else 'Chung',
                'embedding_id': emb.embedding_id if emb else None,
                'chunk_index': emb.chunk_index if emb else 0,
                'snippet': (emb.chunk_text[:250] + '...') if emb else '',
            })

        data = {
            'query_id': ai_query.query_id,
            'query_text': ai_query.query_text,
            'ai_response': ai_query.ai_response,
            'created_at': ai_query.created_at,
            'user_id': ai_query.user_id,
            'sources': sources_data,
        }
        return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)


class AIDocumentProcessAPIView(APIView):
    """
    POST /api/ai/documents/<int:pk>/process/
    Kích hoạt quy trình trích xuất văn bản, chunking và embedding vector cho một tài liệu.
    """
    permission_classes = [AllowAny]

    def post(self, request, pk):
        doc = Document.objects.filter(pk=pk).first()
        if not doc:
            return Response({'status': 'error', 'message': 'Không tìm thấy tài liệu.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user if (request.user and request.user.is_authenticated) else None
        res = RAGService.process_and_index_document(doc, user=user)
        return Response(res, status=status.HTTP_200_OK)


class AIDocumentStatusAPIView(APIView):
    """
    GET /api/ai/documents/<int:pk>/status/
    Kiểm tra trạng thái embedding / indexing của tài liệu trong PostgreSQL.
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        doc = Document.objects.filter(pk=pk).first()
        if not doc:
            return Response({'status': 'error', 'message': 'Không tìm thấy tài liệu.'}, status=status.HTTP_404_NOT_FOUND)

        chunks_count = DocumentEmbedding.objects.filter(document=doc).count()
        latest_chunk = DocumentEmbedding.objects.filter(document=doc).order_by('-created_at').first()

        return Response({
            'status': 'success',
            'document_id': doc.id,
            'title': doc.title,
            'is_indexed': chunks_count > 0,
            'chunks_count': chunks_count,
            'last_indexed_at': latest_chunk.created_at if latest_chunk else None,
        }, status=status.HTTP_200_OK)


class AIDocumentSummaryAPIView(APIView):
    """
    POST /api/ai/documents/<int:pk>/summary/
    Tóm tắt nội dung tài liệu bằng AI.
    """
    permission_classes = [AllowAny]

    def post(self, request, pk):
        user = request.user if (request.user and request.user.is_authenticated) else None
        res = SummaryService.summarize_document(document_id=pk, user=user)
        if res.get('status') == 'error':
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        return Response(res, status=status.HTTP_200_OK)


class AIDocumentSuggestTagsAPIView(APIView):
    """
    POST /api/ai/documents/<int:pk>/suggest-tags/
    Phân tích nội dung và đề xuất thẻ (tags) thông minh cho tài liệu.
    """
    permission_classes = [AllowAny]

    def post(self, request, pk):
        res = TagSuggestionService.suggest_tags(document_id=pk)
        if res.get('status') == 'error':
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        return Response(res, status=status.HTTP_200_OK)
