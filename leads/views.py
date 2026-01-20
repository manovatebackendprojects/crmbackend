from rest_framework import generics
from .models import Lead
from .serializers import LeadSerializer

class CreateLeadAPIView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

class ListLeadAPIView(generics.ListAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
