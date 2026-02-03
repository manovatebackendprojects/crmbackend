from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
from django.apps import apps
from .models import Lead, LeadNote, LeadActivity
from .serializers import (
    LeadSerializer, LeadListSerializer,
    LeadNoteSerializer, LeadActivitySerializer
)


def get_lead_queryset(request):
    if not request or not request.user.is_authenticated:
        return Lead.objects.none()

    queryset = Lead.objects.filter(owner=request.user)

    stage = request.query_params.get('stage')
    if stage:
        queryset = queryset.filter(stage=stage)

    status_param = request.query_params.get('status')
    if status_param:
        queryset = queryset.filter(status=status_param)

    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(
            models.Q(name__icontains=search) |
            models.Q(email__icontains=search) |
            models.Q(company__icontains=search) |
            models.Q(phone__icontains=search)
        )

    return queryset

class LeadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        return LeadSerializer
    
    def get_queryset(self):
        return get_lead_queryset(self.request)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ListLeadAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeadListSerializer

    def get_queryset(self):
        return get_lead_queryset(self.request)


class CreateLeadAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeadSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def notes(self, request, pk=None):
        """Add a note to a lead"""
        lead = self.get_object()
        serializer = LeadNoteSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(lead=lead, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def activities(self, request, pk=None):
        """Add an activity to a lead"""
        lead = self.get_object()
        serializer = LeadActivitySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(lead=lead, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        """Convert lead to deal"""
        lead = self.get_object()
        
        # Create a deal from this lead (requires deals app)
        # This is a placeholder - implement based on your deals model
        try:
            Deal = apps.get_model('deals', 'Deal')
        except LookupError:
            return Response(
                {'detail': 'Deals app is not installed.'},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )
        
        deal = Deal.objects.create(
            name=f"Deal with {lead.company or lead.name}",
            contact_name=lead.name,
            contact_email=lead.email,
            contact_phone=lead.phone,
            company=lead.company,
            value=lead.value,
            stage='Qualification',
            owner=request.user,
            source_lead=lead
        )
        
        # Update lead status
        lead.status = 'Converted'
        lead.save()
        
        return Response({
            'message': 'Lead converted to deal successfully',
            'deal_id': deal.id
        }, status=status.HTTP_201_CREATED)