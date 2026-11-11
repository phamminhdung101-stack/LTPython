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


def _get_authenticated_user(request):
    # Ưu tiên xác thực JWT Bearer token nếu có header hoặc query param
    auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
    has_token = (auth_header and 'Bearer' in auth_header) or (hasattr(request, 'GET') and 'token' in request.GET)
    if has_token:
        try:
            from .authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            auth_res = jwt_auth.authenticate(request)
            if auth_res:
                request.user = auth_res[0]
                return auth_res[0]
        except Exception:
            pass

    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        return user
    return None


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

    if not user.is_active or (user.student_class and getattr(user.student_class, 'is_locked', False)):
        return _json_error("Tài khoản của bạn đã bị vô hiệu hóa hoặc lớp học tạm thời bị khóa.", 403)

    login(request, user)

    from .authentication import generate_jwt_token
    token = generate_jwt_token(user)

    user_payload = {
        'user_id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role_name,
        'role_name': user.role_name,
        'is_admin': user.is_admin,
        'is_lecturer': user.is_lecturer,
        'is_student': user.is_student,
        'department_id': user.department_id,
        'department_name': user.department.department_name if user.department else None,
        'class_id': user.student_class_id,
        'class_name': user.student_class.class_name if user.student_class else None,
    }
    payload = {
        'status': 'ok',
        'message': f"Đăng nhập thành công với vai trò {user.role_name}.",
        'user': user_payload,
        'data': user_payload,
        'token': token,
    }
    res = JsonResponse(payload, status=200, json_dumps_params={'ensure_ascii': False})
    res.data = payload
    return res


@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    logout(request)
    return _json_ok(message="Đã đăng xuất thành công.")


@require_http_methods(["GET"])
def current_user_api(request):
    user = _get_authenticated_user(request)
    if not user:
        return _json_error("Chưa đăng nhập.", 401)

    user_payload = {
        'user_id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'role': user.role_name,
        'role_name': user.role_name,
        'department_name': user.department.department_name if user.department else None,
        'class_name': user.student_class.class_name if user.student_class else None,
    }
    payload = {
        'status': 'ok',
        'user': user_payload,
        'data': user_payload,
    }
    res = JsonResponse(payload, status=200, json_dumps_params={'ensure_ascii': False})
    res.data = payload
    return res


# ─── USER MANAGEMENT API (ADMIN) ─────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def user_api(request):
    user = _get_authenticated_user(request)

    # GET: Danh sách người dùng (chỉ cho phép ADMIN)
    if request.method == "GET":
        if not (user and getattr(user, 'is_admin', False)):
            return _json_error("Chỉ Quản trị viên mới có quyền xem danh sách người dùng.", 403)
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
            'id': u.id,
            'username': u.username,
            'full_name': u.full_name,
            'role': u.role_name,
            'role_name': u.role_name,
            'department_id': u.department_id,
            'department_name': u.department.department_name if u.department else None,
            'department': {
                'department_id': u.department_id,
                'department_name': u.department.department_name if u.department else '',
            } if u.department else {},
            'class_id': u.student_class_id,
            'class_name': u.student_class.class_name if u.student_class else None,
            'student_class': {
                'class_id': u.student_class_id,
                'class_name': u.student_class.class_name if u.student_class else '',
            } if u.student_class else {},
            'is_active': u.is_active,
            'created_at': u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else '',
        } for u in qs[:100]]

        return JsonResponse({
            'status': 'ok',
            'users': data,
            'data': data,
            'total': len(data),
        }, status=200, json_dumps_params={'ensure_ascii': False})

    # POST: Tạo người dùng mới
    if not (user and getattr(user, 'is_admin', False)):
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
@require_http_methods(["GET", "PATCH", "PUT", "DELETE"])
def user_detail_api(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    user = _get_authenticated_user(request)

    if request.method in ("PATCH", "PUT"):
        data = {}
        if request.body:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                pass
        if not data:
            data = request.POST

        # Chỉ Admin mới được phép đổi vai trò role_id
        is_admin = user and getattr(user, 'is_admin', False)
        if 'role_id' in data and is_admin:
            target_user.role_id = data['role_id']
        if 'full_name' in data and (is_admin or (user and user.id == target_user.id)):
            target_user.full_name = data['full_name']
        if 'email' in data and (is_admin or (user and user.id == target_user.id)):
            target_user.email = data['email']
        target_user.save()
        return _json_ok({'user_id': target_user.id, 'full_name': target_user.full_name, 'role_id': target_user.role_id})

    if request.method == "DELETE":
        if not (user and getattr(user, 'is_admin', False)):
            return _json_error("Chỉ Admin mới có quyền xóa người dùng.", 403)
        target_user.delete()
        return _json_ok(message="Đã xóa người dùng thành công.")

    return _json_ok({
        'user_id': target_user.id,
        'username': target_user.username,
        'full_name': target_user.full_name,
        'role': target_user.role_name,
    })


@csrf_exempt
@require_http_methods(["GET"])
def role_api(request):
    roles = Role.objects.all().order_by('id')
    data = [{
        'id': r.id,
        'role_id': r.id,
        'role_name': r.role_name,
        'name': r.get_role_name_display(),
    } for r in roles]
    return JsonResponse({
        'status': 'ok',
        'roles': data,
        'data': data,
        'total': len(data),
    }, status=200, json_dumps_params={'ensure_ascii': False})


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
