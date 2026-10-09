from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from accounts.models import User, Role
from academics.models import Department, Class, Subject
from documents.models import Document


def is_admin_or_lecturer(user):
    return user.is_authenticated and (user.is_admin or user.is_lecturer)


@login_required
@user_passes_test(is_admin_or_lecturer)
def index(request):
    stats = {
        'total_users': User.objects.filter(is_active=True).count(),
        'total_documents': Document.objects.filter(status=Document.APPROVED).count(),
        'pending_documents': Document.objects.filter(status=Document.PENDING).count(),
        'total_departments': Department.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_classes': Class.objects.count(),
    }

    recent_docs = Document.objects.select_related('uploader', 'subject').order_by('-created_at')[:5]
    recent_users = User.objects.select_related('role', 'department').order_by('-created_at')[:5]

    context = {
        'stats': stats,
        'recent_docs': recent_docs,
        'recent_users': recent_users,
        'active_nav': 'dashboard',
    }
    return render(request, 'dashboard/index.html', context)
