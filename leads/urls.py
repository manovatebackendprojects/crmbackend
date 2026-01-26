from django.urls import path
from .views import CreateLeadAPIView, ListLeadAPIView

urlpatterns = [
    path("create/", CreateLeadAPIView.as_view(), name="create-lead"),
    path("list/", ListLeadAPIView.as_view(), name="list-lead"),
]
