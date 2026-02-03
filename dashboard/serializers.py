from rest_framework import serializers
from .models import DashboardMetric, DashboardActivity, AISuggestion, MarketingPerformanceMetric
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardMetricSerializer(serializers.ModelSerializer):
    satisfaction_rate = serializers.FloatField(source='customer_satisfaction_rate')
    
    class Meta:
        model = DashboardMetric
        fields = [
            'total_leads', 'new_leads_this_month',
            'active_deals', 'deals_in_progress',
            'won_deals_total', 'lost_deals_total',
            'total_deal_value', 'satisfaction_rate',
            'last_calculated'
        ]
        read_only_fields = fields


class DashboardActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_initials = serializers.SerializerMethodField()
    avatar_bg_color = serializers.SerializerMethodField()
    
    class Meta:
        model = DashboardActivity
        fields = [
            'id', 'activity_type', 'title', 'description', 'action',
            'user_name', 'user_initials', 'avatar_bg_color',
            'lead_id', 'deal_id', 'task_id',
            'old_value', 'new_value', 'created_at'
        ]
        read_only_fields = fields
    
    def get_user_initials(self, obj):
        """Get user initials for avatar"""
        return obj.user.get_full_name()[:1].upper() if obj.user.get_full_name() else obj.user.username[:1]
    
    def get_avatar_bg_color(self, obj):
        """Generate consistent background color based on user"""
        colors = ['bg-yellow-400', 'bg-teal-600', 'bg-blue-500', 'bg-green-500', 'bg-pink-500']
        index = hash(obj.user.id) % len(colors)
        return colors[index]


class AISuggestionSerializer(serializers.ModelSerializer):
    icon_color = serializers.SerializerMethodField()
    is_valid = serializers.BooleanField(read_only=True)
    related_leads = serializers.SerializerMethodField()
    related_deals = serializers.SerializerMethodField()
    
    class Meta:
        model = AISuggestion
        fields = [
            'id', 'suggestion_type', 'priority', 'title', 'description',
            'confidence_score', 'metric_value', 'metric_change',
            'is_actioned', 'actioned_at', 'action_notes',
            'icon_color', 'is_valid', 'related_leads', 'related_deals',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at', 'expires_at', 'is_valid']
    
    def get_icon_color(self, obj):
        """Get icon color based on suggestion type"""
        color_map = {
            'follow_up': 'bg-yellow-400',
            'risk_alert': 'bg-red-500',
            'opportunity': 'bg-green-500',
            'performance': 'bg-blue-500',
            'close_date': 'bg-orange-500',
        }
        return color_map.get(obj.suggestion_type, 'bg-gray-400')
    
    def get_related_leads(self, obj):
        """Parse and return related lead IDs"""
        if not obj.lead_ids:
            return []
        return [int(x.strip()) for x in obj.lead_ids.split(',') if x.strip().isdigit()]
    
    def get_related_deals(self, obj):
        """Parse and return related deal IDs"""
        if not obj.deal_ids:
            return []
        return [int(x.strip()) for x in obj.deal_ids.split(',') if x.strip().isdigit()]


class MarketingPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingPerformanceMetric
        fields = [
            'id', 'metric_date', 'total_hours', 'active_hours',
            'leads_contacted', 'deals_progressed', 'calls_made',
            'meetings_held', 'conversion_rate', 'avg_deal_value'
        ]
        read_only_fields = fields


class DashboardSummarySerializer(serializers.Serializer):
    """Comprehensive dashboard summary"""
    metrics = DashboardMetricSerializer()
    recent_activities = DashboardActivitySerializer(many=True)
    ai_suggestions = AISuggestionSerializer(many=True)
    top_performing_deals = serializers.SerializerMethodField()
    pending_tasks = serializers.SerializerMethodField()
    
    def get_top_performing_deals(self, obj):
        """Get top 3 performing deals"""
        return {}  # Populated by view
    
    def get_pending_tasks(self, obj):
        """Get pending tasks"""
        return {}  # Populated by view