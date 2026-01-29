from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('crmapp.urls')),
    path('api/calendar/', include('calendar_module.urls')),
    path('api/leads/', include('leads.urls')),
    path('api/tasks/', include('tasks.urls')),

    # OpenAPI schema and Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

