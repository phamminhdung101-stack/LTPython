"""
DocUni - REST API Báo Cáo Thống Kê Dashboard
Phần 3:
- GET /api/dashboard/stats/ : Tổng quan số liệu toàn hệ thống
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum

from accounts.models import User, Role
from academics.models import Department, Class, Subject
from documents.models import Document


def _json_ok(data=None, message: str = 'Thành công') -> JsonResponse:
    return JsonResponse({'status': 'ok', 'message': message, 'data': data}, json_dumps_params={'ensure_ascii': False})


@require_http_methods(["GET"])
def dashboard_stats_api(request):
    """
    API Trả về toàn bộ số liệu thống kê quản trị.
    """
    total_docs = Document.objects.count()
    approved_docs = Document.objects.filter(status=Document.APPROVED).count()
    pending_docs = Document.objects.filter(status=Document.PENDING).count()
    rejected_docs = Document.objects.filter(status=Document.REJECTED).count()

    aggregates = Document.objects.aggregate(
        total_downloads=Sum('download_count'),
        total_views=Sum('view_count'),
    )

    total_users = User.objects.filter(is_active=True).count()
    total_students = User.objects.filter(role__role_name=Role.STUDENT, is_active=True).count()
    total_lecturers = User.objects.filter(role__role_name=Role.LECTURER, is_active=True).count()

    dept_stats = []
    for d in Department.objects.annotate(
        class_cnt=Count('classes', distinct=True),
        subject_cnt=Count('subjects', distinct=True),
    ):
        doc_cnt = Document.objects.filter(subject__department=d).count()
        dept_stats.append({
            'department_id': d.id,
            'department_name': d.department_name,
            'class_count': d.class_cnt,
            'subject_count': d.subject_cnt,
            'document_count': doc_cnt,
        })

    data = {
        'documents': {
            'total': total_docs,
            'approved': approved_docs,
            'pending': pending_docs,
            'rejected': rejected_docs,
            'total_downloads': aggregates['total_downloads'] or 0,
            'total_views': aggregates['total_views'] or 0,
        },
        'users': {
            'total_active': total_users,
            'students': total_students,
            'lecturers': total_lecturers,
        },
        'academics': {
            'departments': Department.objects.count(),
            'classes': Class.objects.count(),
            'subjects': Subject.objects.count(),
            'departments_breakdown': dept_stats,
        }
    }
    return _json_ok(data)
