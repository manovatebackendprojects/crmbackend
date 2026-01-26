from django.urls import path
from .views import CreateTaskAPIView, ListTaskAPIView

urlpatterns = [
    path("create/", CreateTaskAPIView.as_view()),
    path("list/", ListTaskAPIView.as_view()),
]
