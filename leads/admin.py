from django.contrib import admin
from .models import Lead, LeadNote, LeadActivity

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'email', 'stage', 'status', 'value', 'owner', 'created_at']
    list_filter = ['stage', 'status', 'source', 'created_at']
    search_fields = ['name', 'email', 'company', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'company', 'position')
        }),
        ('Status', {
            'fields': ('stage', 'status', 'source')
        }),
        ('Additional Information', {
            'fields': ('value', 'notes', 'image')
        }),
        ('Ownership', {
            'fields': ('owner', 'created_at', 'updated_at')
        }),
    )

@admin.register(LeadNote)
class LeadNoteAdmin(admin.ModelAdmin):
    list_display = ['lead', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['lead__name', 'text']

@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ['lead', 'activity_type', 'activity_date', 'created_by']
    list_filter = ['activity_type', 'activity_date']
    search_fields = ['lead__name', 'description']