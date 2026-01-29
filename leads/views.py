from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import Lead
from .serializers import LeadSerializer

class CreateLeadAPIView(generics.CreateAPIView):
    """
    Create a new lead.
    """
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    
    @extend_schema(tags=["Leads"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ListLeadAPIView(generics.ListAPIView):
    """
    List all leads.
    """
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    
    @extend_schema(tags=["Leads"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
