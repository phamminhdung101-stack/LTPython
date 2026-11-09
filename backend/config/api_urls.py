"""
DocUni - API URL Routing (Phần 2 & Phần 3)
Tất cả các endpoint REST API được tập trung tại đây dưới tiền tố /api/
"""

from django.urls import path

# Accounts & Auth
from accounts.api_views import (
    login_api,
    logout_api,
    current_user_api,
    user_api,
    user_toggle_status_api,
)

# Academics & Folders
from academics.api_views import (
    department_api,
    class_api,
    class_toggle_lock_api,
    subject_api,
    folder_tree_api,
    folder_create_api,
)

# Documents & Cloudflare R2
from documents.api_views import (
    upload_document_api,
    download_document_api,
    delete_document_api,
    document_list_api,
    document_detail_api,
    approve_document_api,
    reject_document_api,
    create_version_api,
    version_list_api,
    document_logs_api,
)

# Document Permissions (ACL)
from permissions.api_views import (
    document_permissions_api,
    delete_permission_api,
    check_document_access_api,
)

# Dashboard Stats
from dashboard.api_views import (
    dashboard_stats_api,
)

app_name = 'api'

urlpatterns = [
    # ── 1. Auth & Users ──
    path('auth/login/', login_api, name='api_login'),
    path('auth/logout/', logout_api, name='api_logout'),
    path('auth/me/', current_user_api, name='api_current_user'),
    path('users/', user_api, name='api_users'),
    path('users/<int:pk>/toggle-status/', user_toggle_status_api, name='api_user_toggle_status'),

    # ── 2. Academics & Organization ──
    path('departments/', department_api, name='api_departments'),
    path('classes/', class_api, name='api_classes'),
    path('classes/<int:pk>/toggle-lock/', class_toggle_lock_api, name='api_class_toggle_lock'),
    path('subjects/', subject_api, name='api_subjects'),
    path('subjects/<int:subject_id>/folders/tree/', folder_tree_api, name='api_folder_tree'),
    path('folders/', folder_create_api, name='api_folder_create'),

    # ── 3. Documents & Cloudflare R2 Storage (Phần 2) ──
    path('documents/', document_list_api, name='api_document_list'),
    path('documents/upload/', upload_document_api, name='api_document_upload'),
    path('documents/<int:pk>/', document_detail_api, name='api_document_detail'),
    path('documents/<int:pk>/download/', download_document_api, name='api_document_download'),
    path('documents/<int:pk>/delete/', delete_document_api, name='api_document_delete_post'),
    path('documents/<int:pk>/', delete_document_api, name='api_document_delete'),

    # ── 4. Approval, Versioning & Audit Logs (Phần 3) ──
    path('documents/<int:pk>/approve/', approve_document_api, name='api_document_approve'),
    path('documents/<int:pk>/reject/', reject_document_api, name='api_document_reject'),
    path('documents/<int:pk>/versions/', version_list_api, name='api_document_versions'),
    path('documents/<int:pk>/versions/upload/', create_version_api, name='api_document_version_upload'),
    path('documents/<int:pk>/logs/', document_logs_api, name='api_document_logs'),

    # ── 5. ACL & Permissions (Phần 3) ──
    path('documents/<int:doc_id>/permissions/', document_permissions_api, name='api_document_permissions'),
    path('documents/<int:doc_id>/permissions/<int:perm_id>/', delete_permission_api, name='api_delete_permission'),
    path('documents/<int:doc_id>/check-access/', check_document_access_api, name='api_check_document_access'),

    # ── 6. Dashboard Statistics ──
    path('dashboard/stats/', dashboard_stats_api, name='api_dashboard_stats'),
]
