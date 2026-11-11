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
    user_detail_api,
    user_toggle_status_api,
    role_api,
)

# Academics & Folders
from academics.api_views import (
    department_api,
    class_api,
    class_toggle_lock_api,
    subject_api,
    folder_tree_api,
    folder_api,
    folder_detail_api,
    folder_documents_api,
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
    submit_approval_api,
    create_version_api,
    version_list_api,
    version_restore_api,
    version_download_api,
    document_logs_api,
    activity_logs_api,
    tag_list_create_api,
    tag_detail_api,
    document_attach_tag_api,
    document_detach_tag_api,
    reindex_document_api,
    indexing_status_api,
    indexing_run_all_api,
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

# AI Search & RAG
from ai_search.api_views import (
    AIChatAPIView,
    AIQueryAPIView,
    AIHistoryListAPIView,
    AIHistoryDetailAPIView,
    AIDocumentProcessAPIView,
    AIDocumentStatusAPIView,
    AIDocumentSummaryAPIView,
    AIDocumentSuggestTagsAPIView,
)

app_name = 'api'

urlpatterns = [
    # ── 1. Auth & Users ──
    path('auth/login/', login_api, name='api_login'),
    path('auth/logout/', logout_api, name='api_logout'),
    path('auth/me/', current_user_api, name='api_current_user'),
    path('users/', user_api, name='api_users'),
    path('users/<int:pk>/', user_detail_api, name='api_user_detail'),
    path('roles/', role_api, name='api_roles'),
    path('users/<int:pk>/toggle-status/', user_toggle_status_api, name='api_user_toggle_status'),

    # ── 2. Academics & Organization ──
    path('departments/', department_api, name='api_departments'),
    path('classes/', class_api, name='api_classes'),
    path('classes/<int:pk>/toggle-lock/', class_toggle_lock_api, name='api_class_toggle_lock'),
    path('subjects/', subject_api, name='api_subjects'),
    path('subjects/<int:subject_id>/folders/tree/', folder_tree_api, name='api_folder_tree'),
    path('folders/', folder_api, name='api_folders'),
    path('folders/<int:pk>/', folder_detail_api, name='api_folder_detail'),
    path('folders/<int:pk>/documents/', folder_documents_api, name='api_folder_documents'),

    # ── 3. Documents & Cloudflare R2 Storage (Phần 2) ──
    path('documents/', document_list_api, name='api_document_list'),
    path('documents/upload/', upload_document_api, name='api_document_upload'),
    path('documents/<int:pk>/', document_detail_api, name='api_document_detail'),
    path('documents/<int:pk>/download/', download_document_api, name='api_document_download'),
    path('documents/<int:pk>/delete/', delete_document_api, name='api_document_delete_post'),
    path('documents/<int:pk>/', delete_document_api, name='api_document_delete'),
    path('activity-logs/', activity_logs_api, name='api_activity_logs'),

    # ── 4. Approval, Versioning & Audit Logs (Phần 3) ──
    path('documents/<int:pk>/approve/', approve_document_api, name='api_document_approve'),
    path('documents/<int:pk>/reject/', reject_document_api, name='api_document_reject'),
    path('documents/<int:pk>/submit-approval/', submit_approval_api, name='api_document_submit_approval'),
    path('documents/<int:pk>/versions/', version_list_api, name='api_document_versions'),
    path('documents/<int:pk>/versions/upload/', create_version_api, name='api_document_version_upload'),
    path('documents/<int:pk>/versions/<int:ver_id>/restore/', version_restore_api, name='api_document_version_restore'),
    path('documents/<int:pk>/versions/<int:ver_id>/download/', version_download_api, name='api_document_version_download'),
    path('documents/<int:pk>/logs/', document_logs_api, name='api_document_logs'),

    # ── 5. Tags & Categorization ──
    path('tags/', tag_list_create_api, name='api_tags'),
    path('tags/<int:pk>/', tag_detail_api, name='api_tag_detail'),
    path('documents/<int:pk>/tags/', document_attach_tag_api, name='api_document_attach_tag'),
    path('documents/<int:pk>/tags/<int:tag_id>/', document_detach_tag_api, name='api_document_detach_tag'),

    # ── 6. ACL & Permissions (Phần 3) ──
    path('documents/<int:doc_id>/permissions/', document_permissions_api, name='api_document_permissions'),
    path('documents/<int:doc_id>/permissions/<int:perm_id>/', delete_permission_api, name='api_delete_permission'),
    path('documents/<int:doc_id>/check-access/', check_document_access_api, name='api_check_document_access'),

    # ── 7. Document Indexing ──
    path('documents/<int:pk>/reindex/', reindex_document_api, name='api_document_reindex'),
    path('indexing/status/', indexing_status_api, name='api_indexing_status'),
    path('indexing/run/', indexing_run_all_api, name='api_indexing_run_all'),

    # ── 8. Dashboard Statistics ──
    path('dashboard/stats/', dashboard_stats_api, name='api_dashboard_stats'),

    # ── 9. AI Search & RAG ──
    path('ai/chat/', AIChatAPIView.as_view(), name='api_ai_chat'),
    path('ai/query/', AIQueryAPIView.as_view(), name='api_ai_query'),
    path('ai/history/', AIHistoryListAPIView.as_view(), name='api_ai_history'),
    path('ai/history/<int:query_id>/', AIHistoryDetailAPIView.as_view(), name='api_ai_history_detail'),
    path('ai/documents/<int:pk>/process/', AIDocumentProcessAPIView.as_view(), name='api_ai_document_process'),
    path('ai/documents/<int:pk>/status/', AIDocumentStatusAPIView.as_view(), name='api_ai_document_status'),
    path('ai/documents/<int:pk>/summary/', AIDocumentSummaryAPIView.as_view(), name='api_ai_document_summary'),
    path('ai/documents/<int:pk>/suggest-tags/', AIDocumentSuggestTagsAPIView.as_view(), name='api_ai_document_suggest_tags'),
]
