from datetime import datetime
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Document, DocumentVersion, Tag, Folder
from .serializers import DocumentSerializer, DocumentCreateSerializer, DocumentVersionSerializer
from permissions.rest_permissions import (
    IsAuthenticatedCustom,
    IsLecturerOrAdmin,
    IsOwnerOrAdmin,
)


class DocumentListCreateAPIView(APIView):
    """
    GET /api/documents/
    Lấy danh sách học liệu có phân quyền:
    - Khách vãng lai: chỉ xem tài liệu công khai (is_public=True) đã duyệt (status='APPROVED').
    - Sinh viên: xem tài liệu công khai + tài liệu theo khoa/lớp + tài liệu do mình đóng góp.
    - Giảng viên / Admin: xem toàn bộ tài liệu trong khoa / hệ thống.
    
    POST /api/documents/
    Sinh viên / Giảng viên đóng góp tài liệu mới.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Document.objects.select_related('subject', 'subject__department', 'folder', 'uploader', 'approved_by').prefetch_related('tags').order_by('-created_at')

        user = request.user if (request.user and request.user.is_authenticated) else None

        # Phân quyền hiển thị danh sách
        if not user:
            qs = qs.filter(status=Document.APPROVED, is_public=True)
        elif user.is_admin:
            pass  # Admin xem tất cả
        elif user.is_lecturer:
            # Giảng viên xem tài liệu đã duyệt, công khai, hoặc tài liệu khoa mình phụ trách
            if user.department_id:
                qs = qs.filter(
                    Q(status=Document.APPROVED) |
                    Q(subject__department_id=user.department_id) |
                    Q(uploader_id=user.user_id)
                )
            else:
                qs = qs.filter(Q(status=Document.APPROVED) | Q(uploader_id=user.user_id))
        else:
            # Sinh viên
            qs = qs.filter(
                Q(status=Document.APPROVED, is_public=True) |
                Q(uploader_id=user.user_id) |
                (Q(status=Document.APPROVED, subject__department_id=user.department_id) if user.department_id else Q())
            )

        # Bộ lọc tìm kiếm
        q = request.GET.get('q', '').strip()
        subject_id = request.GET.get('subject_id')
        dept_id = request.GET.get('department_id')
        doc_status = request.GET.get('status')

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(subject__subject_name__icontains=q)
            )
        if subject_id and subject_id.isdigit():
            qs = qs.filter(subject_id=int(subject_id))
        if dept_id and dept_id.isdigit():
            qs = qs.filter(subject__department_id=int(dept_id))
        if doc_status and doc_status != 'ALL':
            qs = qs.filter(status=doc_status)

        serializer = DocumentSerializer(qs, many=True)
        return Response({
            'status': 'success',
            'total': qs.count(),
            'documents': serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not (request.user and request.user.is_authenticated):
            return Response({
                'status': 'error',
                'message': 'Vui lòng đăng nhập để đóng góp tài liệu.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = DocumentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Giảng viên tự upload có thể được duyệt ngay, sinh viên upload cần kiểm duyệt
        initial_status = Document.APPROVED if request.user.is_lecturer or request.user.is_admin else Document.PENDING

        doc = serializer.save(
            uploader=request.user,
            status=initial_status,
            approved_by=request.user if initial_status == Document.APPROVED else None,
            approved_at=datetime.now() if initial_status == Document.APPROVED else None,
        )

        # Tạo phiên bản ban đầu nếu có file đính kèm
        file_path = request.data.get('file_path', '')
        if file_path:
            DocumentVersion.objects.create(
                document=doc,
                file_path=file_path,
                version_number=1,
                updated_by=request.user,
                change_summary='Bản khởi tạo đầu tiên',
            )

        return Response({
            'status': 'success',
            'message': 'Đóng góp tài liệu thành công!' + (' Đang chờ giảng viên kiểm duyệt.' if initial_status == Document.PENDING else ''),
            'document': DocumentSerializer(doc).data,
        }, status=status.HTTP_201_CREATED)


class DocumentDetailAPIView(APIView):
    """
    GET /api/documents/<pk>/
    DELETE /api/documents/<pk>/
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            doc = Document.objects.select_related('subject', 'subject__department', 'folder', 'uploader', 'approved_by').prefetch_related('tags').get(pk=pk)
        except Document.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy tài liệu.'}, status=status.HTTP_404_NOT_FOUND)

        # Tăng lượt xem
        Document.objects.filter(pk=pk).update(view_count=doc.view_count + 1)
        doc.view_count += 1

        versions = doc.versions.all().order_by('-version_number')

        return Response({
            'status': 'success',
            'document': DocumentSerializer(doc).data,
            'versions': DocumentVersionSerializer(versions, many=True).data,
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        if not (request.user and request.user.is_authenticated):
            return Response({'status': 'error', 'message': 'Vui lòng đăng nhập.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy tài liệu.'}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ Admin hoặc người upload mới được xóa
        if not (request.user.is_admin or doc.uploader_id == request.user.user_id):
            return Response({'status': 'error', 'message': 'Bạn không có quyền xóa tài liệu này.'}, status=status.HTTP_403_FORBIDDEN)

        doc.delete()
        return Response({
            'status': 'success',
            'message': 'Đã xóa tài liệu thành công.',
        }, status=status.HTTP_200_OK)


class DocumentApproveAPIView(APIView):
    """
    POST /api/documents/<pk>/approve/
    Duyệt tài liệu (Giảng viên / Admin)
    """
    permission_classes = [IsLecturerOrAdmin]

    def post(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy tài liệu.'}, status=status.HTTP_404_NOT_FOUND)

        doc.status = Document.APPROVED
        doc.approved_by = request.user
        doc.approved_at = datetime.now()
        doc.save(update_fields=['status', 'approved_by', 'approved_at'])

        return Response({
            'status': 'success',
            'message': f'Đã phê duyệt tài liệu "{doc.title}" thành công.',
            'document': DocumentSerializer(doc).data,
        }, status=status.HTTP_200_OK)


class DocumentRejectAPIView(APIView):
    """
    POST /api/documents/<pk>/reject/
    Từ chối tài liệu (Giảng viên / Admin)
    """
    permission_classes = [IsLecturerOrAdmin]

    def post(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy tài liệu.'}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', 'Không đạt yêu cầu học phần.')
        doc.status = Document.REJECTED
        doc.save(update_fields=['status'])

        return Response({
            'status': 'success',
            'message': f'Đã từ chối tài liệu "{doc.title}". Lý do: {reason}',
            'document': DocumentSerializer(doc).data,
        }, status=status.HTTP_200_OK)


class DocumentPendingListAPIView(APIView):
    """
    GET /api/documents/pending/
    Hàng đợi duyệt tài liệu (Giảng viên / Admin)
    """
    permission_classes = [IsLecturerOrAdmin]

    def get(self, request):
        qs = Document.objects.filter(status=Document.PENDING).select_related('subject', 'uploader').order_by('-created_at')
        if not request.user.is_admin and request.user.department_id:
            qs = qs.filter(subject__department_id=request.user.department_id)

        serializer = DocumentSerializer(qs, many=True)
        return Response({
            'status': 'success',
            'total': qs.count(),
            'pending_documents': serializer.data,
        }, status=status.HTTP_200_OK)


class DocumentDownloadAPIView(APIView):
    """
    POST /api/documents/<pk>/download/
    Ghi nhận lượt tải xuống
    """
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy tài liệu.'}, status=status.HTTP_404_NOT_FOUND)

        Document.objects.filter(pk=pk).update(download_count=doc.download_count + 1)
        latest = doc.latest_version
        file_path = latest.file_path if latest else ''

        return Response({
            'status': 'success',
            'message': 'Bắt đầu tải xuống.',
            'download_count': doc.download_count + 1,
            'file_path': file_path,
        }, status=status.HTTP_200_OK)

