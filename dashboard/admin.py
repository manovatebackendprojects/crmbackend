from django.contrib import admin
from .models import DashboardMetric, DashboardActivity, AISuggestion, MarketingPerformanceMetric


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_leads', 'active_deals', 'customer_satisfaction_rate', 'last_calculated']
    list_filter = ['last_calculated']
    search_fields = ['user__email', 'user__first_name']
    readonly_fields = ['last_calculated']
    
    actions = ['recalculate_metrics']
    
    def recalculate_metrics(self, request, queryset):
        for metric in queryset:
            metric.calculate_metrics()
        self.message_user(request, f"Recalculated metrics for {queryset.count()} users.")
    recalculate_metrics.short_description = "Recalculate selected metrics"


@admin.register(DashboardActivity)
class DashboardActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'title', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'title', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User & Type', {
            'fields': ('user', 'activity_type')
        }),
        ('Content', {
            'fields': ('title', 'description', 'action')
        }),
        ('Related Objects', {
            'fields': ('lead_id', 'deal_id', 'task_id'),
            'classes': ('collapse',)
        }),
        ('Changes', {
            'fields': ('old_value', 'new_value'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )


@admin.register(AISuggestion)
class AISuggestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'suggestion_type', 'priority', 'title', 'confidence_score', 'is_actioned', 'created_at']
    list_filter = ['suggestion_type', 'priority', 'is_actioned', 'created_at']
    search_fields = ['user__email', 'title', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Suggestion Details', {
            'fields': ('user', 'suggestion_type', 'priority', 'title', 'description')
        }),
        ('Metrics', {
            'fields': ('confidence_score', 'metric_value', 'metric_change')
        }),
        ('Related Objects', {
            'fields': ('lead_ids', 'deal_ids'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_actioned', 'actioned_at', 'action_notes')
        }),
        ('Timeline', {
            'fields': ('created_at', 'expires_at')
        }),
    )


@admin.register(MarketingPerformanceMetric)
class MarketingPerformanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'metric_date', 'total_hours', 'active_hours', 'leads_contacted', 'conversion_rate']
    list_filter = ['metric_date', 'user']
    search_fields = ['user__email']
    
    fieldsets = (
        ('User & Date', {
            'fields': ('user', 'metric_date')
        }),
        ('Hours Tracking', {
            'fields': ('total_hours', 'active_hours')
        }),
        ('Activity Metrics', {
            'fields': ('leads_contacted', 'deals_progressed', 'calls_made', 'meetings_held')
        }),
        ('Performance', {
            'fields': ('conversion_rate', 'avg_deal_value')
        }),
    )