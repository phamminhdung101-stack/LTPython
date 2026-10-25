from django.contrib import admin
from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['role_id', 'role_name']
    search_fields = ['role_name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'full_name', 'role', 'department', 'student_class', 'created_at']
    list_filter = ['role', 'department']
    search_fields = ['username', 'full_name']
    ordering = ['user_id']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Thông tin đăng nhập', {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('full_name',)}),
        ('Phân quyền & Đơn vị', {'fields': ('role', 'department', 'student_class')}),
        ('Thời gian', {'fields': ('created_at',)}),
    )
