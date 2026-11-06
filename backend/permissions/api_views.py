"""
DocUni - REST API Quản Lý Quyền Truy Cập Tài Liệu (ACL Management)
Phần 3:
- GET  /api/documents/<doc_id>/permissions/ : Danh sách phân quyền của tài liệu
- POST /api/documents/<doc_id>/permissions/ : Thêm quyền truy cập (CLASS, DEPARTMENT, USER)
- DELETE /api/documents/<doc_id>/permissions/<perm_id>/ : Gỡ quyền truy cập
- GET  /api/documents/<doc_id>/check-access/ : Kiểm tra quyền truy cập của người dùng hiện tại
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from documents.models import Document, DocumentActivityLog
from academics.models import Department, Class
from accounts.models import User
from .models import DocumentPermission
from .services import can_user_access_document, can_user_download_document


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


@csrf_exempt
@require_http_methods(["GET", "POST"])
def document_permissions_api(request, doc_id):
    doc = get_object_or_404(Document, pk=doc_id)
    user = request.user

    # GET: Xem danh sách phân quyền
    if request.method == "GET":
        perms = doc.permissions.select_related('department', 'student_class', 'user').order_by('created_at')
        data = []
        for p in perms:
            target_name = ''
            if p.permission_type == DocumentPermission.CLASS and p.student_class:
                target_name = f"Lớp {p.student_class.class_name}"
            elif p.permission_type == DocumentPermission.DEPARTMENT and p.department:
                target_name = f"Khoa {p.department.department_name}"
            elif p.permission_type == DocumentPermission.USER and p.user:
                target_name = f"Người dùng {p.user.full_name} (@{p.user.username})"

            data.append({
                'permission_id': p.id,
                'permission_type': p.permission_type,
                'target_name': target_name,
                'class_id': p.student_class_id,
                'department_id': p.department_id,
                'user_id': p.user_id,
                'can_view': p.can_view,
                'can_download': p.can_download,
                'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
            })

        return _json_ok({
            'document_id': doc.id,
            'title': doc.title,
            'is_public': doc.is_public,
            'permissions': data,
        })

    # POST: Thêm phân quyền mới (Chỉ Tác giả, Giảng viên hoặc Admin)
    is_owner = (user.is_authenticated and doc.uploader_id == user.id)
    is_staff = (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False)))
    if not (is_owner or is_staff):
        return _json_error("Bạn không có quyền cấu hình phân quyền cho tài liệu này.", 403)

    data = request.POST
    if not data:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}

    perm_type = (data.get('permission_type') or '').upper()
    if perm_type not in (DocumentPermission.CLASS, DocumentPermission.DEPARTMENT, DocumentPermission.USER):
        return _json_error("Loại quyền 'permission_type' phải là CLASS, DEPARTMENT hoặc USER.", 400)

    can_view = str(data.get('can_view', 'true')).lower() in ('true', '1', 'yes')
    can_download = str(data.get('can_download', 'true')).lower() in ('true', '1', 'yes')

    student_class = None
    department = None
    target_user = None

    if perm_type == DocumentPermission.CLASS:
        class_id = data.get('class_id')
        if not class_id:
            return _json_error("Vui lòng cung cấp 'class_id'.", 400)
        student_class = get_object_or_404(Class, pk=class_id)
        target_desc = f"Lớp {student_class.class_name}"

    elif perm_type == DocumentPermission.DEPARTMENT:
        dept_id = data.get('department_id')
        if not dept_id:
            return _json_error("Vui lòng cung cấp 'department_id'.", 400)
        department = get_object_or_404(Department, pk=dept_id)
        target_desc = f"Khoa {department.department_name}"

    elif perm_type == DocumentPermission.USER:
        target_uid = data.get('user_id')
        if not target_uid:
            return _json_error("Vui lòng cung cấp 'user_id'.", 400)
        target_user = get_object_or_404(User, pk=target_uid)
        target_desc = f"Người dùng {target_user.full_name}"

    perm = DocumentPermission.objects.create(
        document=doc,
        permission_type=perm_type,
        student_class=student_class,
        department=department,
        user=target_user,
        can_view=can_view,
        can_download=can_download,
    )

    # Ghi log hoạt động
    DocumentActivityLog.objects.create(
        document=doc,
        user=user,
        action='CHANGE_PERMISSION',
        description=f"Cấp quyền truy cập ({'Xem' if can_view else ''}{'+ Tải' if can_download else ''}) cho {target_desc}.",
    )

    return _json_ok({
        'permission_id': perm.id,
        'permission_type': perm.permission_type,
        'target_desc': target_desc,
        'can_view': perm.can_view,
        'can_download': perm.can_download,
    }, message=f"Đã thêm quyền cho {target_desc}.", status=201)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_permission_api(request, doc_id, perm_id):
    """Xóa một quyền truy cập."""
    doc = get_object_or_404(Document, pk=doc_id)
    user = request.user

    is_owner = (user.is_authenticated and doc.uploader_id == user.id)
    is_staff = (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False)))
    if not (is_owner or is_staff):
        return _json_error("Bạn không có quyền xóa phân quyền của tài liệu này.", 403)

    perm = get_object_or_404(DocumentPermission, pk=perm_id, document=doc)
    perm.delete()

    DocumentActivityLog.objects.create(
        document=doc,
        user=user,
        action='CHANGE_PERMISSION',
        description=f"Đã gỡ quyền truy cập (Loại {perm.permission_type}).",
    )

    return _json_ok(message="Đã gỡ bỏ quyền truy cập thành công.")


@require_http_methods(["GET"])
def check_document_access_api(request, doc_id):
    """Kiểm tra quyền truy cập của người dùng với tài liệu."""
    doc = get_object_or_404(Document, pk=doc_id)
    user = request.user

    can_view, view_reason = can_user_access_document(user, doc)
    can_download, dl_reason = can_user_download_document(user, doc)

    return _json_ok({
        'document_id': doc.id,
        'title': doc.title,
        'is_public': doc.is_public,
        'status': doc.status,
        'can_view': can_view,
        'view_reason': view_reason,
        'can_download': can_download,
        'download_reason': dl_reason,
    })
