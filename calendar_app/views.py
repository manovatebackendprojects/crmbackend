# Views for calendar
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Event.objects.filter(created_by=self.request.user)

        # Calendar filters (month/week/day)
        date = self.request.query_params.get('date')
        view_type = self.request.query_params.get('view')  # day / week / month

        if date and view_type:
            date = parse_date(date)

            if view_type == 'day':
                queryset = queryset.filter(start_datetime__date=date)

            elif view_type == 'week':
                queryset = queryset.filter(
                    start_datetime__week=date.isocalendar()[1]
                )

            elif view_type == 'month':
                queryset = queryset.filter(
                    start_datetime__year=date.year,
                    start_datetime__month=date.month
                )

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
