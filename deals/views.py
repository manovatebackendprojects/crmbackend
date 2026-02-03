from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from .models import Deal, DealComment, DealAttachment
from .serializers import (
    DealSerializer, 
    DealListSerializer,
    DealCommentSerializer, 
    DealAttachmentSerializer
)


class DealViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Return deals owned by the current user"""
        queryset = Deal.objects.filter(owner=self.request.user)
        
        # Filter by stage
        stage = self.request.query_params.get('stage')
        if (stage):
            queryset = queryset.filter(stage=stage)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            if status_filter == 'Active':
                queryset = queryset.exclude(status__in=['Won', 'Lost'])
            else:
                queryset = queryset.filter(status=status_filter)
        
        # Search by title, client, or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(client__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related('owner').prefetch_related(
            'comments', 'attachments'
        )
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return DealListSerializer
        return DealSerializer
    
    def perform_create(self, serializer):
        """Set the owner to the current user"""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to a deal"""
        deal = self.get_object()
        
        # Only pass text data, set deal and created_by in save()
        serializer = DealCommentSerializer(data={
            'text': request.data.get('text', '')
        })
        
        if serializer.is_valid():
            serializer.save(deal=deal, created_by=request.user)
            
            # Return updated deal with all comments
            deal_serializer = DealSerializer(deal, context={'request': request})
            return Response(deal_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Add an attachment to a deal"""
        deal = self.get_object()
        file = request.FILES.get('file')
        
        if not file:
            return Response(
                {'file': 'No file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only pass file data, set deal and uploaded_by in save()
        serializer = DealAttachmentSerializer(
            data={'file': file},
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save(deal=deal, uploaded_by=request.user)
            
            # Return updated deal with all attachments
            deal_serializer = DealSerializer(deal, context={'request': request})
            return Response(deal_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='attachments/(?P<attachment_id>[^/.]+)')
    def delete_attachment(self, request, pk=None, attachment_id=None):
        """Delete a specific attachment from a deal"""
        deal = self.get_object()
        
        try:
            attachment = DealAttachment.objects.get(id=attachment_id, deal=deal)
            attachment.file.delete()  # Delete file from storage
            attachment.delete()
            
            # Return updated deal
            deal_serializer = DealSerializer(deal, context={'request': request})
            return Response(deal_serializer.data, status=status.HTTP_200_OK)
        
        except DealAttachment.DoesNotExist:
            return Response(
                {'detail': 'Attachment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def update_stage(self, request, pk=None):
        """Update deal stage with validation"""
        deal = self.get_object()
        new_stage = request.data.get('stage')
        
        if not new_stage:
            return Response(
                {'stage': 'This field is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(deal, data={'stage': new_stage}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def close_deal(self, request, pk=None):
        """Close a deal with Won/Lost status"""
        deal = self.get_object()
        outcome = request.data.get('status')
        
        if outcome not in ['Won', 'Lost']:
            return Response(
                {'status': 'Status must be "Won" or "Lost".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate that deal is in Revenue stage
        if deal.stage != 'Revenue':
            return Response(
                {'detail': 'Deals can only be closed from the Revenue stage.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(
            deal,
            data={'stage': 'Status', 'status': outcome},
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)