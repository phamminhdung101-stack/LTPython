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
    return JsonResponse(payload, status=status, json_dumps_params={'ensure_ascii': False})


def _json_ok(data=None, message: str = 'Thành công', status: int = 200) -> JsonResponse:
    payload = {'status': 'ok', 'message': message}
    if data is not None:
        payload['data'] = data
    return JsonResponse(payload, status=status, json_dumps_params={'ensure_ascii': False})


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
            'department_name': d.department_name,
            'class_count': d.class_count,
            'subject_count': d.subject_count,
        } for d in depts]
        return _json_ok(data)

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
            'class_name': c.class_name,
            'department_id': c.department_id,
            'department_name': c.department.department_name,
            'is_locked': c.is_locked,
        } for c in qs]
        return _json_ok(data)

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
            'subject_name': s.subject_name,
            'department_id': s.department_id,
            'department_name': s.department.department_name,
        } for s in qs]
        return _json_ok(data)

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
@require_http_methods(["POST"])
def folder_create_api(request):
    """Tạo thư mục hoặc thư mục con mới."""
    user = request.user if request.user.is_authenticated else None
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
        'folder_name': folder.folder_name,
        'subject_id': folder.subject_id,
        'parent_folder_id': folder.parent_folder_id,
    }, message=f"Đã tạo thư mục '{folder.folder_name}'.", status=201)
