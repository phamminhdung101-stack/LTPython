from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Document, DocumentVersion, Tag, DocumentActivityLog
from academics.models import Subject, Department


# ---------------------------------------------------------------------------
# Student-facing views
# ---------------------------------------------------------------------------

@login_required
def home(request):
    recent_docs = Document.objects.filter(
        status=Document.APPROVED, is_public=True
    ).select_related('subject__department', 'uploader').prefetch_related('tags')[:6]

    context = {
        'recent_docs': recent_docs,
        'active_nav': 'home',
    }
    return render(request, 'student/home.html', context)


@login_required
def document_list(request):
    qs = Document.objects.filter(
        status=Document.APPROVED, is_public=True
    ).select_related('subject__department', 'uploader').prefetch_related('tags')

    q = request.GET.get('q', '').strip()
    subject_ids = request.GET.getlist('subjects')
    dept_id = request.GET.get('department', '')
    sort = request.GET.get('sort', 'newest')

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(subject__subject_name__icontains=q))
    if subject_ids:
        qs = qs.filter(subject_id__in=subject_ids)
    if dept_id:
        qs = qs.filter(subject__department_id=dept_id)

    if sort == 'downloads':
        qs = qs.order_by('-download_count')
    else:
        qs = qs.order_by('-created_at')

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page_obj,
        'subjects': Subject.objects.select_related('department').order_by('subject_name'),
        'departments': Department.objects.order_by('department_name'),
        'filters': {
            'q': q,
            'subjects': subject_ids,
            'department': dept_id,
            'sort': sort,
        },
        'total_count': qs.count(),
        'active_nav': 'document_list',
    }
    return render(request, 'student/document_list.html', context)


@login_required
def document_detail(request, pk):
    doc = get_object_or_404(
        Document.objects.select_related(
            'subject__department', 'uploader__role', 'uploader__department'
        ).prefetch_related('tags', 'versions__updated_by'),
        pk=pk,
        status=Document.APPROVED,
        is_public=True,
    )

    # Increment view count
    Document.objects.filter(pk=pk).update(view_count=doc.view_count + 1)

    # Log view activity
    DocumentActivityLog.objects.create(
        document=doc,
        user=request.user if request.user.is_authenticated else None,
        action='VIEW',
    )

    context = {
        'doc': doc,
        'versions': doc.versions.order_by('-version_number'),
        'latest_version': doc.versions.order_by('-version_number').first(),
        'active_nav': 'document_list',
    }
    return render(request, 'student/document_detail.html', context)


@login_required
def download_document(request, pk):
    doc = get_object_or_404(Document, pk=pk, status=Document.APPROVED)
    latest = doc.versions.order_by('-version_number').first()
    if not latest:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy file tải xuống.'}, status=404)

    Document.objects.filter(pk=pk).update(download_count=doc.download_count + 1)
    DocumentActivityLog.objects.create(document=doc, user=request.user, action='DOWNLOAD')

    return JsonResponse({'status': 'ok', 'url': latest.file.url, 'filename': latest.file.name})
