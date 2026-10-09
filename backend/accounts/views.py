from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q

from .models import User, Role
from academics.models import Department, Class


def is_admin(user):
    return user.is_authenticated and user.is_admin


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# ---------------------------------------------------------------------------
# User Management (admin only)
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def user_list(request):
    qs = User.objects.select_related('role', 'department', 'student_class').order_by('-created_at')

    q = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '')
    dept_filter = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')

    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(username__icontains=q) |
            Q(email__icontains=q)
        )
    if role_filter:
        qs = qs.filter(role__role_name=role_filter)
    if dept_filter:
        qs = qs.filter(department_id=dept_filter)
    if status_filter == 'ACTIVE':
        qs = qs.filter(is_active=True)
    elif status_filter == 'INACTIVE':
        qs = qs.filter(is_active=False)

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'roles': Role.objects.all(),
        'departments': Department.objects.all(),
        'filters': {
            'q': q,
            'role': role_filter,
            'department': dept_filter,
            'status': status_filter,
        },
        'total_count': qs.count(),
        'active_nav': 'users',
    }
    return render(request, 'accounts/user_management.html', context)


@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        role_name = request.POST.get('role', '')
        dept_id = request.POST.get('department', '') or None
        class_id = request.POST.get('student_class', '') or None
        is_active = request.POST.get('is_active', 'true') == 'true'

        errors = {}
        if not full_name:
            errors['full_name'] = 'Họ tên không được để trống.'
        if not username:
            errors['username'] = 'Username không được để trống.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username đã tồn tại.'
        if email and User.objects.filter(email=email).exists():
            errors['email'] = 'Email đã được sử dụng.'
        if not password:
            errors['password'] = 'Mật khẩu không được để trống.'

        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        role = Role.objects.get(role_name=role_name) if role_name else None
        user = User(
            username=username,
            full_name=full_name,
            email=email,
            role=role,
            department_id=dept_id,
            student_class_id=class_id,
            is_active=is_active,
        )
        user.set_password(password)
        user.save()
        messages.success(request, f'Đã tạo người dùng {full_name}.')
        return JsonResponse({'status': 'ok', 'message': 'Thêm người dùng thành công.'})

    return JsonResponse({'status': 'error'}, status=405)


@login_required
@user_passes_test(is_admin)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        role_name = request.POST.get('role', '')
        dept_id = request.POST.get('department', '') or None
        class_id = request.POST.get('student_class', '') or None
        is_active = request.POST.get('is_active', 'true') == 'true'

        errors = {}
        if not full_name:
            errors['full_name'] = 'Họ tên không được để trống.'
        if email and User.objects.filter(email=email).exclude(pk=pk).exists():
            errors['email'] = 'Email đã được sử dụng.'

        if errors:
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

        user.full_name = full_name
        user.email = email
        user.role = Role.objects.get(role_name=role_name) if role_name else None
        user.department_id = dept_id
        user.student_class_id = class_id
        user.is_active = is_active
        if password:
            user.set_password(password)
        user.save()
        messages.success(request, f'Đã cập nhật người dùng {full_name}.')
        return JsonResponse({'status': 'ok', 'message': 'Cập nhật thành công.'})

    # GET – return JSON data for pre-filling the modal
    return JsonResponse({
        'id': user.pk,
        'full_name': user.full_name,
        'username': user.username,
        'email': user.email,
        'role': user.role.role_name if user.role else '',
        'department': user.department_id or '',
        'student_class': user.student_class_id or '',
        'is_active': user.is_active,
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        return JsonResponse({'status': 'error', 'message': 'Không thể xóa tài khoản đang đăng nhập.'}, status=400)
    name = user.full_name
    user.delete()
    messages.success(request, f'Đã xóa người dùng {name}.')
    return JsonResponse({'status': 'ok', 'message': 'Xóa người dùng thành công.'})


@login_required
@user_passes_test(is_admin)
@require_POST
def user_toggle_status(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        return JsonResponse({'status': 'error', 'message': 'Không thể tự khóa tài khoản của mình.'}, status=400)
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    state = 'Active' if user.is_active else 'Inactive'
    return JsonResponse({'status': 'ok', 'is_active': user.is_active, 'message': f'Tài khoản đã được đặt thành {state}.'})
