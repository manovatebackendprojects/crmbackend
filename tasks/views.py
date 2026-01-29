from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated

permission_classes = [IsAuthenticated]


class CreateTaskAPIView(generics.CreateAPIView):
    """
    Create a new task.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    @extend_schema(tags=["Tasks"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ListTaskAPIView(generics.ListAPIView):
    """
    List all tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    @extend_schema(tags=["Tasks"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
