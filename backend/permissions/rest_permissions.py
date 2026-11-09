"""
Phân quyền theo vai trò (Role-Based Access Control - RBAC) sử dụng Django REST Framework.
Dựa trên bảng roles (ADMIN, LECTURER, STUDENT) trong PostgreSQL.
"""

from rest_framework import permissions
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from accounts.models import Role


class IsAuthenticatedCustom(permissions.BasePermission):
    """Bắt buộc người dùng phải đăng nhập hợp lệ."""
    message = 'Vui lòng đăng nhập để thực hiện thao tác này.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            raise NotAuthenticated('Vui lòng đăng nhập để thực hiện thao tác này.')
        return True


class IsAdminUserRole(permissions.BasePermission):
    """Chỉ dành cho tài khoản có vai trò ADMIN."""
    message = 'Bạn không có quyền quản trị viên (ADMIN) để thực hiện thao tác này.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return bool(request.user.is_admin)


class IsLecturerUserRole(permissions.BasePermission):
    """Chỉ dành cho tài khoản có vai trò LECTURER."""
    message = 'Thao tác này chỉ dành riêng cho Giảng viên (LECTURER).'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return bool(request.user.is_lecturer)


class IsStudentUserRole(permissions.BasePermission):
    """Chỉ dành cho tài khoản có vai trò STUDENT."""
    message = 'Thao tác này chỉ dành cho Sinh viên (STUDENT).'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return bool(request.user.is_student)


class IsLecturerOrAdmin(permissions.BasePermission):
    """Dành cho Giảng viên hoặc Quản trị viên (kiểm duyệt, quản lý học liệu)."""
    message = 'Bạn cần có quyền Giảng viên hoặc Quản trị viên để thực hiện thao tác này.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return bool(request.user.is_admin or request.user.is_lecturer)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Kiểm tra quyền trên từng đối tượng dữ liệu:
    Chủ sở hữu (uploader/user) hoặc Quản trị viên mới có quyền sửa/xóa.
    """
    message = 'Bạn không có quyền chỉnh sửa tài nguyên của người dùng khác.'

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_admin:
            return True

        # Kiểm tra theo thuộc tính người tạo (uploader hoặc user)
        owner = getattr(obj, 'uploader', None) or getattr(obj, 'user', None)
        if owner and owner == request.user:
            return True

        # Nếu là tài liệu của chính sinh viên
        if hasattr(obj, 'user_id') and obj.user_id == request.user.user_id:
            return True

        return False
