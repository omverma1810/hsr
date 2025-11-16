from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pathlib import Path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from api.views import DevIndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Root development index — lists API docs and useful endpoints
    path('', DevIndexView.as_view(), name='dev-index'),

    # API endpoints
    path('api/', include('api.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # In development, also serve app static files from the api app static folder
    urlpatterns += static(settings.STATIC_URL, document_root=str(settings.BASE_DIR / 'api' / 'static'))
