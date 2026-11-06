"""
URL configuration for DocUni Backend.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.api_views import (
    HealthCheckAPIView,
    LoginAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    AuthStatusAPIView,
    ChangePasswordAPIView,
    UserListCreateAPIView,
    UserDetailAPIView,
    RoleListAPIView,
)
from academics.api_views import (
    DepartmentListAPIView,
    DepartmentDetailAPIView,
    ClassListAPIView,
    ClassDetailAPIView,
    SubjectListAPIView,
    SubjectDetailAPIView,
)
from documents.api_views import (
    DocumentListCreateAPIView,
    DocumentUploadAPIView,
    DocumentDetailAPIView,
    DocumentApproveAPIView,
    DocumentRejectAPIView,
    DocumentPendingListAPIView,
    DocumentDownloadAPIView,
    FolderListCreateAPIView,
    ActivityLogListAPIView,
    DashboardStatsAPIView,
)
from ai_search.api_views import (
    AIQueryAPIView,
    AIHistoryAPIView,
)

# API URL patterns
api_patterns = [
    # Health check
    path('health/', HealthCheckAPIView.as_view(), name='api_health'),

    # Auth
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('auth/me/', CurrentUserAPIView.as_view(), name='api_me'),
    path('auth/status/', AuthStatusAPIView.as_view(), name='api_auth_status'),
    path('auth/change-password/', ChangePasswordAPIView.as_view(), name='api_change_password'),

    # User Management
    path('users/', UserListCreateAPIView.as_view(), name='api_users'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='api_user_detail'),
    path('roles/', RoleListAPIView.as_view(), name='api_roles'),

    # Academics
    path('departments/', DepartmentListAPIView.as_view(), name='api_departments'),
    path('departments/<int:pk>/', DepartmentDetailAPIView.as_view(), name='api_department_detail'),
    path('classes/', ClassListAPIView.as_view(), name='api_classes'),
    path('classes/<int:pk>/', ClassDetailAPIView.as_view(), name='api_class_detail'),
    path('subjects/', SubjectListAPIView.as_view(), name='api_subjects'),
    path('subjects/<int:pk>/', SubjectDetailAPIView.as_view(), name='api_subject_detail'),

    # Documents
    path('documents/', DocumentListCreateAPIView.as_view(), name='api_documents'),
    path('documents/upload/', DocumentUploadAPIView.as_view(), name='api_document_upload'),
    path('documents/<int:pk>/', DocumentDetailAPIView.as_view(), name='api_document_detail'),
    path('documents/<int:pk>/approve/', DocumentApproveAPIView.as_view(), name='api_document_approve'),
    path('documents/<int:pk>/reject/', DocumentRejectAPIView.as_view(), name='api_document_reject'),
    path('documents/<int:pk>/download/', DocumentDownloadAPIView.as_view(), name='api_document_download'),
    path('documents/pending/', DocumentPendingListAPIView.as_view(), name='api_documents_pending'),
    path('folders/', FolderListCreateAPIView.as_view(), name='api_folders'),
    path('activity-logs/', ActivityLogListAPIView.as_view(), name='api_activity_logs'),

    # Dashboard & Statistics
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='api_dashboard_stats'),

    # AI Search
    path('ai/query/', AIQueryAPIView.as_view(), name='api_ai_query'),
    path('ai/history/', AIHistoryAPIView.as_view(), name='api_ai_history'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
]

# Chú ý bảo mật: Không phục vụ trực tiếp thư mục media qua static URL để chống bypass quyền truy cập.
# Toàn bộ việc tải file phải đi qua API /api/documents/<pk>/download/ có kiểm tra JWT / RBAC.
