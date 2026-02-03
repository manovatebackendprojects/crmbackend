from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Deal(models.Model):
    STAGE_CHOICES = [
        ('Clients', 'Clients'),
        ('Orders', 'Orders'),
        ('Tasks', 'Tasks'),
        ('Due Date', 'Due Date'),
        ('Revenue', 'Revenue'),
        ('Status', 'Status'),
    ]
    
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Won', 'Won'),
        ('Lost', 'Lost'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    client = models.CharField(max_length=255, blank=True, null=True)
    
    # Pipeline & Status
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='Clients')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    
    # Financial Information
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Deal value/revenue")
    
    # Timeline
    due_date = models.DateField(blank=True, null=True)
    
    # Assignment
    assignee_initials = models.CharField(max_length=10, blank=True, null=True)
    
    # Ownership & Timestamps
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client or 'No Client'}"
    
    def get_activity_counts(self):
        """Return counts of comments and attachments"""
        return {
            'comments': self.comments.count(),
            'attachments': self.attachments.count(),
        }


class DealComment(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.deal.title} by {self.created_by.username}"


class DealAttachment(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='deal_attachments/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.deal.title}"
    
    def save(self, *args, **kwargs):
        if self.file and not self.file_name:
            self.file_name = self.file.name
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)