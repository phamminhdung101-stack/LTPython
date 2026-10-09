from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count

from .models import Department, Class, Subject


def is_admin(user):
    return user.is_authenticated and user.is_admin


# ---------------------------------------------------------------------------
# Organization management page (single page, 3 tabs)
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def organization_management(request):
    departments = Department.objects.annotate(
        class_count=Count('classes', distinct=True),
        subject_count=Count('subjects', distinct=True),
    ).order_by('department_name')

    classes = Class.objects.select_related('department').order_by('class_name')
    subjects = Subject.objects.select_related('department').order_by('subject_name')

    context = {
        'departments': departments,
        'classes': classes,
        'subjects': subjects,
        'active_nav': 'organization',
    }
    return render(request, 'academics/organization_management.html', context)


# ---------------------------------------------------------------------------
# Department CRUD (JSON API consumed by the template JS)
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def department_create(request):
    if request.method == 'POST':
        name = request.POST.get('department_name', '').strip()
        if not name:
            return JsonResponse({'status': 'error', 'errors': {'department_name': 'Tên khoa không được để trống.'}}, status=400)
        if Department.objects.filter(department_name__iexact=name).exists():
            return JsonResponse({'status': 'error', 'errors': {'department_name': 'Tên khoa đã tồn tại.'}}, status=400)
        dept = Department.objects.create(department_name=name)
        return JsonResponse({'status': 'ok', 'id': dept.pk, 'department_name': dept.department_name})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
@user_passes_test(is_admin)
def department_update(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('department_name', '').strip()
        if not name:
            return JsonResponse({'status': 'error', 'errors': {'department_name': 'Tên khoa không được để trống.'}}, status=400)
        if Department.objects.filter(department_name__iexact=name).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'errors': {'department_name': 'Tên khoa đã tồn tại.'}}, status=400)
        dept.department_name = name
        dept.save()
        return JsonResponse({'status': 'ok', 'id': dept.pk, 'department_name': dept.department_name})
    return JsonResponse({'id': dept.pk, 'department_name': dept.department_name})


@login_required
@user_passes_test(is_admin)
@require_POST
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    dept.delete()
    return JsonResponse({'status': 'ok', 'message': 'Đã xóa khoa.'})


# ---------------------------------------------------------------------------
# Class CRUD
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def class_create(request):
    if request.method == 'POST':
        name = request.POST.get('class_name', '').strip()
        dept_id = request.POST.get('department', '')
        if not name:
            return JsonResponse({'status': 'error', 'errors': {'class_name': 'Tên lớp không được để trống.'}}, status=400)
        if not dept_id:
            return JsonResponse({'status': 'error', 'errors': {'department': 'Vui lòng chọn khoa.'}}, status=400)
        if Class.objects.filter(class_name__iexact=name).exists():
            return JsonResponse({'status': 'error', 'errors': {'class_name': 'Tên lớp đã tồn tại.'}}, status=400)
        cls = Class.objects.create(class_name=name, department_id=dept_id)
        return JsonResponse({'status': 'ok', 'id': cls.pk, 'class_name': cls.class_name, 'department': cls.department.department_name})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
@user_passes_test(is_admin)
def class_update(request, pk):
    cls = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('class_name', '').strip()
        dept_id = request.POST.get('department', '')
        is_locked = request.POST.get('is_locked', 'false') == 'true'
        if not name:
            return JsonResponse({'status': 'error', 'errors': {'class_name': 'Tên lớp không được để trống.'}}, status=400)
        if Class.objects.filter(class_name__iexact=name).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'errors': {'class_name': 'Tên lớp đã tồn tại.'}}, status=400)
        cls.class_name = name
        cls.department_id = dept_id or cls.department_id
        cls.is_locked = is_locked
        cls.save()
        return JsonResponse({'status': 'ok', 'id': cls.pk, 'class_name': cls.class_name, 'department': cls.department.department_name})
    return JsonResponse({'id': cls.pk, 'class_name': cls.class_name, 'department_id': cls.department_id, 'is_locked': cls.is_locked})


@login_required
@user_passes_test(is_admin)
@require_POST
def class_delete(request, pk):
    cls = get_object_or_404(Class, pk=pk)
    cls.delete()
    return JsonResponse({'status': 'ok', 'message': 'Đã xóa lớp.'})


# ---------------------------------------------------------------------------
# Subject CRUD
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def subject_create(request):
    if request.method == 'POST':
        name = request.POST.get('subject_name', '').strip()
        dept_id = request.POST.get('department', '')
        if not name:
            return JsonResponse({'status': 'error', 'errors': {'subject_name': 'Tên môn học không được để trống.'}}, status=400)
        if not dept_id:
            return JsonResponse({'status': 'error', 'errors': {'department': 'Vui lòng chọn khoa.'}}, status=400)
        if Subject.objects.filter(subject_name__iexact=name, department_id=dept_id).exists():
            return JsonResponse({'status': 'error', 'errors': {'subject_name': 'Môn học đã tồn tại trong khoa này.'}}, status=400)
        subj = Subject.objects.create(subject_name=name, department_id=dept_id)
        return JsonResponse({'status': 'ok', 'id': subj.pk, 'subject_name': subj.subject_name, 'department': subj.department.department_name})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
@user_passes_test(is_admin)
def subject_update(request, pk):
    subj = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('subject_name', '').strip()
        dept_id = request.POST.get('department', '')
        if not name:
            return JsonResponse({'status': 'error', 'errors': {'subject_name': 'Tên môn học không được để trống.'}}, status=400)
        if Subject.objects.filter(subject_name__iexact=name, department_id=dept_id).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'errors': {'subject_name': 'Môn học đã tồn tại trong khoa này.'}}, status=400)
        subj.subject_name = name
        subj.department_id = dept_id or subj.department_id
        subj.save()
        return JsonResponse({'status': 'ok', 'id': subj.pk, 'subject_name': subj.subject_name, 'department': subj.department.department_name})
    return JsonResponse({'id': subj.pk, 'subject_name': subj.subject_name, 'department_id': subj.department_id})


@login_required
@user_passes_test(is_admin)
@require_POST
def subject_delete(request, pk):
    subj = get_object_or_404(Subject, pk=pk)
    subj.delete()
    return JsonResponse({'status': 'ok', 'message': 'Đã xóa môn học.'})
