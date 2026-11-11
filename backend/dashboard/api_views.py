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
    Chỉ Quản trị viên và Giảng viên được phép truy cập.
    """
    user = request.user
    if user.is_authenticated and getattr(user, 'is_student', False):
        return JsonResponse({'status': 'error', 'message': 'Chỉ Quản trị viên và Giảng viên mới có quyền xem thống kê.'}, status=403)

    from documents.models import DocumentActivityLog
    total_docs = Document.objects.count()
    approved_docs = Document.objects.filter(status=Document.APPROVED).count()
    pending_docs = Document.objects.filter(status=Document.PENDING).count()
    rejected_docs = Document.objects.filter(status=Document.REJECTED).count()

    aggregates = Document.objects.aggregate(
        total_downloads=Sum('download_count'),
        total_views=Sum('view_count'),
    )
    total_views = aggregates.get('total_views') or 0
    total_downloads = aggregates.get('total_downloads') or 0

    total_users = User.objects.filter(is_active=True).count()
    total_students = User.objects.filter(role__role_name=Role.STUDENT, is_active=True).count()
    total_lecturers = User.objects.filter(role__role_name=Role.LECTURER, is_active=True).count()
    total_admins = User.objects.filter(role__role_name=Role.ADMIN, is_active=True).count()

    from documents.models import Folder, Tag
    from documents.indexing_service import get_indexing_stats
    indexing_stats = get_indexing_stats()

    # Subject breakdown
    subject_stats = []
    for s in Subject.objects.annotate(doc_count=Count('documents')).order_by('-doc_count')[:6]:
        subject_stats.append({
            'subject_id': s.id,
            'subject_name': s.subject_name,
            'doc_count': s.doc_count,
        })

    # Monthly upload trends (Last 6 months)
    from django.db import connection
    monthly_trends = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TO_CHAR(created_at, 'YYYY-MM') AS month_str, COUNT(*) AS count
            FROM documents
            GROUP BY TO_CHAR(created_at, 'YYYY-MM')
            ORDER BY month_str DESC
            LIMIT 6
        """)
        for row in cursor.fetchall():
            monthly_trends.append({'month': row[0], 'count': row[1]})
    monthly_trends.reverse()

    # Recent activities from DocumentActivityLog
    days = request.GET.get('days')
    logs_qs = DocumentActivityLog.objects.select_related('document', 'user').order_by('-created_at')
    if days and days.isdigit():
        from django.utils import timezone
        from datetime import timedelta
        since = timezone.now() - timedelta(days=int(days))
        logs_qs = logs_qs.filter(created_at__gte=since)

    recent_logs = logs_qs[:10]
    acts = []
    for log in recent_logs:
        acts.append({
            'log_id': log.id,
            'document_id': log.document_id,
            'document_title': log.document.title if log.document else 'Tài liệu học phần',
            'user_name': log.user.full_name if log.user else 'Người dùng',
            'user_role': log.user.role.role_name if (log.user and log.user.role) else 'Sinh viên',
            'action': log.action,
            'description': log.description,
            'created_at': log.created_at.strftime('%Y-%m-%d %H:%M') if log.created_at else '',
        })

    stats_summary = {
        'total_documents': total_docs,
        'approved_documents': approved_docs,
        'pending_documents': pending_docs,
        'rejected_documents': rejected_docs,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'total_users': total_users,
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_admins': total_admins,
        'total_departments': Department.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_classes': Class.objects.count(),
        'total_folders': Folder.objects.count(),
        'total_tags': Tag.objects.count(),
        'indexing': indexing_stats,
    }

    payload = {
        'status': 'ok',
        'message': 'Thành công',
        'stats': stats_summary,
        'subject_breakdown': subject_stats,
        'monthly_trends': monthly_trends,
        'recent_activities': acts,
        'indexing': indexing_stats,
        'data': stats_summary,
    }
    res = JsonResponse(payload, status=200, json_dumps_params={'ensure_ascii': False})
    res.data = payload
    return res
