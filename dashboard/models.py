from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class DashboardMetric(models.Model):
    """Store calculated metrics for performance optimization"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_metric')
    
    # Lead Metrics
    total_leads = models.IntegerField(default=0)
    new_leads_this_month = models.IntegerField(default=0)
    
    # Deal Metrics
    active_deals = models.IntegerField(default=0)
    deals_in_progress = models.IntegerField(default=0)
    won_deals_total = models.IntegerField(default=0)
    lost_deals_total = models.IntegerField(default=0)
    total_deal_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Performance
    customer_satisfaction_rate = models.FloatField(default=0, help_text="Percentage of won deals")
    
    # Timestamps
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dashboard Metric'
        verbose_name_plural = 'Dashboard Metrics'
    
    def __str__(self):
        return f"Dashboard Metrics for {self.user.email}"
    
    def calculate_metrics(self):
        """Recalculate all metrics from source models"""
        from leads.models import Lead
        from deals.models import Deal
        
        # Lead metrics
        self.total_leads = Lead.objects.filter(owner=self.user).count()
        today = timezone.now().date()
        month_start = today.replace(day=1)
        self.new_leads_this_month = Lead.objects.filter(
            owner=self.user,
            created_at__date__gte=month_start
        ).count()
        
        # Deal metrics
        deals = Deal.objects.filter(owner=self.user)
        self.active_deals = deals.exclude(status__in=['Won', 'Lost']).count()
        self.deals_in_progress = deals.filter(
            stage__in=['Orders', 'Tasks', 'Due Date']
        ).count()
        
        won = deals.filter(status='Won').count()
        lost = deals.filter(status='Lost').count()
        self.won_deals_total = won
        self.lost_deals_total = lost
        
        # Satisfaction rate
        total_closed = won + lost
        self.customer_satisfaction_rate = (won / total_closed * 100) if total_closed > 0 else 0
        
        # Total value
        self.total_deal_value = deals.aggregate(Sum('amount'))['amount__sum'] or 0
        
        self.save()


class DashboardActivity(models.Model):
    """Track user activities for activity feed"""
    ACTIVITY_TYPE_CHOICES = [
        ('lead_created', 'Lead Created'),
        ('lead_updated', 'Lead Updated'),
        ('lead_deleted', 'Lead Deleted'),
        ('deal_created', 'Deal Created'),
        ('deal_updated', 'Deal Updated'),
        ('deal_stage_changed', 'Deal Stage Changed'),
        ('deal_won', 'Deal Won'),
        ('deal_lost', 'Deal Lost'),
        ('task_created', 'Task Created'),
        ('task_completed', 'Task Completed'),
        ('comment_added', 'Comment Added'),
        ('file_uploaded', 'File Uploaded'),
        ('team_joined', 'Team Member Joined'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES)
    
    # Related object info
    lead_id = models.IntegerField(blank=True, null=True)
    deal_id = models.IntegerField(blank=True, null=True)
    task_id = models.IntegerField(blank=True, null=True)
    
    # Activity details
    title = models.CharField(max_length=255, help_text="e.g., 'Acme Corp Lead Created'")
    description = models.TextField(blank=True, null=True)
    action = models.CharField(max_length=255, help_text="e.g., 'Lead created for Acme Corp'")
    
    # Change tracking
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"


class AISuggestion(models.Model):
    """AI-driven suggestions for users"""
    SUGGESTION_TYPE_CHOICES = [
        ('follow_up', 'Follow-up Needed'),
        ('risk_alert', 'Lead at Risk'),
        ('opportunity', 'Opportunity'),
        ('performance', 'Performance Insight'),
        ('close_date', 'Close Date Warning'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_suggestions')
    suggestion_type = models.CharField(max_length=30, choices=SUGGESTION_TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Suggestion content
    title = models.CharField(max_length=255, help_text="e.g., '3 leads at risk'")
    description = models.TextField(help_text="Detailed explanation and recommendation")
    confidence_score = models.FloatField(default=0.5, validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Related objects
    lead_ids = models.TextField(blank=True, null=True, help_text="Comma-separated lead IDs")
    deal_ids = models.TextField(blank=True, null=True, help_text="Comma-separated deal IDs")
    
    # Metrics
    metric_value = models.CharField(max_length=100, blank=True, null=True)
    metric_change = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., '+15%' or '-5%'")
    
    # Status
    is_actioned = models.BooleanField(default=False)
    actioned_at = models.DateTimeField(blank=True, null=True)
    action_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When this suggestion becomes outdated")
    
    class Meta:
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.suggestion_type} - {self.title}"
    
    def is_valid(self):
        """Check if suggestion is still valid"""
        return timezone.now() < self.expires_at and not self.is_actioned


class MarketingPerformanceMetric(models.Model):
    """Track marketing performance and time spent"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketing_metrics')
    
    # Date
    metric_date = models.DateField()
    
    # Hours tracking
    total_hours = models.FloatField(default=0, help_text="Total hours worked")
    active_hours = models.FloatField(default=0, help_text="Hours spent on active tasks")
    
    # Performance indicators
    leads_contacted = models.IntegerField(default=0)
    deals_progressed = models.IntegerField(default=0)
    calls_made = models.IntegerField(default=0)
    meetings_held = models.IntegerField(default=0)
    
    # Efficiency
    conversion_rate = models.FloatField(default=0, help_text="Percentage")
    avg_deal_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['user', 'metric_date']
        ordering = ['-metric_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.metric_date}"