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
    ClassListAPIView,
    SubjectListAPIView,
)
from documents.api_views import (
    DocumentListCreateAPIView,
    DocumentDetailAPIView,
    DocumentApproveAPIView,
    DocumentRejectAPIView,
    DocumentPendingListAPIView,
    DocumentDownloadAPIView,
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
    path('classes/', ClassListAPIView.as_view(), name='api_classes'),
    path('subjects/', SubjectListAPIView.as_view(), name='api_subjects'),

    # Documents
    path('documents/', DocumentListCreateAPIView.as_view(), name='api_documents'),
    path('documents/<int:pk>/', DocumentDetailAPIView.as_view(), name='api_document_detail'),
    path('documents/<int:pk>/approve/', DocumentApproveAPIView.as_view(), name='api_document_approve'),
    path('documents/<int:pk>/reject/', DocumentRejectAPIView.as_view(), name='api_document_reject'),
    path('documents/<int:pk>/download/', DocumentDownloadAPIView.as_view(), name='api_document_download'),
    path('documents/pending/', DocumentPendingListAPIView.as_view(), name='api_documents_pending'),

    # AI Search
    path('ai/query/', AIQueryAPIView.as_view(), name='api_ai_query'),
    path('ai/history/', AIHistoryAPIView.as_view(), name='api_ai_history'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
