"""
DocUni - REST API Quản Lý Khoa, Lớp Học, Môn Học & Cây Thư Mục
Phần 3:
- GET /api/departments/ & POST /api/departments/
- GET /api/classes/ & POST /api/classes/
- PATCH /api/classes/<id>/toggle-lock/
- GET /api/subjects/ & POST /api/subjects/
- GET /api/subjects/<id>/folders/tree/ : Lấy toàn bộ cây thư mục phân cấp
- POST /api/folders/ : Tạo thư mục/thư mục con
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Department, Class, Subject
from documents.models import Folder
from documents.services import get_folder_tree, create_folder


def _json_error(message: str, status: int = 400, errors=None) -> JsonResponse:
    payload = {'status': 'error', 'message': message}
    if errors:
        payload['errors'] = errors
    res = JsonResponse(payload, status=status, json_dumps_params={'ensure_ascii': False})
    res.data = payload
    return res


def _json_ok(data=None, message: str = 'Thành công', status: int = 200) -> JsonResponse:
    payload = {'status': 'ok', 'message': message}
    if data is not None:
        payload['data'] = data
    res = JsonResponse(payload, status=status, json_dumps_params={'ensure_ascii': False})
    res.data = payload
    return res


# ─── DEPARTMENTS API ─────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def department_api(request):
    if request.method == "GET":
        depts = Department.objects.annotate(
            class_count=Count('classes', distinct=True),
            subject_count=Count('subjects', distinct=True),
        ).order_by('department_name')
        data = [{
            'id': d.id,
            'department_id': d.id,
            'department_name': d.department_name,
            'class_count': d.class_count,
            'subject_count': d.subject_count,
        } for d in depts]
        return JsonResponse({
            'status': 'ok',
            'departments': data,
            'data': data,
            'total': len(data),
        }, status=200, json_dumps_params={'ensure_ascii': False})

    # POST: Tạo khoa mới (Admin only)
    if not (request.user.is_authenticated and getattr(request.user, 'is_admin', False)):
        return _json_error("Chỉ Quản trị viên mới có quyền tạo Khoa.", 403)

    name = request.POST.get('department_name', '').strip()
    if not name:
        try:
            body = json.loads(request.body.decode('utf-8'))
            name = body.get('department_name', '').strip()
        except Exception:
            pass

    if not name:
        return _json_error("Tên khoa không được để trống.", 400)

    if Department.objects.filter(department_name__iexact=name).exists():
        return _json_error("Tên khoa đã tồn tại.", 400)

    dept = Department.objects.create(department_name=name)
    return _json_ok({'id': dept.id, 'department_name': dept.department_name}, message="Tạo khoa thành công.", status=201)


# ─── CLASSES API ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def class_api(request):
    if request.method == "GET":
        dept_id = request.GET.get('department_id')
        qs = Class.objects.select_related('department').order_by('class_name')
        if dept_id:
            qs = qs.filter(department_id=dept_id)

        data = [{
            'id': c.id,
            'class_id': c.id,
            'class_name': c.class_name,
            'department_id': c.department_id,
            'department_name': c.department.department_name if c.department else '',
            'department': {
                'department_id': c.department_id,
                'department_name': c.department.department_name if c.department else '',
            } if c.department else {},
            'is_locked': c.is_locked,
        } for c in qs]
        return JsonResponse({
            'status': 'ok',
            'classes': data,
            'data': data,
            'total': len(data),
        }, status=200, json_dumps_params={'ensure_ascii': False})

    # POST: Tạo lớp mới (Admin only)
    if not (request.user.is_authenticated and getattr(request.user, 'is_admin', False)):
        return _json_error("Chỉ Quản trị viên mới có quyền tạo Lớp.", 403)

    name = request.POST.get('class_name', '').strip()
    dept_id = request.POST.get('department_id')
    if not name:
        try:
            body = json.loads(request.body.decode('utf-8'))
            name = body.get('class_name', '').strip()
            dept_id = body.get('department_id')
        except Exception:
            pass

    if not name:
        return _json_error("Tên lớp không được để trống.", 400)
    if not dept_id:
        return _json_error("Khoa (department_id) là bắt buộc.", 400)

    try:
        dept = Department.objects.get(pk=dept_id)
    except Department.DoesNotExist:
        return _json_error("Khoa không tồn tại.", 404)

    if Class.objects.filter(class_name__iexact=name).exists():
        return _json_error("Tên lớp đã tồn tại.", 400)

    cls = Class.objects.create(class_name=name, department=dept)
    return _json_ok({
        'id': cls.id,
        'class_name': cls.class_name,
        'department_id': dept.id,
        'department_name': dept.department_name,
        'is_locked': cls.is_locked,
    }, message="Tạo lớp học thành công.", status=201)


@csrf_exempt
@require_http_methods(["PATCH", "POST"])
def class_toggle_lock_api(request, pk):
    """Khóa hoặc mở khóa lớp học."""
    if not (request.user.is_authenticated and getattr(request.user, 'is_admin', False)):
        return _json_error("Chỉ Quản trị viên mới có quyền khóa/mở khóa lớp.", 403)

    cls = get_object_or_404(Class, pk=pk)
    cls.is_locked = not cls.is_locked
    cls.save(update_fields=['is_locked'])

    state_str = "khóa" if cls.is_locked else "mở khóa"
    return _json_ok({
        'id': cls.id,
        'class_name': cls.class_name,
        'is_locked': cls.is_locked,
    }, message=f"Đã {state_str} lớp {cls.class_name}.")


# ─── SUBJECTS API ────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def subject_api(request):
    if request.method == "GET":
        dept_id = request.GET.get('department_id')
        qs = Subject.objects.select_related('department').order_by('subject_name')
        if dept_id:
            qs = qs.filter(department_id=dept_id)

        data = [{
            'id': s.id,
            'subject_id': s.id,
            'subject_name': s.subject_name,
            'department_id': s.department_id,
            'department_name': s.department.department_name if s.department else '',
            'department': {
                'department_id': s.department_id,
                'department_name': s.department.department_name if s.department else '',
            } if s.department else {},
        } for s in qs]
        return JsonResponse({
            'status': 'ok',
            'subjects': data,
            'data': data,
            'total': len(data),
        }, status=200, json_dumps_params={'ensure_ascii': False})

    # POST: Tạo môn học mới
    if not (request.user.is_authenticated and getattr(request.user, 'is_admin', False)):
        return _json_error("Chỉ Quản trị viên mới có quyền tạo môn học.", 403)

    name = request.POST.get('subject_name', '').strip()
    dept_id = request.POST.get('department_id')
    if not name or not dept_id:
        try:
            body = json.loads(request.body.decode('utf-8'))
            name = body.get('subject_name', '').strip()
            dept_id = body.get('department_id')
        except Exception:
            pass

    if not name or not dept_id:
        return _json_error("Tên môn và Khoa là bắt buộc.", 400)

    try:
        dept = Department.objects.get(pk=dept_id)
    except Department.DoesNotExist:
        return _json_error("Khoa không tồn tại.", 404)

    if Subject.objects.filter(subject_name__iexact=name, department=dept).exists():
        return _json_error(f"Môn học '{name}' đã tồn tại trong khoa này.", 400)

    sub = Subject.objects.create(subject_name=name, department=dept)
    return _json_ok({
        'id': sub.id,
        'subject_name': sub.subject_name,
        'department_id': dept.id,
        'department_name': dept.department_name,
    }, message="Tạo môn học thành công.", status=201)


# ─── CÂY THƯ MỤC (FOLDER TREE) API ──────────────────────────────────────────

@require_http_methods(["GET"])
def folder_tree_api(request, subject_id):
    """Lấy toàn bộ cây thư mục phân cấp cha - con của môn học."""
    subject = get_object_or_404(Subject, pk=subject_id)
    tree = get_folder_tree(subject_id=subject.id)
    return _json_ok({
        'subject_id': subject.id,
        'subject_name': subject.subject_name,
        'tree': tree,
    })


@csrf_exempt
@require_http_methods(["GET", "POST"])
def folder_api(request):
    """
    API Quản lý Thư mục:
    - GET: Danh sách thư mục (hỗ trợ lọc theo subject_id, parent_id, tìm kiếm)
    - POST: Tạo thư mục mới (Admin / Giảng viên)
    """
    if request.method == "GET":
        qs = Folder.objects.select_related('subject', 'parent_folder').annotate(
            doc_count=Count('documents')
        ).order_by('folder_name')

        subject_id = request.GET.get('subject_id')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)

        parent_id = request.GET.get('parent_id')
        if parent_id:
            if str(parent_id).lower() in ('root', 'null', 'none', '0'):
                qs = qs.filter(parent_folder__isnull=True)
            else:
                qs = qs.filter(parent_folder_id=parent_id)

        q = request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(folder_name__icontains=q)

        data = [{
            'id': f.id,
            'folder_id': f.id,
            'folder_name': f.folder_name,
            'subject_id': f.subject_id,
            'subject_name': f.subject.subject_name if f.subject else '',
            'parent_folder_id': f.parent_folder_id,
            'parent_folder_name': f.parent_folder.folder_name if f.parent_folder else None,
            'doc_count': f.doc_count,
            'breadcrumb': f.breadcrumb,
            'created_at': f.created_at.strftime('%Y-%m-%d %H:%M') if f.created_at else '',
        } for f in qs]

        payload = {
            'status': 'ok',
            'folders': data,
            'data': data,
            'total': len(data),
        }
        res = JsonResponse(payload, status=200, json_dumps_params={'ensure_ascii': False})
        res.data = payload
        return res

    # POST: Tạo thư mục hoặc thư mục con
    user = request.user
    if not (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))):
        return _json_error("Chỉ Quản trị viên hoặc Giảng viên mới có quyền tạo thư mục.", 403)

    name = request.POST.get('folder_name', '').strip()
    subject_id = request.POST.get('subject_id')
    parent_id = request.POST.get('parent_folder_id')

    if not name or not subject_id:
        try:
            body = json.loads(request.body.decode('utf-8'))
            name = body.get('folder_name', '').strip()
            subject_id = body.get('subject_id')
            parent_id = body.get('parent_folder_id')
        except Exception:
            pass

    if not name:
        return _json_error("Tên thư mục không được để trống.", 400)
    if not subject_id:
        return _json_error("Môn học (subject_id) là bắt buộc.", 400)

    try:
        folder = create_folder(name, int(subject_id), int(parent_id) if parent_id else None, user=user)
    except Exception as e:
        return _json_error(str(e), 400)

    return _json_ok({
        'id': folder.id,
        'folder_id': folder.id,
        'folder_name': folder.folder_name,
        'subject_id': folder.subject_id,
        'parent_folder_id': folder.parent_folder_id,
        'breadcrumb': folder.breadcrumb,
    }, message=f"Đã tạo thư mục '{folder.folder_name}'.", status=201)


folder_create_api = folder_api


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def folder_detail_api(request, pk):
    """
    API Chi tiết, Sửa hoặc Xóa thư mục:
    - GET: Chi tiết thư mục, đường dẫn breadcrumb, thư mục con và tài liệu bên trong
    - PATCH: Đổi tên thư mục, di chuyển thư mục cha (kiểm tra chống vòng lặp)
    - DELETE: Xóa thư mục an toàn (bảo toàn tài liệu, chuyển về thư mục gốc)
    """
    folder = get_object_or_404(
        Folder.objects.select_related('subject', 'parent_folder'),
        pk=pk
    )
    user = request.user

    if request.method == "GET":
        docs = folder.documents.select_related('uploader', 'subject')
        docs_data = [{
            'document_id': d.id,
            'id': d.id,
            'title': d.title,
            'status': d.status,
            'is_public': d.is_public,
            'view_count': d.view_count,
            'download_count': d.download_count,
            'uploader_name': d.uploader.full_name if (d.uploader and d.uploader.full_name) else (d.uploader.username if d.uploader else 'Ẩn danh'),
            'created_at': d.created_at.strftime('%Y-%m-%d %H:%M') if d.created_at else '',
        } for d in docs]

        subfolders = folder.subfolders.annotate(doc_count=Count('documents'))
        subfolders_data = [{
            'id': sf.id,
            'folder_id': sf.id,
            'folder_name': sf.folder_name,
            'doc_count': sf.doc_count,
        } for sf in subfolders]

        return _json_ok({
            'folder_id': folder.id,
            'id': folder.id,
            'folder_name': folder.folder_name,
            'subject_id': folder.subject_id,
            'subject_name': folder.subject.subject_name if folder.subject else '',
            'parent_folder_id': folder.parent_folder_id,
            'parent_folder_name': folder.parent_folder.folder_name if folder.parent_folder else None,
            'doc_count': folder.documents.count(),
            'breadcrumb': folder.breadcrumb,
            'subfolders': subfolders_data,
            'documents': docs_data,
        })

    # Quyền sửa / xóa: Yêu cầu Admin hoặc Giảng viên
    if not (user.is_authenticated and (getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False))):
        return _json_error("Chỉ Quản trị viên hoặc Giảng viên mới có quyền chỉnh sửa/xóa thư mục.", 403)

    if request.method == "PATCH":
        data = {}
        if request.body:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                pass
        if not data:
            data = request.POST

        new_name = data.get('folder_name', '').strip()
        new_parent_id = data.get('parent_folder_id')

        if new_name:
            folder.folder_name = new_name

        if new_parent_id is not None:
            if str(new_parent_id).lower() in ('null', 'none', '', '0'):
                folder.parent_folder = None
            else:
                new_parent_id = int(new_parent_id)
                if new_parent_id == folder.id:
                    return _json_error("Không thể đặt thư mục làm thư mục cha của chính nó.", 400)
                # Chống tạo vòng lặp cây thư mục
                curr = Folder.objects.filter(pk=new_parent_id).first()
                while curr:
                    if curr.id == folder.id:
                        return _json_error("Không thể tạo vòng lặp thư mục phân cấp.", 400)
                    curr = curr.parent_folder
                folder.parent_folder_id = new_parent_id

        folder.save()
        return _json_ok({
            'folder_id': folder.id,
            'folder_name': folder.folder_name,
            'subject_id': folder.subject_id,
            'parent_folder_id': folder.parent_folder_id,
            'breadcrumb': folder.breadcrumb,
        }, message=f"Đã cập nhật thư mục '{folder.folder_name}'.")

    if request.method == "DELETE":
        folder_name = folder.folder_name
        folder_id = folder.id
        # Bảo toàn tài liệu: chuyển tài liệu trong thư mục này về thư mục gốc (folder=None)
        folder.documents.all().update(folder=None)
        folder.delete()
        return _json_ok(
            data={'deleted_folder_id': folder_id},
            message=f"Đã xóa thư mục '{folder_name}'. Toàn bộ tài liệu bên trong đã được bảo toàn an toàn."
        )


@require_http_methods(["GET"])
def folder_documents_api(request, pk):
    """Lấy danh sách tài liệu thuộc thư mục cụ thể."""
    folder = get_object_or_404(Folder, pk=pk)
    docs = folder.documents.select_related('uploader', 'subject')
    data = [{
        'document_id': d.id,
        'id': d.id,
        'title': d.title,
        'description': d.description,
        'status': d.status,
        'is_public': d.is_public,
        'view_count': d.view_count,
        'download_count': d.download_count,
        'uploader_name': d.uploader.full_name if (d.uploader and d.uploader.full_name) else (d.uploader.username if d.uploader else 'Ẩn danh'),
        'created_at': d.created_at.strftime('%Y-%m-%d %H:%M') if d.created_at else '',
    } for d in docs]

    return _json_ok({
        'folder_id': folder.id,
        'folder_name': folder.folder_name,
        'breadcrumb': folder.breadcrumb,
        'documents': data,
        'total': len(data),
    })
