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

import os
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count

from .models import Document, DocumentVersion, DocumentActivityLog, Folder, Tag
from academics.models import Subject
from .validators import validate_file_upload
from .r2_service import r2_service
from permissions.services import can_user_access_document, can_user_download_document
from .indexing_service import index_document, get_indexing_stats


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

        # 7. Tự động Indexing phục vụ tìm kiếm ngữ cảnh AI
        try:
            index_document(doc, user=user)
        except Exception:
            pass

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


@csrf_exempt
@require_http_methods(["GET", "POST"])
def document_list_api(request):
    """
    API Danh sách tài liệu với bộ lọc hoặc tạo tài liệu mới:
    """
    if request.method == "POST":
        body = {}
        if request.body:
            try:
                body = json.loads(request.body.decode('utf-8'))
            except Exception:
                pass
        title = body.get('title') or request.POST.get('title', '').strip()
        description = body.get('description') or request.POST.get('description', '').strip()
        subject_id = body.get('subject_id') or request.POST.get('subject_id')
        folder_id = body.get('folder_id') or request.POST.get('folder_id')
        is_public = body.get('is_public', False)
        if isinstance(is_public, str):
            is_public = is_public.lower() in ('true', '1', 'yes')

        if not title:
            return _json_error("Tiêu đề tài liệu là bắt buộc.", 400)
        if not subject_id:
            return _json_error("Môn học là bắt buộc.", 400)

        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return _json_error("Môn học không tồn tại.", 404)

        user = request.user if request.user.is_authenticated else None
        folder = None
        if folder_id:
            try:
                folder = Folder.objects.get(pk=folder_id)
            except Folder.DoesNotExist:
                pass

        doc_status = Document.APPROVED if is_public else Document.PENDING
        approved_by = None
        approved_at = None
        if doc_status == Document.APPROVED:
            approved_by = user or User.objects.filter(role__role_name='ADMIN').first()
            approved_at = timezone.now()

        doc = Document.objects.create(
            title=title,
            description=description,
            subject=subject,
            folder=folder,
            uploader=user,
            status=doc_status,
            approved_by=approved_by,
            approved_at=approved_at,
            is_public=bool(is_public),
        )
        doc_payload = {
            'document_id': doc.id,
            'id': doc.id,
            'title': doc.title,
            'description': doc.description,
            'subject_id': doc.subject_id,
            'status': doc.status,
            'is_public': doc.is_public,
        }
        return JsonResponse({
            'status': 'ok',
            'message': 'Tạo tài liệu thành công.',
            'document': doc_payload,
            'data': doc_payload,
        }, status=201, json_dumps_params={'ensure_ascii': False})

    user = request.user
    qs = Document.objects.select_related('subject__department', 'uploader', 'approved_by')

    scope = request.GET.get('scope', 'all')
    if scope == 'strict':
        # Nếu là sinh viên thông thường và yêu cầu lọc nghiêm ngặt: chỉ thấy APPROVED & public, hoặc bài của chính mình
        if not (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))):
            if user.is_authenticated:
                qs = qs.filter(Q(status=Document.APPROVED, is_public=True) | Q(uploader=user))
            else:
                qs = qs.filter(status=Document.APPROVED, is_public=True)

    uploader_param = request.GET.get('uploader', '').strip()
    if uploader_param == 'me' and user.is_authenticated:
        qs = qs.filter(uploader=user)
    elif uploader_param and uploader_param.isdigit():
        qs = qs.filter(uploader_id=int(uploader_param))

    q = request.GET.get('q', '').strip()
    matched_snippets = {}
    if q:
        # 1. Tìm trong nội dung đã lập chỉ mục (document_embeddings)
        content_doc_ids = set()
        try:
            from ai_search.models import DocumentEmbedding
            matching_chunks = DocumentEmbedding.objects.filter(chunk_text__icontains=q)
            for chunk in matching_chunks:
                c_doc_id = chunk.document_id
                content_doc_ids.add(c_doc_id)
                if c_doc_id not in matched_snippets:
                    # Trích đoạn ngữ cảnh chứa từ khóa tìm kiếm
                    text = chunk.chunk_text
                    idx = text.lower().find(q.lower())
                    start = max(0, idx - 45)
                    end = min(len(text), idx + len(q) + 90)
                    snip = ("..." if start > 0 else "") + text[start:end].strip() + ("..." if end < len(text) else "")
                    matched_snippets[c_doc_id] = snip
        except Exception:
            pass

        # 2. Kết hợp tìm kiếm đa trường: Tiêu đề, Mô tả, Môn học, Thẻ (Tags) và Nội dung tệp
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(subject__subject_name__icontains=q) |
            Q(tags__tag_name__icontains=q) |
            Q(id__in=content_doc_ids)
        ).distinct()

    subject_id = request.GET.get('subject_id')
    if subject_id:
        qs = qs.filter(subject_id=subject_id)

    dept_id = request.GET.get('department_id')
    if dept_id:
        qs = qs.filter(subject__department_id=dept_id)

    doc_status = request.GET.get('status')
    if doc_status and doc_status.upper() != 'ALL':
        qs = qs.filter(status=doc_status.upper())

    folder_id = request.GET.get('folder_id')
    if folder_id:
        qs = qs.filter(folder_id=folder_id)

    tag_filter = request.GET.get('tag', '').strip()
    if tag_filter:
        qs = qs.filter(tags__tag_name__iexact=tag_filter)

    sort = request.GET.get('sort', 'newest')
    if sort == 'downloads':
        qs = qs.order_by('-download_count')
    elif sort == 'views':
        qs = qs.order_by('-view_count')
    else:
        qs = qs.order_by('id')

    data = []
    for d in qs:
        latest = d.latest_version
        dept_obj = d.subject.department if d.subject else None
        str_file = str(latest.file) if (latest and latest.file) else ''
        fname = os.path.basename(str_file) if str_file else f"document_{d.id}.pdf"
        fsize = 1024 * 1024 * 2

        data.append({
            'document_id': d.id,
            'id': d.id,
            'title': d.title,
            'description': d.description or '',
            'matched_snippet': matched_snippets.get(d.id, ''),
            'is_content_match': bool(matched_snippets.get(d.id)),
            'subject_id': d.subject_id,
            'subject': {
                'subject_id': d.subject_id,
                'subject_name': d.subject.subject_name if d.subject else '',
                'department': {
                    'department_id': dept_obj.id if dept_obj else None,
                    'department_name': dept_obj.department_name if dept_obj else '',
                }
            },
            'subject_name': d.subject.subject_name if d.subject else '',
            'department_name': dept_obj.department_name if dept_obj else '',
            'status': d.status,
            'is_public': d.is_public,
            'view_count': d.view_count,
            'download_count': d.download_count,
            'uploader_id': d.uploader_id,
            'uploader_name': d.uploader.full_name if (d.uploader and d.uploader.full_name) else (d.uploader.username if d.uploader else 'Ẩn danh'),
            'file_name': fname,
            'original_file_name': fname,
            'file_size': fsize,
            'folder_id': d.folder_id,
            'folder_name': d.folder.folder_name if d.folder else None,
            'tags': [t.tag_name for t in d.tags.all()],
            'latest_version': latest.version_number if latest else 'v1.0',
            'created_at': d.created_at.strftime('%Y-%m-%d %H:%M') if d.created_at else '',
        })

    return JsonResponse({
        'status': 'ok',
        'message': 'Thành công',
        'documents': data,
        'data': data,
        'total': len(data),
    }, status=200, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def document_detail_api(request, pk):
    """
    API Chi tiết, Sửa hoặc Xóa tài liệu:
    - GET: Chi tiết tài liệu
    - PATCH: Cập nhật tiêu đề, mô tả
    - DELETE: Xóa tài liệu
    """
    if request.method == "DELETE":
        return delete_document_api(request, pk)

    doc = get_object_or_404(
        Document.objects.select_related('subject__department', 'uploader', 'approved_by').prefetch_related('tags', 'versions'),
        pk=pk,
    )

    if request.method == "PATCH":
        body = {}
        if request.body:
            try:
                body = json.loads(request.body.decode('utf-8'))
            except Exception:
                pass
        if 'title' in body:
            doc.title = body['title']
        if 'description' in body:
            doc.description = body['description']
        if 'is_public' in body:
            doc.is_public = bool(body['is_public'])
        if 'status' in body:
            doc.status = body['status']
        doc.save()
        doc_payload = {
            'document_id': doc.id,
            'id': doc.id,
            'title': doc.title,
            'description': doc.description,
            'status': doc.status,
            'is_public': doc.is_public,
        }
        return JsonResponse({
            'status': 'ok',
            'message': 'Cập nhật tài liệu thành công.',
            'document': doc_payload,
            'data': doc_payload,
        }, status=200, json_dumps_params={'ensure_ascii': False})

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

        # Lập chỉ mục nội dung cho phiên bản mới
        try:
            index_document(doc, user=user)
        except Exception:
            pass

    return _json_ok({
        'document_id': doc.id,
        'version_id': version.id,
        'version_number': version.version_number,
        'object_key': object_key,
        'download_url': version.get_download_url(),
        'change_summary': version.change_summary,
        'doc_status': doc.status,
    }, message=f"Đã nâng cấp phiên bản lên v{next_ver}.0 thành công.", status=201)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def version_list_api(request, pk):
    """
    API Lấy danh sách lịch sử tất cả phiên bản của một tài liệu hoặc tải lên phiên bản mới.
    """
    if request.method == "POST":
        return create_version_api(request, pk)

    doc = get_object_or_404(Document, pk=pk)
    user = request.user
    can_download, _ = can_user_download_document(user, doc)

    versions = []
    for v in doc.versions.order_by('-version_number'):
        versions.append({
            'id': v.id,
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


@require_http_methods(["GET"])
def activity_logs_api(request):
    """
    API Lấy nhật ký hoạt động chung của toàn hệ thống kèm bộ lọc (Action, User, Document, Days, Search).
    """
    qs = DocumentActivityLog.objects.select_related('document', 'user').order_by('-created_at')

    action = request.GET.get('action')
    if action and action.upper() != 'ALL':
        qs = qs.filter(action=action.upper())

    user_id = request.GET.get('user_id')
    if user_id:
        qs = qs.filter(user_id=user_id)

    doc_id = request.GET.get('document_id')
    if doc_id:
        qs = qs.filter(document_id=doc_id)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(description__icontains=q) | Q(document__title__icontains=q))

    days = request.GET.get('days')
    if days and days.isdigit():
        from datetime import timedelta
        since = timezone.now() - timedelta(days=int(days))
        qs = qs.filter(created_at__gte=since)

    limit = int(request.GET.get('limit', 100))
    logs = qs[:limit]

    data = [{
        'log_id': log.id,
        'document_id': log.document_id,
        'document_title': log.document.title if log.document else 'Tài liệu',
        'user_id': log.user_id,
        'user_name': log.user.full_name if (log.user and log.user.full_name) else (log.user.username if log.user else 'Hệ thống / Ẩn danh'),
        'user_role': log.user.role.role_name if (log.user and log.user.role) else 'User',
        'action': log.action,
        'action_display': log.get_action_display(),
        'description': log.description,
        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
    } for log in logs]

    return JsonResponse({
        'status': 'ok',
        'logs': data,
        'data': data,
        'total': len(data),
    }, status=200, json_dumps_params={'ensure_ascii': False})


# ─── TAG MANAGEMENT APIs ─────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def tag_list_create_api(request):
    """
    API Quản lý thẻ tài liệu:
    - GET: Danh sách tất cả thẻ kèm số lượng tài liệu gắn thẻ
    - POST: Tạo thẻ mới (Admin / Giảng viên)
    """
    if request.method == "GET":
        tags = Tag.objects.annotate(doc_count=Count('documents')).order_by('tag_name')
        q = request.GET.get('q', '').strip()
        if q:
            tags = tags.filter(tag_name__icontains=q)

        data = [{
            'id': t.id,
            'tag_id': t.id,
            'tag_name': t.tag_name,
            'doc_count': t.doc_count,
        } for t in tags]

        return JsonResponse({
            'status': 'ok',
            'tags': data,
            'data': data,
            'total': len(data),
        }, status=200, json_dumps_params={'ensure_ascii': False})

    # POST: Tạo thẻ mới
    user = request.user
    if not (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))):
        return _json_error("Chỉ Quản trị viên hoặc Giảng viên mới có quyền tạo thẻ tag.", 403)

    name = request.POST.get('tag_name', '').strip().lower()
    if not name:
        try:
            b = json.loads(request.body.decode('utf-8'))
            name = b.get('tag_name', '').strip().lower()
        except Exception:
            pass

    if not name:
        return _json_error("Tên thẻ (tag_name) không được để trống.", 400)

    tag, created = Tag.objects.get_or_create(tag_name=name)
    return _json_ok({
        'id': tag.id,
        'tag_id': tag.id,
        'tag_name': tag.tag_name,
        'created': created,
    }, message=f"Đã {'tạo mới' if created else 'lấy'} thẻ #{tag.tag_name}.", status=201 if created else 200)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def tag_detail_api(request, pk):
    """Chỉnh sửa hoặc xóa thẻ tag (Admin only)."""
    tag = get_object_or_404(Tag, pk=pk)
    user = request.user
    if not (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))):
        return _json_error("Chỉ Quản trị viên hoặc Giảng viên mới có quyền chỉnh sửa/xóa thẻ tag.", 403)

    if request.method == "PATCH":
        data = {}
        if request.body:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                pass
        if not data:
            data = request.POST
        new_name = data.get('tag_name', '').strip().lower()
        if not new_name:
            return _json_error("Tên thẻ mới không được để trống.", 400)
        tag.tag_name = new_name
        tag.save()
        return _json_ok({'id': tag.id, 'tag_name': tag.tag_name}, message=f"Đã cập nhật tên thẻ thành #{tag.tag_name}.")

    if request.method == "DELETE":
        name = tag.tag_name
        tag.delete()
        return _json_ok({'deleted_tag_id': pk}, message=f"Đã xóa thẻ #{name} khỏi hệ thống.")


@csrf_exempt
@require_http_methods(["POST"])
def document_attach_tag_api(request, pk):
    """Gắn thẻ tag vào tài liệu."""
    doc = get_object_or_404(Document, pk=pk)
    user = request.user
    is_owner = (user.is_authenticated and doc.uploader_id == user.id)
    is_staff = (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False)))
    if not (is_owner or is_staff):
        return _json_error("Bạn không có quyền gắn thẻ cho tài liệu này.", 403)

    data = {}
    if request.body:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            pass
    if not data:
        data = request.POST

    tag_name = data.get('tag_name', '').strip().lower()
    tag_id = data.get('tag_id')
    if tag_id:
        t_obj = Tag.objects.filter(id=tag_id).first()
        if t_obj:
            tag_name = t_obj.tag_name
    tags_list = data.get('tags', [])
    if isinstance(tags_list, str):
        tags_list = [t.strip().lower() for t in tags_list.split(',') if t.strip()]

    if tag_name and tag_name not in tags_list:
        tags_list.append(tag_name)

    attached = []
    for t_name in tags_list:
        if t_name:
            tag, _ = Tag.objects.get_or_create(tag_name=t_name)
            doc.tags.add(tag)
            attached.append(tag.tag_name)
            DocumentActivityLog.objects.create(
                document=doc,
                user=user,
                action='ADD_TAG',
                description=f"Gắn thẻ #{tag.tag_name} vào tài liệu '{doc.title}'.",
            )

    return _json_ok({
        'document_id': doc.id,
        'attached_tags': attached,
        'current_tags': [t.tag_name for t in doc.tags.all()],
    }, message=f"Đã gắn {len(attached)} thẻ vào tài liệu.")


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def document_detach_tag_api(request, pk, tag_id):
    """Gỡ thẻ tag khỏi tài liệu."""
    doc = get_object_or_404(Document, pk=pk)
    tag = get_object_or_404(Tag, pk=tag_id)
    user = request.user
    is_owner = (user.is_authenticated and doc.uploader_id == user.id)
    is_staff = (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False)))
    if not (is_owner or is_staff):
        return _json_error("Bạn không có quyền gỡ thẻ của tài liệu này.", 403)

    doc.tags.remove(tag)
    DocumentActivityLog.objects.create(
        document=doc,
        user=user,
        action='REMOVE_TAG',
        description=f"Gỡ thẻ #{tag.tag_name} khỏi tài liệu '{doc.title}'.",
    )
    return _json_ok({
        'document_id': doc.id,
        'detached_tag': tag.tag_name,
        'current_tags': [t.tag_name for t in doc.tags.all()],
    }, message=f"Đã gỡ thẻ #{tag.tag_name} khỏi tài liệu.")


# ─── VERSIONING RESTORE & DOWNLOAD APIs ──────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def version_restore_api(request, pk, ver_id):
    """
    Khôi phục tài liệu về phiên bản cũ:
    Tạo một phiên bản mới với version_number tăng dần kế thừa file từ phiên bản cũ,
    không xóa lịch sử các phiên bản trung gian.
    """
    doc = get_object_or_404(Document, pk=pk)
    target_ver = get_object_or_404(DocumentVersion, pk=ver_id, document=doc)
    user = request.user
    is_owner = (user.is_authenticated and doc.uploader_id == user.id)
    is_staff = (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False)))
    if not (is_owner or is_staff):
        return _json_error("Bạn không có quyền khôi phục phiên bản tài liệu.", 403)

    latest = doc.latest_version
    next_ver = (latest.version_number + 1) if latest else 1

    summary = f"Khôi phục từ phiên bản v{target_ver.version_number}.0 (Gốc: {target_ver.change_summary or 'Ban đầu'})"
    new_ver = DocumentVersion.objects.create(
        document=doc,
        file=target_ver.file,
        version_number=next_ver,
        change_summary=summary,
        updated_by=user if user.is_authenticated else None,
    )

    DocumentActivityLog.objects.create(
        document=doc,
        user=user if user.is_authenticated else None,
        action='UPDATE',
        description=f"Khôi phục nội dung từ phiên bản v{target_ver.version_number}.0 thành phiên bản v{next_ver}.0",
    )

    try:
        index_document(doc, user=user)
    except Exception:
        pass

    return _json_ok({
        'document_id': doc.id,
        'restored_from_version': target_ver.version_number,
        'new_version_id': new_ver.id,
        'new_version_number': new_ver.version_number,
        'change_summary': new_ver.change_summary,
    }, message=f"Đã khôi phục tài liệu thành công về phiên bản mới v{next_ver}.0.")


@require_http_methods(["GET"])
def version_download_api(request, pk, ver_id):
    """Tải xuống file của một phiên bản cụ thể."""
    doc = get_object_or_404(Document, pk=pk)
    version = get_object_or_404(DocumentVersion, pk=ver_id, document=doc)
    user = request.user

    can_download, reason = can_user_download_document(user, doc)
    if not can_download:
        return _json_error(reason, 403)

    DocumentActivityLog.objects.create(
        document=doc,
        user=user if user.is_authenticated else None,
        action='DOWNLOAD',
        description=f"Tải xuống phiên bản lịch sử v{version.version_number}.0 (Object: {version.object_key})",
    )
    download_url = version.get_download_url(expires_in=3600)
    return _json_ok({
        'document_id': doc.id,
        'version_id': version.id,
        'version_number': version.version_number,
        'download_url': download_url,
    })


# ─── SUBMIT FOR APPROVAL API ─────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def submit_approval_api(request, pk):
    """Gửi tài liệu vào hàng đợi xét duyệt công khai (status -> PENDING)."""
    doc = get_object_or_404(Document, pk=pk)
    user = request.user
    is_owner = (user.is_authenticated and doc.uploader_id == user.id)
    is_staff = (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False)))
    if not (is_owner or is_staff):
        return _json_error("Bạn không có quyền gửi duyệt tài liệu này.", 403)

    doc.status = Document.PENDING
    doc.save(update_fields=['status'])

    DocumentActivityLog.objects.create(
        document=doc,
        user=user if user.is_authenticated else None,
        action='UPDATE',
        description=f"Gửi tài liệu '{doc.title}' vào hàng đợi kiểm duyệt công khai.",
    )
    return _json_ok({
        'document_id': doc.id,
        'status': doc.status,
    }, message=f"Đã gửi tài liệu '{doc.title}' vào hàng đợi xét duyệt.")


# ─── INDEXING APIS ───────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def reindex_document_api(request, pk):
    """Reindex một tài liệu cụ thể (Admin / Giảng viên)."""
    doc = get_object_or_404(Document, pk=pk)
    user = request.user
    if not (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))):
        return _json_error("Chỉ Quản trị viên mới có quyền Indexing tài liệu.", 403)

    res = index_document(doc, user=user)
    return _json_ok(res, message=f"Đã Indexing thành công tài liệu '{doc.title}'.")


@require_http_methods(["GET"])
def indexing_status_api(request):
    """Thống kê trạng thái Indexing toàn hệ thống từ PostgreSQL."""
    return _json_ok(get_indexing_stats())


@csrf_exempt
@require_http_methods(["POST"])
def indexing_run_all_api(request):
    """Chạy Indexing toàn bộ tài liệu trong hệ thống (Admin only)."""
    user = request.user
    if not (user.is_authenticated and getattr(user, 'is_admin', False)):
        return _json_error("Chỉ Quản trị viên mới có quyền chạy Indexing toàn bộ hệ thống.", 403)

    docs = Document.objects.all()
    count = 0
    for d in docs:
        index_document(d, user=user)
        count += 1

    stats = get_indexing_stats()
    stats['indexed_count'] = count
    return _json_ok(stats, message=f"Đã Indexing toàn bộ {count} tài liệu vào PostgreSQL.")

