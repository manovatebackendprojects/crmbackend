from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, Sum, Avg
from .models import DashboardMetric, DashboardActivity, AISuggestion, MarketingPerformanceMetric
from .serializers import (
    DashboardMetricSerializer,
    DashboardActivitySerializer,
    AISuggestionSerializer,
    MarketingPerformanceSerializer,
    DashboardSummarySerializer
)


class DashboardViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users only see their own dashboard"""
        return DashboardMetric.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get comprehensive dashboard summary"""
        user = request.user
        
        # Get or create dashboard metric
        metric, _ = DashboardMetric.objects.get_or_create(user=user)
        metric.calculate_metrics()
        
        # Get recent activities
        activities = DashboardActivity.objects.filter(
            user=user
        ).order_by('-created_at')[:10]
        
        # Get active AI suggestions
        suggestions = AISuggestion.objects.filter(
            user=user,
            expires_at__gt=timezone.now(),
            is_actioned=False
        ).order_by('-priority', '-created_at')[:5]
        
        data = {
            'metrics': DashboardMetricSerializer(metric).data,
            'recent_activities': DashboardActivitySerializer(activities, many=True).data,
            'ai_suggestions': AISuggestionSerializer(suggestions, many=True).data,
            'dashboard_timestamp': timezone.now().isoformat()
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get dashboard metrics"""
        user = request.user
        metric, _ = DashboardMetric.objects.get_or_create(user=user)
        metric.calculate_metrics()
        
        serializer = DashboardMetricSerializer(metric)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def refresh_metrics(self, request):
        """Force refresh dashboard metrics"""
        user = request.user
        metric, _ = DashboardMetric.objects.get_or_create(user=user)
        metric.calculate_metrics()
        
        serializer = DashboardMetricSerializer(metric)
        return Response(serializer.data)


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardActivitySerializer
    
    def get_queryset(self):
        """Return activities for current user"""
        queryset = DashboardActivity.objects.filter(user=self.request.user)
        
        # Filter by type
        activity_type = self.request.query_params.get('type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by date range
        days = self.request.query_params.get('days', 7)
        try:
            days = int(days)
            since_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=since_date)
        except ValueError:
            pass
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def log_activity(self, request):
        """Create a new activity log"""
        activity_type = request.data.get('activity_type')
        title = request.data.get('title')
        description = request.data.get('description', '')
        action = request.data.get('action', '')
        
        if not activity_type or not title:
            return Response(
                {'detail': 'activity_type and title are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        activity = DashboardActivity.objects.create(
            user=request.user,
            activity_type=activity_type,
            title=title,
            description=description,
            action=action,
            lead_id=request.data.get('lead_id'),
            deal_id=request.data.get('deal_id'),
            task_id=request.data.get('task_id'),
            old_value=request.data.get('old_value'),
            new_value=request.data.get('new_value'),
        )
        
        serializer = DashboardActivitySerializer(activity)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities"""
        limit = request.query_params.get('limit', 15)
        try:
            limit = int(limit)
        except ValueError:
            limit = 15
        
        activities = self.get_queryset()[:limit]
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get activity summary"""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_activities = DashboardActivity.objects.filter(
            user=request.user,
            created_at__gte=today_start
        ).count()
        
        week_activities = DashboardActivity.objects.filter(
            user=request.user,
            created_at__gte=now - timedelta(days=7)
        ).count()
        
        activity_types = DashboardActivity.objects.filter(
            user=request.user,
            created_at__gte=now - timedelta(days=30)
        ).values('activity_type').annotate(count=Count('id'))
        
        return Response({
            'today_activities': today_activities,
            'week_activities': week_activities,
            'activity_types': activity_types
        })


class AISuggestionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AISuggestionSerializer
    
    def get_queryset(self):
        """Return suggestions for current user"""
        queryset = AISuggestion.objects.filter(user=self.request.user)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by type
        suggestion_type = self.request.query_params.get('type')
        if suggestion_type:
            queryset = queryset.filter(suggestion_type=suggestion_type)
        
        # Only active suggestions
        active_only = self.request.query_params.get('active_only', 'true')
        if active_only == 'true':
            queryset = queryset.filter(
                expires_at__gt=timezone.now(),
                is_actioned=False
            )
        
        return queryset.order_by('-priority', '-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_actioned(self, request, pk=None):
        """Mark suggestion as actioned"""
        suggestion = self.get_object()
        suggestion.is_actioned = True
        suggestion.actioned_at = timezone.now()
        suggestion.action_notes = request.data.get('action_notes', '')
        suggestion.save()
        
        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_suggestion(self, request):
        """Create a new AI suggestion (admin use)"""
        suggestion = AISuggestion.objects.create(
            user=request.user,
            suggestion_type=request.data.get('suggestion_type'),
            priority=request.data.get('priority', 'medium'),
            title=request.data.get('title'),
            description=request.data.get('description'),
            confidence_score=request.data.get('confidence_score', 0.5),
            lead_ids=request.data.get('lead_ids', ''),
            deal_ids=request.data.get('deal_ids', ''),
            metric_value=request.data.get('metric_value'),
            metric_change=request.data.get('metric_change'),
            expires_at=timezone.now() + timedelta(days=int(request.data.get('days', 7)))
        )
        
        serializer = self.get_serializer(suggestion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active suggestions only"""
        suggestions = self.get_queryset()[:10]
        serializer = self.get_serializer(suggestions, many=True)
        return Response(serializer.data)


class MarketingPerformanceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MarketingPerformanceSerializer
    
    def get_queryset(self):
        """Return performance metrics for current user"""
        queryset = MarketingPerformanceMetric.objects.filter(user=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(metric_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(metric_date__lte=end_date)
        
        return queryset.order_by('-metric_date')
    
    @action(detail=False, methods=['get'])
    def current_month(self, request):
        """Get current month performance"""
        now = timezone.now()
        month_start = now.replace(day=1)
        
        metrics = MarketingPerformanceMetric.objects.filter(
            user=request.user,
            metric_date__gte=month_start.date()
        )
        
        aggregates = metrics.aggregate(
            total_hours=Sum('total_hours'),
            active_hours=Sum('active_hours'),
            leads_contacted=Sum('leads_contacted'),
            deals_progressed=Sum('deals_progressed'),
            calls_made=Sum('calls_made'),
            meetings_held=Sum('meetings_held'),
            avg_conversion_rate=Avg('conversion_rate'),
            avg_deal_value=Avg('avg_deal_value')
        )
        
        return Response(aggregates)
    
    @action(detail=False, methods=['get'])
    def trend(self, request):
        """Get performance trend data"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        metrics = MarketingPerformanceMetric.objects.filter(
            user=request.user,
            metric_date__gte=start_date.date()
        ).order_by('metric_date')
        
        data = {
            'dates': [],
            'total_hours': [],
            'active_hours': [],
            'leads_contacted': [],
            'deals_progressed': [],
        }
        
        for metric in metrics:
            data['dates'].append(metric.metric_date.isoformat())
            data['total_hours'].append(metric.total_hours)
            data['active_hours'].append(metric.active_hours)
            data['leads_contacted'].append(metric.leads_contacted)
            data['deals_progressed'].append(metric.deals_progressed)
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def record_performance(self, request):
        """Record performance metrics for today"""
        today = timezone.now().date()
        
        metric, created = MarketingPerformanceMetric.objects.update_or_create(
            user=request.user,
            metric_date=today,
            defaults={
                'total_hours': request.data.get('total_hours', 0),
                'active_hours': request.data.get('active_hours', 0),
                'leads_contacted': request.data.get('leads_contacted', 0),
                'deals_progressed': request.data.get('deals_progressed', 0),
                'calls_made': request.data.get('calls_made', 0),
                'meetings_held': request.data.get('meetings_held', 0),
                'conversion_rate': request.data.get('conversion_rate', 0),
                'avg_deal_value': request.data.get('avg_deal_value', 0),
            }
        )
        
        serializer = self.get_serializer(metric)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)