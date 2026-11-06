"""
DocUni - REST API Quản Lý Tài Khoản & Người Dùng
Phần 3:
- POST /api/auth/login/ : Đăng nhập xác thực và trả về vai trò & quyền hạn
- POST /api/auth/logout/ : Đăng xuất
- GET  /api/auth/me/ : Lấy thông tin tài khoản hiện tại
- GET  /api/users/ : Danh sách người dùng (Admin)
- POST /api/users/ : Thêm người dùng mới kèm gán Lớp/Khoa/Vai trò
- PATCH /api/users/<id>/toggle-status/ : Khóa/kích hoạt tài khoản người dùng
"""

import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import User, Role
from academics.models import Department, Class


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


# ─── AUTHENTICATION API ──────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """
    API Đăng nhập:
    Hỗ trợ nhận cả application/json và multipart/form-data.
    """
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    if not username or not password:
        try:
            body = json.loads(request.body.decode('utf-8'))
            username = body.get('username', '').strip()
            password = body.get('password', '')
        except Exception:
            pass

    if not username or not password:
        return _json_error("Vui lòng cung cấp 'username' và 'password'.", 400)

    user = authenticate(request, username=username, password=password)
    if not user:
        return _json_error("Tên đăng nhập hoặc mật khẩu không chính xác.", 401)

    if not user.is_active:
        return _json_error("Tài khoản của bạn đã bị vô hiệu hóa hoặc khóa.", 403)

    login(request, user)

    return _json_ok({
        'user_id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role_name,
        'is_admin': user.is_admin,
        'is_lecturer': user.is_lecturer,
        'is_student': user.is_student,
        'department_id': user.department_id,
        'department_name': user.department.department_name if user.department else None,
        'class_id': user.student_class_id,
        'class_name': user.student_class.class_name if user.student_class else None,
    }, message=f"Đăng nhập thành công với vai trò {user.role_name}.")


@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    logout(request)
    return _json_ok(message="Đã đăng xuất thành công.")


@require_http_methods(["GET"])
def current_user_api(request):
    user = request.user
    if not user.is_authenticated:
        return _json_error("Chưa đăng nhập.", 401)

    return _json_ok({
        'user_id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role_name,
        'department_name': user.department.department_name if user.department else None,
        'class_name': user.student_class.class_name if user.student_class else None,
    })


# ─── USER MANAGEMENT API (ADMIN) ─────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def user_api(request):
    # GET: Danh sách người dùng
    if request.method == "GET":
        qs = User.objects.select_related('role', 'department', 'student_class').order_by('-created_at')

        q = request.GET.get('q', '').strip()
        role = request.GET.get('role', '').strip()
        dept_id = request.GET.get('department_id')
        class_id = request.GET.get('class_id')

        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(username__icontains=q))
        if role:
            qs = qs.filter(role__role_name=role.upper())
        if dept_id:
            qs = qs.filter(department_id=dept_id)
        if class_id:
            qs = qs.filter(student_class_id=class_id)

        data = [{
            'user_id': u.id,
            'username': u.username,
            'full_name': u.full_name,
            'role': u.role_name,
            'department_id': u.department_id,
            'department_name': u.department.department_name if u.department else None,
            'class_id': u.student_class_id,
            'class_name': u.student_class.class_name if u.student_class else None,
            'is_active': u.is_active,
            'created_at': u.created_at.strftime('%Y-%m-%d %H:%M'),
        } for u in qs[:100]]

        return _json_ok(data)

    # POST: Tạo người dùng mới
    if not (request.user.is_authenticated and getattr(request.user, 'is_admin', False)):
        return _json_error("Chỉ Quản trị viên mới có quyền tạo người dùng.", 403)

    data = request.POST
    if not data:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}

    username = data.get('username', '').strip()
    full_name = data.get('full_name', '').strip()
    password = data.get('password', '').strip() or '123456'
    role_name = (data.get('role') or 'STUDENT').upper()
    dept_id = data.get('department_id')
    class_id = data.get('class_id')

    if not username or not full_name:
        return _json_error("Vui lòng nhập 'username' và 'full_name'.", 400)

    if User.objects.filter(username__iexact=username).exists():
        return _json_error(f"Username '{username}' đã được sử dụng.", 400)

    role, _ = Role.objects.get_or_create(role_name=role_name)
    dept = Department.objects.filter(pk=dept_id).first() if dept_id else None
    student_class = Class.objects.filter(pk=class_id).first() if class_id else None

    user = User.objects.create_user(
        username=username,
        full_name=full_name,
        role=role,
        password=password,
        department=dept,
        student_class=student_class,
    )

    return _json_ok({
        'user_id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role_name,
        'department_name': dept.department_name if dept else None,
        'class_name': student_class.class_name if student_class else None,
    }, message=f"Đã tạo người dùng '{user.full_name}' thành công.", status=201)


@csrf_exempt
@require_http_methods(["PATCH", "POST"])
def user_toggle_status_api(request, pk):
    """Khóa hoặc kích hoạt tài khoản."""
    if not (request.user.is_authenticated and getattr(request.user, 'is_admin', False)):
        return _json_error("Chỉ Quản trị viên mới có quyền khóa/mở khóa tài khoản.", 403)

    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    st = "kích hoạt" if user.is_active else "khóa"
    return _json_ok({
        'user_id': user.id,
        'username': user.username,
        'is_active': user.is_active,
    }, message=f"Đã {st} tài khoản {user.username}.")
