from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.permissions import IsAuthenticated
from api.views import DevIndexView

# API Documentation views - restrict to authenticated users in production
if settings.DEBUG:
    # In development, allow public access
    schema_view = SpectacularAPIView.as_view()
    swagger_view = SpectacularSwaggerView.as_view(url_name='schema')
    redoc_view = SpectacularRedocView.as_view(url_name='schema')
else:
    # In production, require authentication
    schema_view = SpectacularAPIView.as_view(permission_classes=[IsAuthenticated])
    swagger_view = SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[IsAuthenticated])
    redoc_view = SpectacularRedocView.as_view(url_name='schema', permission_classes=[IsAuthenticated])

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('api.urls')),

    # API Documentation (public in dev, authenticated in production)
    path('api/schema/', schema_view, name='schema'),
    path('api/docs/', swagger_view, name='swagger-ui'),
    path('api/redoc/', redoc_view, name='redoc'),
]

# Root development index - only in DEBUG mode
if settings.DEBUG:
    urlpatterns.insert(0, path('', DevIndexView.as_view(), name='dev-index'))
else:
    urlpatterns.insert(0, path('', RedirectView.as_view(pattern_name='swagger-ui', permanent=False), name='root-redirect'))

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # In development, also serve app static files from the api app static folder
    urlpatterns += static(settings.STATIC_URL, document_root=str(settings.BASE_DIR / 'api' / 'static'))
