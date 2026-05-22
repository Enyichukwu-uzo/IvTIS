# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings               # NEW
from django.conf.urls.static import static     # NEW

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('exams/', include('exams.urls')),
    path('staff/', include('staff.urls')),
]

# Only active when DEBUG=True (development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    """
    This tells Django to serve uploaded files from MEDIA_ROOT
    when accessed via MEDIA_URL.
    In production, Nginx or a CDN handles this instead.
    """