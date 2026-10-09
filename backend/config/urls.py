from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Auth views wired directly (no app_name conflict)
from accounts.views import login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),

    # Apps
    path('dashboard/', include('dashboard.urls')),
    path('admin-panel/', include('accounts.urls')),
    path('admin-panel/', include('academics.urls')),
    path('', include('documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
