import json
import os
from datetime import datetime
from pathlib import Path

from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from django.core.exceptions import SuspiciousFileOperation
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny

from academics.models import Subject
from .models import Document, DocumentVersion, Tag, Folder, DocumentActivityLog
from .serializers import DocumentSerializer, DocumentCreateSerializer, DocumentVersionSerializer
from .storage_service import LocalDocumentStorageService
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
    Sinh viên / Giảng viên đóng góp tài liệu mới (hỗ trợ cả JSON metadata và multipart/form-data upload file).
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = Document.objects.select_related(
            'subject', 'subject__department', 'folder', 'uploader', 'approved_by'
        ).prefetch_related('tags', 'versions').order_by('-created_at')

        user = request.user if (request.user and request.user.is_authenticated) else None

        # Phân quyền hiển thị danh sách
        if not user:
            qs = qs.filter(status=Document.APPROVED, is_public=True)
        elif user.is_admin:
            pass  # Admin xem tất cả
        elif user.is_lecturer:
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
        if subject_id and str(subject_id).isdigit():
            qs = qs.filter(subject_id=int(subject_id))
        if dept_id and str(dept_id).isdigit():
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

        # Nếu có file đính kèm dạng multipart, chuyển tiếp sang logic upload tệp
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            return DocumentUploadAPIView().post(request)

        # Xử lý tạo metadata tài liệu dạng JSON
        serializer = DocumentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        doc = serializer.save(
            uploader=request.user,
            status=Document.PENDING,
        )

        file_path = request.data.get('file_path', '')
        if file_path:
            meta = {
                'file_name': os.path.basename(file_path),
                'original_file_name': os.path.basename(file_path),
                'file_type': os.path.splitext(file_path)[1].lstrip('.').upper() or 'DOCUMENT',
                'file_size': int(request.data.get('file_size', 0)),
                'mime_type': 'application/octet-stream',
                'object_key': file_path,
                'storage_provider': 'LOCAL',
                'uploader_id': request.user.user_id,
                'subject_id': doc.subject_id,
                'class_id': getattr(request.user, 'class_id', None),
                'department_id': getattr(doc.subject, 'department_id', None) or getattr(request.user, 'department_id', None),
                'upload_date': datetime.now().isoformat(),
                'document_status': Document.PENDING,
                'description': doc.description or '',
            }
            DocumentVersion.objects.create(
                document=doc,
                file_path=file_path,
                version_number=1,
                updated_by=request.user,
                change_summary=json.dumps(meta, ensure_ascii=False),
            )

        DocumentActivityLog.objects.create(
            document=doc,
            user=request.user,
            action='CREATE',
            description=f"Tạo thông tin tài liệu: {doc.title}",
        )

        return Response({
            'status': 'success',
            'message': 'Đóng góp tài liệu thành công! Tài liệu đang ở trạng thái chờ duyệt (PENDING).',
            'document': DocumentSerializer(doc).data,
        }, status=status.HTTP_201_CREATED)


class DocumentUploadAPIView(APIView):
    """
    POST /api/documents/upload/
    Upload tài liệu thực tế lưu vào thư mục media/documents/YYYY/MM/.
    Kiểm tra MIME type, magic bytes, định dạng whitelist và giới hạn dung lượng.
    Lưu metadata vào PostgreSQL với trạng thái PENDING mặc định.
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not (request.user and request.user.is_authenticated):
            return Response({
                'status': 'error',
                'message': 'Vui lòng đăng nhập để tải lên tài liệu.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({
                'status': 'error',
                'message': 'Vui lòng chọn tệp tài liệu để tải lên.',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Lấy thông tin đầu vào
        subject_id = request.data.get('subject_id')
        if not subject_id:
            return Response({
                'status': 'error',
                'message': 'Thông tin môn học (subject_id) là bắt buộc.',
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            subject = Subject.objects.select_related('department').get(pk=int(subject_id))
        except (Subject.DoesNotExist, ValueError):
            return Response({
                'status': 'error',
                'message': f'Môn học với ID {subject_id} không tồn tại.',
            }, status=status.HTTP_404_NOT_FOUND)

        title = request.data.get('title', '').strip() or uploaded_file.name
        description = request.data.get('description', '').strip()
        folder_id = request.data.get('folder_id')
        is_public_raw = request.data.get('is_public', False)
        is_public = str(is_public_raw).lower() in ('true', '1', 'yes')

        # 1. Lưu file vào FileSystemStorage cục bộ
        storage_service = LocalDocumentStorageService()
        try:
            file_meta = storage_service.save_document_file(uploaded_file)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

        object_key = file_meta['object_key']

        # 2. Lưu Metadata vào PostgreSQL trong Database Transaction
        try:
            with transaction.atomic():
                doc = Document.objects.create(
                    title=title,
                    description=description,
                    subject=subject,
                    folder_id=int(folder_id) if folder_id and str(folder_id).isdigit() else None,
                    uploader=request.user,
                    status=Document.PENDING,  # Mặc định tài liệu mới upload có trạng thái PENDING
                    is_public=is_public,
                )

                # Bổ sung thông tin metadata chi tiết
                dept_id = getattr(subject, 'department_id', None) or getattr(request.user, 'department_id', None)
                cls_id = getattr(request.user, 'class_id', None)
                if request.data.get('class_id') and str(request.data.get('class_id')).isdigit():
                    cls_id = int(request.data.get('class_id'))
                if request.data.get('department_id') and str(request.data.get('department_id')).isdigit():
                    dept_id = int(request.data.get('department_id'))

                full_meta = {
                    'document_id': doc.document_id,
                    'file_name': file_meta['file_name'],
                    'original_file_name': file_meta['original_file_name'],
                    'file_type': file_meta['file_type'],
                    'file_size': file_meta['file_size'],
                    'mime_type': file_meta['mime_type'],
                    'object_key': object_key,
                    'storage_provider': 'LOCAL',
                    'uploader_id': request.user.user_id,
                    'subject_id': subject.subject_id,
                    'class_id': cls_id,
                    'department_id': dept_id,
                    'upload_date': file_meta['upload_date'],
                    'document_status': Document.PENDING,
                    'description': description,
                }

                DocumentVersion.objects.create(
                    document=doc,
                    file_path=object_key,
                    version_number=1,
                    updated_by=request.user,
                    change_summary=json.dumps(full_meta, ensure_ascii=False),
                )

                # Ghi log hoạt động
                DocumentActivityLog.objects.create(
                    document=doc,
                    user=request.user,
                    action='CREATE',
                    description=f"Tải lên tài liệu mới: {title} (File: {file_meta['original_file_name']}, Khóa: {object_key})",
                )

            return Response({
                'status': 'success',
                'message': 'Tải lên tài liệu thành công. Tài liệu đang ở trạng thái chờ duyệt (PENDING).',
                'document': DocumentSerializer(doc).data,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Đồng bộ dữ liệu: Nếu lưu metadata vào PostgreSQL thất bại, phải xóa file vừa upload
            storage_service.delete_document_file(object_key)
            return Response({
                'status': 'error',
                'message': f'Lưu thông tin tài liệu thất bại: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentDetailAPIView(APIView):
    """
    GET /api/documents/<pk>/
    DELETE /api/documents/<pk>/
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            doc = Document.objects.select_related(
                'subject', 'subject__department', 'folder', 'uploader', 'approved_by'
            ).prefetch_related('tags', 'versions').get(pk=pk)
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
            return Response({
                'status': 'error',
                'message': 'Vui lòng đăng nhập để thực hiện thao tác xóa.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({'status': 'error', 'message': 'Không tìm thấy tài liệu.'}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra quyền xóa: Chỉ Admin hoặc người đã upload tài liệu mới được xóa
        if not (request.user.is_admin or doc.uploader_id == request.user.user_id):
            return Response({
                'status': 'error',
                'message': 'Bạn không có quyền xóa tài liệu này.',
            }, status=status.HTTP_403_FORBIDDEN)

        storage_service = LocalDocumentStorageService()
        object_keys_to_delete = [
            v.file_path for v in doc.versions.all() if v.file_path and not v.file_path.startswith('/storage/')
        ]

        # Xóa metadata trong PostgreSQL
        with transaction.atomic():
            doc_title = doc.title
            doc.delete()

        # Xóa các file vật lý thực tế trong media/ sau khi xóa DB thành công
        for key in object_keys_to_delete:
            storage_service.delete_document_file(key)

        return Response({
            'status': 'success',
            'message': f'Đã xóa tài liệu "{doc_title}" và tệp lưu trữ thành công.',
        }, status=status.HTTP_200_OK)


class DocumentDownloadAPIView(APIView):
    """
    GET /api/documents/<pk>/download/
    POST /api/documents/<pk>/download/
    Tải file tài liệu thực tế từ media/ có kiểm tra JWT / Authentication và phân quyền.
    """
    permission_classes = [AllowAny]

    def _handle_download(self, request, pk):
        user = request.user if (request.user and request.user.is_authenticated) else None

        # 1. Kiểm tra xác thực (Bắt buộc phải đăng nhập hoặc gửi token)
        if not user:
            return Response({
                'status': 'error',
                'message': 'Vui lòng đăng nhập hoặc cung cấp JWT token hợp lệ để tải tài liệu.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 2. Truy vấn tài liệu
        try:
            doc = Document.objects.select_related('subject', 'uploader').get(pk=pk)
        except Document.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Tài liệu không tồn tại trên hệ thống.',
            }, status=status.HTTP_404_NOT_FOUND)

        # 3. Kiểm tra trạng thái và quyền Download
        # - Tài liệu đã APPROVED: Người dùng có quyền truy cập được phép tải.
        # - Tài liệu chưa APPROVED (PENDING hoặc REJECTED): Chỉ Admin, Giảng viên hoặc chính người upload mới được phép tải.
        if doc.status != Document.APPROVED:
            is_uploader = (doc.uploader_id == user.user_id)
            is_staff = user.is_admin or user.is_lecturer
            if not (is_uploader or is_staff):
                return Response({
                    'status': 'error',
                    'message': 'Tài liệu chưa được phê duyệt. Bạn không có quyền tải xuống tài liệu này.',
                }, status=status.HTTP_403_FORBIDDEN)

        # 4. Lấy object_key từ version mới nhất
        object_key = doc.object_key
        if not object_key:
            return Response({
                'status': 'error',
                'message': 'Tài liệu không có tệp đính kèm.',
            }, status=status.HTTP_404_NOT_FOUND)

        # 5. Xác định file thực tế trong media/ và Chống Path Traversal
        storage_service = LocalDocumentStorageService()
        try:
            abs_path = storage_service.get_absolute_path(object_key)
        except SuspiciousFileOperation:
            return Response({
                'status': 'error',
                'message': 'Đường dẫn tệp tin không an toàn hoặc không hợp lệ.',
            }, status=status.HTTP_400_BAD_REQUEST)

        if not abs_path or not abs_path.exists() or not abs_path.is_file():
            return Response({
                'status': 'error',
                'message': 'Tệp tin không tồn tại trên hệ thống lưu trữ.',
            }, status=status.HTTP_404_NOT_FOUND)

        # 6. Ghi nhận lượt tải và nhật ký hoạt động
        Document.objects.filter(pk=pk).update(download_count=doc.download_count + 1)
        DocumentActivityLog.objects.create(
            document=doc,
            user=user,
            action='DOWNLOAD',
            description=f"Tải xuống tài liệu: {doc.title} (File: {doc.original_file_name or doc.file_name})",
        )

        # 7. Trả file về client
        filename_for_download = doc.original_file_name or doc.file_name or abs_path.name
        mime_type = doc.mime_type or 'application/octet-stream'

        response = FileResponse(open(abs_path, 'rb'), content_type=mime_type, as_attachment=True, filename=filename_for_download)
        return response

    def get(self, request, pk):
        return self._handle_download(request, pk)

    def post(self, request, pk):
        return self._handle_download(request, pk)


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

        DocumentActivityLog.objects.create(
            document=doc,
            user=request.user,
            action='APPROVE',
            description=f"Phê duyệt tài liệu: {doc.title}",
        )

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

        DocumentActivityLog.objects.create(
            document=doc,
            user=request.user,
            action='REJECT',
            description=f"Từ chối tài liệu: {doc.title}. Lý do: {reason}",
        )

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
        qs = Document.objects.filter(status=Document.PENDING).select_related(
            'subject', 'uploader'
        ).prefetch_related('versions').order_by('-created_at')

        if not request.user.is_admin and request.user.department_id:
            qs = qs.filter(subject__department_id=request.user.department_id)

        serializer = DocumentSerializer(qs, many=True)
        return Response({
            'status': 'success',
            'total': qs.count(),
            'pending_documents': serializer.data,
        }, status=status.HTTP_200_OK)
