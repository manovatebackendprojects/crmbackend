from django.contrib import admin
from django.urls import path, include
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/leads/", include("leads.urls")),
    path("api/tasks/", include("tasks.urls")),
]
