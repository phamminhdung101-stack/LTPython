"""
DocUni - REST API Endpoints Cho Quản Lý Tài Liệu & Cloudflare R2
Phần 2:
- POST /api/documents/upload/ : Tải lên tài liệu, upload R2, lưu metadata vào DB
- GET /api/documents/<id>/download/ : Tải file, kiểm tra ACL, sinh presigned URL R2
- DELETE /api/documents/<id>/ : Xóa file R2 & xóa bản ghi DB
- GET /api/documents/ : Danh sách tài liệu kèm bộ lọc
- GET /api/documents/<id>/ : Chi tiết tài liệu

Phần 3:
- POST /api/documents/<id>/approve/ : Duyệt tài liệu (Giảng viên / Admin)
- POST /api/documents/<id>/reject/ : Từ chối tài liệu kèm lý do
- POST /api/documents/<id>/versions/ : Nâng cấp phiên bản tài liệu (v2.0, v3.0...)
- GET /api/documents/<id>/versions/ : Danh sách lịch sử các phiên bản
- GET /api/documents/<id>/logs/ : Nhật ký kiểm toán hoạt động (Audit Activity Logs)
"""

import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from .models import Document, DocumentVersion, DocumentActivityLog, Folder, Tag
from academics.models import Subject
from .validators import validate_file_upload
from .r2_service import r2_service
from permissions.services import can_user_access_document, can_user_download_document


def _json_error(message: str, status: int = 400, errors=None) -> JsonResponse:
    payload = {'status': 'error', 'message': message}
    if errors:
        payload['errors'] = errors
    return JsonResponse(payload, status=status, json_dumps_params={'ensure_ascii': False})


def _json_ok(data=None, message: str = 'Thành công', status: int = 200) -> JsonResponse:
    payload = {'status': 'ok', 'message': message}
    if data is not None:
        payload['data'] = data
    return JsonResponse(payload, status=status, json_dumps_params={'ensure_ascii': False})


# ─── PHẦN 2: UPLOAD / DOWNLOAD / XÓA FILE ────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def upload_document_api(request):
    """
    API Tải lên tài liệu:
    - Kiểm tra định dạng (.pdf, .docx, .pptx, .xlsx, .zip)
    - Kiểm tra dung lượng (<= 50MB)
    - Tải file lên Cloudflare R2 bucket (hoặc local fallback)
    - Lưu metadata, SHA-256 và object key vào PostgreSQL
    - Ghi nhận nhật ký CREATE
    """
    user = request.user if request.user.is_authenticated else None

    # 1. Lấy và kiểm tra file
    file_obj = request.FILES.get('file')
    if not file_obj:
        return _json_error("Vui lòng đính kèm file tài liệu (tham số 'file').", 400)

    is_valid, err_msg, meta = validate_file_upload(file_obj)
    if not is_valid:
        return _json_error(err_msg, 400)

    # 2. Lấy các thông số metadata từ request
    title = request.POST.get('title', '').strip() or meta['filename']
    description = request.POST.get('description', '').strip()
    subject_id = request.POST.get('subject_id')
    folder_id = request.POST.get('folder_id')
    is_public = request.POST.get('is_public', 'false').lower() in ('true', '1', 'yes')

    if not subject_id:
        return _json_error("Môn học ('subject_id') là bắt buộc.", 400)

    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        return _json_error(f"Không tìm thấy môn học với ID = {subject_id}.", 404)

    folder = None
    if folder_id:
        try:
            folder = Folder.objects.get(pk=folder_id, subject=subject)
        except Folder.DoesNotExist:
            return _json_error(f"Thư mục ID = {folder_id} không tồn tại hoặc không thuộc môn học này.", 404)

    # Nếu người upload là Giảng viên hoặc Admin -> có thể duyệt trực tiếp, ngược lại mặc định PENDING
    status = Document.PENDING
    if user and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False)):
        # Giảng viên/Admin tải lên có thể tự công khai nếu muốn
        if is_public:
            status = Document.APPROVED

    with transaction.atomic():
        # 3. Tạo bản ghi Document trong PostgreSQL
        doc = Document.objects.create(
            title=title,
            description=description,
            subject=subject,
            folder=folder,
            uploader=user,
            status=status,
            is_public=is_public if status == Document.APPROVED else False,
            approved_by=user if status == Document.APPROVED else None,
            approved_at=timezone.now() if status == Document.APPROVED else None,
        )

        # 4. Tạo Object Key chuẩn và tải lên Cloudflare R2
        # Định dạng khóa: documents/{subject_id}/{doc_id}/v1_{filename}
        clean_filename = meta['filename'].replace(' ', '_')
        object_key = f"documents/{subject.id}/{doc.id}/v1_{clean_filename}"

        upload_res = r2_service.upload_file(
            file_obj=file_obj,
            object_key=object_key,
            content_type=meta['content_type'],
        )

        # 5. Lưu phiên bản v1.0 vào PostgreSQL
        version = DocumentVersion.objects.create(
            document=doc,
            file=object_key,
            version_number=1,
            updated_by=user,
            change_summary="Bản phát hành đầu tiên (v1.0)",
        )

        # Gắn thẻ (Tags) nếu có
        raw_tags = request.POST.get('tags', '')
        if raw_tags:
            tag_names = [t.strip().lower() for t in raw_tags.split(',') if t.strip()]
            for t_name in tag_names:
                tag, _ = Tag.objects.get_or_create(tag_name=t_name)
                doc.tags.add(tag)

        # 6. Ghi nhật ký hoạt động
        DocumentActivityLog.objects.create(
            document=doc,
            user=user,
            action='CREATE',
            description=f"Tải lên tài liệu mới '{title}' (Dung lượng: {round(meta['file_size']/1024, 1)} KB, SHA-256: {meta['checksum_sha256'][:12]}...)",
        )

    download_url = r2_service.generate_download_url(object_key)

    data = {
        'document_id': doc.id,
        'title': doc.title,
        'subject_id': subject.id,
        'subject_name': subject.subject_name,
        'status': doc.status,
        'is_public': doc.is_public,
        'version': {
            'version_id': version.id,
            'version_number': version.version_number,
            'object_key': object_key,
            'download_url': download_url,
            'storage_provider': upload_res['storage_provider'],
            'file_size': meta['file_size'],
            'content_type': meta['content_type'],
            'checksum_sha256': meta['checksum_sha256'],
        }
    }
    return _json_ok(data, message="Tải lên tài liệu thành công.", status=201)


@require_http_methods(["GET"])
def download_document_api(request, pk):
    """
    API Tải xuống tài liệu:
    - Kiểm tra quyền truy cập (ACL): Class, Department, User
    - Sinh Presigned URL Cloudflare R2 có hạn dùng (3600s)
    - Tăng số lượt tải (download_count)
    - Ghi nhận nhật ký DOWNLOAD
    """
    doc = get_object_or_404(Document, pk=pk)
    user = request.user

    # 1. Kiểm tra quyền tải theo ACL
    can_download, reason = can_user_download_document(user, doc)
    if not can_download:
        return _json_error(reason, 403)

    # 2. Lấy phiên bản mới nhất
    latest = doc.latest_version
    if not latest:
        return _json_error("Tài liệu không có phiên bản file nào khả dụng.", 404)

    # 3. Tăng lượt tải & ghi log
    Document.objects.filter(pk=pk).update(download_count=doc.download_count + 1)
    DocumentActivityLog.objects.create(
        document=doc,
        user=user if user.is_authenticated else None,
        action='DOWNLOAD',
        description=f"Tải xuống phiên bản v{latest.version_number}.0 (Khóa R2: {latest.object_key})",
    )

    # 4. Sinh URL tải an toàn từ Cloudflare R2
    download_url = latest.get_download_url(expires_in=3600)

    # Nếu client truyền ?redirect=true -> chuyển hướng trực tiếp
    if request.GET.get('redirect', '').lower() in ('true', '1'):
        from django.shortcuts import redirect
        return redirect(download_url)

    return _json_ok({
        'document_id': doc.id,
        'title': doc.title,
        'version_number': latest.version_number,
        'object_key': latest.object_key,
        'download_url': download_url,
        'expires_in': 3600,
    })


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_document_api(request, pk):
    """
    API Xóa tài liệu:
    - Chỉ cho phép Tác giả, Giảng viên hoặc Admin
    - Xóa toàn bộ file các phiên bản trên Cloudflare R2
    - Xóa bản ghi trong PostgreSQL
    - Ghi nhận nhật ký DELETE
    """
    doc = get_object_or_404(Document, pk=pk)
    user = request.user

    # Kiểm tra quyền xóa
    is_owner = (user.is_authenticated and doc.uploader_id == user.id)
    is_staff = (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False)))

    if not (is_owner or is_staff):
        return _json_error("Bạn không có quyền xóa tài liệu này.", 403)

    # Thu thập danh sách object key cần xóa trên R2
    object_keys = list(doc.versions.values_list('file', flat=True))

    with transaction.atomic():
        # Xóa các file trên R2
        for key in object_keys:
            if key:
                r2_service.delete_file(key)

        title = doc.title
        doc_id = doc.id
        doc.delete()

    return _json_ok(
        data={'deleted_document_id': doc_id, 'deleted_files_count': len(object_keys)},
        message=f"Đã xóa tài liệu '{title}' và các file liên quan trên Cloudflare R2.",
    )


@require_http_methods(["GET"])
def document_list_api(request):
    """
    API Danh sách tài liệu với bộ lọc:
    - q: tìm kiếm theo tiêu đề hoặc tên môn
    - subject_id: lọc theo môn
    - department_id: lọc theo khoa
    - status: PENDING, APPROVED, REJECTED
    - sort: newest, downloads, views
    """
    user = request.user
    qs = Document.objects.select_related('subject__department', 'uploader', 'approved_by')

    # Nếu là sinh viên thông thường: chỉ thấy APPROVED & public, hoặc bài của chính mình
    if not (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))):
        if user.is_authenticated:
            qs = qs.filter(Q(status=Document.APPROVED, is_public=True) | Q(uploader=user))
        else:
            qs = qs.filter(status=Document.APPROVED, is_public=True)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(subject__subject_name__icontains=q))

    subject_id = request.GET.get('subject_id')
    if subject_id:
        qs = qs.filter(subject_id=subject_id)

    dept_id = request.GET.get('department_id')
    if dept_id:
        qs = qs.filter(subject__department_id=dept_id)

    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status.upper())

    sort = request.GET.get('sort', 'newest')
    if sort == 'downloads':
        qs = qs.order_by('-download_count')
    elif sort == 'views':
        qs = qs.order_by('-view_count')
    else:
        qs = qs.order_by('-created_at')

    data = []
    for d in qs[:50]:
        latest = d.latest_version
        data.append({
            'document_id': d.id,
            'title': d.title,
            'description': d.description,
            'subject_id': d.subject_id,
            'subject_name': d.subject.subject_name if d.subject else '',
            'department_name': d.subject.department.department_name if d.subject and d.subject.department else '',
            'status': d.status,
            'is_public': d.is_public,
            'view_count': d.view_count,
            'download_count': d.download_count,
            'uploader_name': d.uploader.full_name if d.uploader else 'Ẩn danh',
            'latest_version': latest.version_number if latest else None,
            'created_at': d.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    return _json_ok(data)


@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def document_detail_api(request, pk):
    """
    API Chi tiết hoặc Xóa tài liệu:
    - GET: Chi tiết tài liệu, kiểm tra quyền truy cập, ghi log VIEW
    - DELETE: Xóa tài liệu và file trên Cloudflare R2, ghi log DELETE
    """
    if request.method == "DELETE":
        return delete_document_api(request, pk)
    doc = get_object_or_404(
        Document.objects.select_related('subject__department', 'uploader', 'approved_by').prefetch_related('tags', 'versions'),
        pk=pk,
    )
    user = request.user

    can_view, view_reason = can_user_access_document(user, doc)
    can_download, _ = can_user_download_document(user, doc)

    # Nếu người dùng có quyền xem -> tăng view_count và ghi log
    if can_view:
        Document.objects.filter(pk=pk).update(view_count=doc.view_count + 1)
        DocumentActivityLog.objects.create(
            document=doc,
            user=user if user.is_authenticated else None,
            action='VIEW',
        )

    versions_data = []
    for v in doc.versions.order_by('-version_number'):
        versions_data.append({
            'version_id': v.id,
            'version_number': v.version_number,
            'object_key': v.object_key,
            'download_url': v.get_download_url() if can_download else None,
            'change_summary': v.change_summary,
            'updated_at': v.updated_at.strftime('%Y-%m-%d %H:%M'),
        })

    data = {
        'document_id': doc.id,
        'title': doc.title,
        'description': doc.description,
        'subject_id': doc.subject_id,
        'subject_name': doc.subject.subject_name,
        'department_name': doc.subject.department.department_name,
        'folder_id': doc.folder_id,
        'status': doc.status,
        'is_public': doc.is_public,
        'view_count': doc.view_count,
        'download_count': doc.download_count,
        'uploader_name': doc.uploader.full_name if doc.uploader else 'Ẩn danh',
        'approved_by': doc.approved_by.full_name if doc.approved_by else None,
        'approved_at': doc.approved_at.strftime('%Y-%m-%d %H:%M') if doc.approved_at else None,
        'tags': [t.tag_name for t in doc.tags.all()],
        'can_view': can_view,
        'can_download': can_download,
        'access_note': view_reason,
        'versions': versions_data,
        'created_at': doc.created_at.strftime('%Y-%m-%d %H:%M'),
    }
    return _json_ok(data)


# ─── PHẦN 3: DUYỆT TÀI LIỆU, PHIÊN BẢN & NHẬT KÝ KIỂM TOÁN ──────────────────

@csrf_exempt
@require_http_methods(["POST"])
def approve_document_api(request, pk):
    """
    API Phê duyệt tài liệu (Giảng viên / Admin):
    - Đổi status -> APPROVED
    - Đặt is_public = True
    - Ghi nhận approved_by và approved_at
    - Ghi nhật ký kiểm toán APPROVE
    """
    doc = get_object_or_404(Document, pk=pk)
    user = request.user

    if not (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))):
        return _json_error("Chỉ có Giảng viên hoặc Quản trị viên mới có quyền phê duyệt tài liệu.", 403)

    from .services import approve_document
    doc = approve_document(doc, user)

    return _json_ok({
        'document_id': doc.id,
        'status': doc.status,
        'is_public': doc.is_public,
        'approved_by': user.full_name,
        'approved_at': doc.approved_at.isoformat(),
    }, message=f"Đã phê duyệt tài liệu '{doc.title}'.")


@csrf_exempt
@require_http_methods(["POST"])
def reject_document_api(request, pk):
    """
    API Từ chối tài liệu (Giảng viên / Admin):
    - Đổi status -> REJECTED
    - Đặt is_public = False
    - Yêu cầu lý do từ chối (feedback_reason)
    - Ghi nhật ký kiểm toán REJECT
    """
    doc = get_object_or_404(Document, pk=pk)
    user = request.user

    if not (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))):
        return _json_error("Chỉ có Giảng viên hoặc Quản trị viên mới có quyền từ chối duyệt.", 403)

    reason = request.POST.get('reason', '').strip()
    if not reason:
        # Hỗ trợ lấy từ JSON body nếu client gửi Application/json
        try:
            body_data = json.loads(request.body.decode('utf-8'))
            reason = body_data.get('reason', '').strip()
        except Exception:
            pass

    if not reason:
        return _json_error("Vui lòng nhập lý do từ chối để sinh viên chỉnh sửa.", 400)

    from .services import reject_document
    doc = reject_document(doc, user, reason)

    return _json_ok({
        'document_id': doc.id,
        'status': doc.status,
        'is_public': doc.is_public,
        'reason': reason,
    }, message=f"Đã từ chối duyệt tài liệu '{doc.title}'.")


@csrf_exempt
@require_http_methods(["POST"])
def create_version_api(request, pk):
    """
    API Nâng cấp phiên bản tài liệu (v2.0, v3.0...):
    - Nhận file mới, kiểm tra định dạng & dung lượng
    - Tải file lên Cloudflare R2 với object_key mới
    - Tự động tăng version_number
    - Lưu change_summary
    - Nếu sinh viên nộp lại sau khi bị từ chối -> tự động đưa về PENDING
    - Ghi log UPDATE
    """
    doc = get_object_or_404(Document, pk=pk)
    user = request.user

    # Kiểm tra quyền: Chỉ tác giả hoặc Giảng viên/Admin mới được cập nhật
    is_owner = (user.is_authenticated and doc.uploader_id == user.id)
    is_staff = (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False)))
    if not (is_owner or is_staff):
        return _json_error("Bạn không có quyền phát hành phiên bản mới cho tài liệu này.", 403)

    file_obj = request.FILES.get('file')
    if not file_obj:
        return _json_error("Vui lòng đính kèm file phiên bản mới.", 400)

    is_valid, err_msg, meta = validate_file_upload(file_obj)
    if not is_valid:
        return _json_error(err_msg, 400)

    change_summary = request.POST.get('change_summary', '').strip() or "Cập nhật nội dung tài liệu"

    latest = doc.latest_version
    next_ver = (latest.version_number + 1) if latest else 1

    clean_filename = meta['filename'].replace(' ', '_')
    object_key = f"documents/{doc.subject_id}/{doc.id}/v{next_ver}_{clean_filename}"

    # Upload R2
    upload_res = r2_service.upload_file(
        file_obj=file_obj,
        object_key=object_key,
        content_type=meta['content_type'],
    )

    with transaction.atomic():
        version = DocumentVersion.objects.create(
            document=doc,
            file=object_key,
            version_number=next_ver,
            change_summary=change_summary,
            updated_by=user if user.is_authenticated else None,
        )

        # Nếu sinh viên nộp lại sau khi bị REJECTED -> đưa về PENDING để duyệt lại
        if doc.status == Document.REJECTED:
            doc.status = Document.PENDING
            doc.save(update_fields=['status'])

        # Ghi log hoạt động
        DocumentActivityLog.objects.create(
            document=doc,
            user=user if user.is_authenticated else None,
            action='UPDATE',
            description=f"Phát hành phiên bản v{next_ver}.0: {change_summary}",
        )

    return _json_ok({
        'document_id': doc.id,
        'version_id': version.id,
        'version_number': version.version_number,
        'object_key': object_key,
        'download_url': version.get_download_url(),
        'change_summary': version.change_summary,
        'doc_status': doc.status,
    }, message=f"Đã nâng cấp phiên bản lên v{next_ver}.0 thành công.", status=201)


@require_http_methods(["GET"])
def version_list_api(request, pk):
    """
    API Lấy danh sách lịch sử tất cả phiên bản của một tài liệu.
    """
    doc = get_object_or_404(Document, pk=pk)
    user = request.user
    can_download, _ = can_user_download_document(user, doc)

    versions = []
    for v in doc.versions.order_by('-version_number'):
        versions.append({
            'version_id': v.id,
            'version_number': v.version_number,
            'object_key': v.object_key,
            'download_url': v.get_download_url() if can_download else None,
            'change_summary': v.change_summary,
            'updated_by': v.updated_by.full_name if v.updated_by else 'Ẩn danh',
            'updated_at': v.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    return _json_ok({
        'document_id': doc.id,
        'title': doc.title,
        'total_versions': len(versions),
        'versions': versions,
    })


@require_http_methods(["GET"])
def document_logs_api(request, pk):
    """
    API Lấy nhật ký kiểm toán (Audit Activity Logs) của tài liệu.
    """
    doc = get_object_or_404(Document, pk=pk)
    logs = doc.activity_logs.select_related('user').order_by('-created_at')

    data = []
    for log in logs:
        data.append({
            'log_id': log.id,
            'action': log.action,
            'action_display': log.get_action_display(),
            'description': log.description,
            'user': log.user.full_name if log.user else 'Hệ thống / Ẩn danh',
            'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    return _json_ok({
        'document_id': doc.id,
        'title': doc.title,
        'total_logs': len(data),
        'logs': data,
    })
