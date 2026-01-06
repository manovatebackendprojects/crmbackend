
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    #path('api/leads/', include('leads.urls')),
    #path('api/deals/', include('deals.urls')),
    #path('api/tasks/', include('tasks.urls')),
    path('api/calendar/', include('calendar_module.urls')),
    #path('api/dashboard/', include('dashboard.urls')),

# Swagger URLs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]