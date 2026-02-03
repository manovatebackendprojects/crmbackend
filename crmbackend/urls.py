from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('crmapp.urls')),
    path('api/calendar/', include('calendar_events.urls')),
    path('api/', include('leads.urls')),
    path('api/', include('tasks.urls')),
    path('api/', include('deals.urls')),

    # ... other patterns
    path('api/dashboard/', include('dashboard.urls')),

    # OpenAPI schema and Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Convenient aliases for documentation
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-root'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-api'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)