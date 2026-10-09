from django.contrib import admin
from .models import Department, Class, Subject


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department_name']
    search_fields = ['department_name']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'department', 'is_locked']
    list_filter = ['department', 'is_locked']
    search_fields = ['class_name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject_name', 'department']
    list_filter = ['department']
    search_fields = ['subject_name']
