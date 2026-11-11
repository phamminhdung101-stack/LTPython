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

    # Real Chart 1: Xu hướng xem và tải 7 ngày gần nhất từ DocumentActivityLog
    chart_trends_7d = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DATE(created_at) AS log_date,
                   COUNT(*) FILTER (WHERE action = 'VIEW') AS views,
                   COUNT(*) FILTER (WHERE action = 'DOWNLOAD') AS downloads
            FROM document_activity_logs
            WHERE action IN ('VIEW', 'DOWNLOAD')
            GROUP BY log_date
            ORDER BY log_date DESC
            LIMIT 7
        """)
        rows_7d = cursor.fetchall()

    if rows_7d:
        rows_7d_sorted = sorted(rows_7d, key=lambda x: x[0])
        day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        for r_date, r_views, r_downloads in rows_7d_sorted:
            chart_trends_7d.append({
                'date': day_names[r_date.weekday()],
                'full_date': str(r_date),
                'views': r_views,
                'downloads': r_downloads,
            })
    else:
        chart_trends_7d = [
            {'date': 'Thứ 2', 'views': 0, 'downloads': 0},
            {'date': 'Thứ 3', 'views': 0, 'downloads': 0},
            {'date': 'Thứ 4', 'views': 0, 'downloads': 0},
            {'date': 'Thứ 5', 'views': 0, 'downloads': 0},
            {'date': 'Thứ 6', 'views': 0, 'downloads': 0},
            {'date': 'Thứ 7', 'views': 0, 'downloads': 0},
            {'date': 'Chủ nhật', 'views': 0, 'downloads': 0},
        ]

    # Real Chart 1 (phần 30 ngày): 4 tuần gần nhất
    chart_trends_30d = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN created_at >= NOW() - INTERVAL '7 days' THEN 'Tuần 4'
                    WHEN created_at >= NOW() - INTERVAL '14 days' THEN 'Tuần 3'
                    WHEN created_at >= NOW() - INTERVAL '21 days' THEN 'Tuần 2'
                    ELSE 'Tuần 1'
                END AS week_label,
                COUNT(*) FILTER (WHERE action = 'VIEW') AS views,
                COUNT(*) FILTER (WHERE action = 'DOWNLOAD') AS downloads
            FROM document_activity_logs
            WHERE action IN ('VIEW', 'DOWNLOAD')
              AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY week_label
        """)
        w_dict = {r[0]: {'views': r[1], 'downloads': r[2]} for r in cursor.fetchall()}

    for w_name in ['Tuần 1', 'Tuần 2', 'Tuần 3', 'Tuần 4']:
        info = w_dict.get(w_name, {'views': 0, 'downloads': 0})
        chart_trends_30d.append({
            'date': w_name,
            'views': info['views'],
            'downloads': info['downloads'],
        })

    # Real Chart 2: Top 5 tài liệu được tải và xem nhiều nhất từ bảng documents
    top_docs_qs = Document.objects.filter(status=Document.APPROVED).order_by('-download_count', '-view_count')[:5]
    top_documents = []
    for d_obj in top_docs_qs:
        short_title = d_obj.title[:20] + ("..." if len(d_obj.title) > 20 else "")
        top_documents.append({
            'id': d_obj.id,
            'name': short_title,
            'full_title': d_obj.title,
            'downloads': d_obj.download_count,
            'views': d_obj.view_count,
        })

    # Real Chart 3: Cơ cấu phân bổ học liệu thực tế từ DocumentVersion và Subject
    import os
    from documents.models import DocumentVersion
    category_colors = ["#3b82f6", "#f97316", "#10b981", "#a855f7", "#ef4444"]
    ext_labels = {
        '.pdf': 'Tài liệu PDF',
        '.docx': 'Tài liệu Word',
        '.pptx': 'Slide PowerPoint',
        '.txt': 'Văn bản thuần TXT',
    }
    ext_counts = {}
    for ver in DocumentVersion.objects.all():
        ext = os.path.splitext(ver.file)[1].lower() or '.txt'
        label = ext_labels.get(ext, f'File {ext.upper()}')
        ext_counts[label] = ext_counts.get(label, 0) + 1

    category_breakdown = []
    for idx, (lbl, cnt) in enumerate(sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:5]):
        category_breakdown.append({
            'name': lbl,
            'value': cnt,
            'fill': category_colors[idx % len(category_colors)],
        })

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
        'chart_trends_7d': chart_trends_7d,
        'chart_trends_30d': chart_trends_30d,
        'top_documents': top_documents,
        'category_breakdown': category_breakdown,
        'recent_activities': acts,
        'indexing': indexing_stats,
        'data': stats_summary,
    }
    res = JsonResponse(payload, status=200, json_dumps_params={'ensure_ascii': False})
    res.data = payload
    return res
