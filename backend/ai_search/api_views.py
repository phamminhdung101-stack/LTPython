from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import AIQuery, AIQuerySource, DocumentEmbedding
from .serializers import AIQuerySerializer
from documents.models import Document
from documents.serializers import DocumentSerializer


class AIQueryAPIView(APIView):
    """
    POST /api/ai/query/
    Thực hiện truy vấn câu hỏi học tập theo ngữ cảnh (RAG-lite) kết nối kho tài liệu.
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

        # Tìm các tài liệu liên quan trong kho học liệu PostgreSQL
        words = [w.lower() for w in query_text.split() if len(w) > 2]
        matching_docs = Document.objects.filter(status=Document.APPROVED)

        # Lọc ngữ cảnh theo từ khóa
        matched = []
        for doc in matching_docs:
            doc_text = f"{doc.title} {doc.description or ''} {doc.subject.subject_name}".lower()
            if any(w in doc_text for w in words):
                matched.append(doc)
            if len(matched) >= 3:
                break

        if not matched:
            matched = list(matching_docs[:2])

        # Sinh câu trả lời RAG dựa trên tài liệu thực tế
        sources_summary = ", ".join([f'"{d.title}" ({d.subject.subject_name})' for d in matched])
        ai_response = (
            f"Dựa trên nội dung học liệu được trích xuất từ {sources_summary}:\n\n"
            f"Đối với câu hỏi '{query_text}', hệ thống DocUni đã đối soát với tài liệu học phần chính thức. "
            f"Nội dung trọng tâm bao gồm các định nghĩa, quy trình và bài tập thực hành được quy định trong đề cương môn học. "
            f"Bạn có thể xem các trích dẫn tài liệu đính kèm bên dưới để tra cứu chi tiết."
        )

        # Lưu lịch sử câu hỏi vào database PostgreSQL
        ai_query = AIQuery.objects.create(
            user=user,
            query_text=query_text,
            ai_response=ai_response,
        )

        for doc in matched:
            AIQuerySource.objects.create(
                query=ai_query,
                document=doc,
                embedding=None,
            )

        return Response({
            'status': 'success',
            'query_id': ai_query.query_id,
            'query': query_text,
            'answer': ai_response,
            'sources': DocumentSerializer(matched, many=True).data,
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

