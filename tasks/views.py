from rest_framework import generics
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
permission_classes = [IsAuthenticated]


class CreateTaskAPIView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class ListTaskAPIView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
