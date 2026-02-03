from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import CalendarEvent, EventAttendee, EventReminder
from .serializers import (
    CalendarEventSerializer,
    CalendarEventListSerializer,
    EventAttendeeSerializer,
    EventReminderSerializer
)


class CalendarEventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return events owned by the current user"""
        queryset = CalendarEvent.objects.filter(owner=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(event_date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(event_date__lte=end_date)
            except ValueError:
                pass
        
        # Filter by event type
        event_type = self.request.query_params.get('type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by date (single date)
        date = self.request.query_params.get('date')
        if date:
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(event_date=date)
            except ValueError:
                pass
        
        # Search by title or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        # Filter upcoming events
        upcoming = self.request.query_params.get('upcoming')
        if upcoming == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                event_date__gte=now.date()
            ) | queryset.filter(
                event_date=now.date(),
                start_time__gte=now.time()
            )
        
        return queryset.select_related('owner').prefetch_related(
            'attendee_records', 'reminders'
        )
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return CalendarEventListSerializer
        return CalendarEventSerializer
    
    def perform_create(self, serializer):
        """Set the owner to the current user and create reminders"""
        event = serializer.save(owner=self.request.user)
        self._create_reminder(event)
        self._create_attendee_records(event, serializer.validated_data.get('attendees', ''))
    
    def perform_update(self, serializer):
        """Update event and reminders"""
        event = serializer.save()
        # Delete old reminders and create new ones
        event.reminders.all().delete()
        self._create_reminder(event)
        self._create_attendee_records(event, serializer.validated_data.get('attendees', ''))
    
    def _create_reminder(self, event):
        """Create reminder for the event"""
        if event.reminder_set:
            reminder_datetime = datetime.combine(
                event.event_date,
                event.start_time
            ) - timedelta(minutes=event.reminder_minutes_before)
            
            EventReminder.objects.create(
                event=event,
                reminder_time=reminder_datetime,
                reminder_type='notification'
            )
    
    def _create_attendee_records(self, event, attendees_str):
        """Create or update attendee records"""
        if not attendees_str:
            return
        
        # Parse attendees string
        try:
            if attendees_str.startswith('['):
                attendees_list = json.loads(attendees_str)
            else:
                attendees_list = [email.strip() for email in attendees_str.split(',')]
        except:
            attendees_list = [email.strip() for email in attendees_str.split(',')]
        
        # Clear existing attendees
        event.attendee_records.all().delete()
        
        # Create new attendee records
        for attendee_info in attendees_list:
            if isinstance(attendee_info, dict):
                email = attendee_info.get('email', '')
                name = attendee_info.get('name', '')
            else:
                email = attendee_info
                name = ''
            
            if email and '@' in email:
                EventAttendee.objects.create(
                    event=event,
                    email=email,
                    name=name or email.split('@')[0],
                    status='pending'
                )
    
    @action(detail=True, methods=['get'])
    def attendees(self, request, pk=None):
        """Get all attendees for an event"""
        event = self.get_object()
        serializer = EventAttendeeSerializer(
            event.attendee_records.all(),
            many=True
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_attendee(self, request, pk=None):
        """Add a new attendee to an event"""
        event = self.get_object()
        email = request.data.get('email')
        name = request.data.get('name', '')
        
        if not email:
            return Response(
                {'email': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not '@' in email:
            return Response(
                {'email': 'Invalid email format.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            attendee, created = EventAttendee.objects.get_or_create(
                event=event,
                email=email,
                defaults={'name': name or email.split('@')[0], 'status': 'pending'}
            )
            
            if not created:
                return Response(
                    {'detail': 'Attendee already exists.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = EventAttendeeSerializer(attendee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='attendees/(?P<attendee_id>[^/.]+)/respond')
    def respond_to_event(self, request, pk=None, attendee_id=None):
        """Update attendee response status"""
        event = self.get_object()
        status_response = request.data.get('status')
        
        if status_response not in ['accepted', 'declined', 'tentative']:
            return Response(
                {'status': 'Invalid status value.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            attendee = EventAttendee.objects.get(id=attendee_id, event=event)
            attendee.status = status_response
            attendee.responded_at = timezone.now()
            attendee.save()
            
            serializer = EventAttendeeSerializer(attendee)
            return Response(serializer.data)
        
        except EventAttendee.DoesNotExist:
            return Response(
                {'detail': 'Attendee not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'], url_path='attendees/(?P<attendee_id>[^/.]+)')
    def remove_attendee(self, request, pk=None, attendee_id=None):
        """Remove an attendee from an event"""
        event = self.get_object()
        
        try:
            attendee = EventAttendee.objects.get(id=attendee_id, event=event)
            attendee.delete()
            
            serializer = CalendarEventSerializer(event, context={'request': request})
            return Response(serializer.data)
        
        except EventAttendee.DoesNotExist:
            return Response(
                {'detail': 'Attendee not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def week_view(self, request, pk=None):
        """Get events for a specific week"""
        week_date = request.query_params.get('date')
        
        if not week_date:
            week_date = timezone.now().date()
        else:
            try:
                week_date = datetime.strptime(week_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'detail': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get week range (Sunday to Saturday)
        from datetime import timedelta
        week_start = week_date - timedelta(days=week_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        events = self.get_queryset().filter(
            event_date__gte=week_start,
            event_date__lte=week_end
        )
        
        serializer = self.get_serializer(events, many=True)
        return Response({
            'week_start': week_start,
            'week_end': week_end,
            'events': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def month_view(self, request):
        """Get events for a specific month"""
        month_date = request.query_params.get('date')
        
        if not month_date:
            month_date = timezone.now().date()
        else:
            try:
                month_date = datetime.strptime(month_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'detail': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get month range
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
        
        events = self.get_queryset().filter(
            event_date__gte=month_start,
            event_date__lte=month_end
        )
        
        serializer = self.get_serializer(events, many=True)
        return Response({
            'month': month_date.strftime('%Y-%m'),
            'month_start': month_start,
            'month_end': month_end,
            'events': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def today_events(self, request):
        """Get today's events"""
        today = timezone.now().date()
        events = self.get_queryset().filter(event_date=today)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming_events(self, request):
        """Get upcoming events"""
        now = timezone.now()
        events = self.get_queryset().filter(
            event_date__gte=now.date()
        ) | self.get_queryset().filter(
            event_date=now.date(),
            start_time__gte=now.time()
        )
        
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
            events = events[:limit]
        except ValueError:
            pass
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)