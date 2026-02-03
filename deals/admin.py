from django.contrib import admin
from .models import Deal, DealComment, DealAttachment


class DealCommentInline(admin.TabularInline):
    model = DealComment
    extra = 0
    readonly_fields = ['created_by', 'created_at']


class DealAttachmentInline(admin.TabularInline):
    model = DealAttachment
    extra = 0
    readonly_fields = ['uploaded_by', 'uploaded_at', 'file_size']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'stage', 'status', 'amount', 'due_date', 
                    'owner', 'created_at']
    list_filter = ['stage', 'status', 'created_at']
    search_fields = ['title', 'client', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DealCommentInline, DealAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'client')
        }),
        ('Pipeline', {
            'fields': ('stage', 'status')
        }),
        ('Financial', {
            'fields': ('amount', 'due_date')
        }),
        ('Assignment', {
            'fields': ('assignee_initials', 'owner')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DealComment)
class DealCommentAdmin(admin.ModelAdmin):
    list_display = ['deal', 'created_by', 'created_at', 'text_preview']
    list_filter = ['created_at']
    search_fields = ['text', 'deal__title']
    readonly_fields = ['created_by', 'created_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text Preview'


@admin.register(DealAttachment)
class DealAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'deal', 'file_size', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['file_name', 'deal__title']
    readonly_fields = ['uploaded_by', 'uploaded_at', 'file_size']