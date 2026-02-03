from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Lead(models.Model):
    STAGE_CHOICES = [
        ('New', 'New'),
        ('Opened', 'Opened'),
        ('Interested', 'Interested'),
        ('Rejected', 'Rejected'),
        ('Closed', 'Closed'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Converted', 'Converted'),
    ]
    
    SOURCE_CHOICES = [
        ('Direct', 'Direct'),
        ('Linkedin', 'Linkedin'),
        ('Twitter', 'Twitter'),
        ('Facebook', 'Facebook'),
        ('Website', 'Website'),
        ('Referral', 'Referral'),
        ('Other', 'Other'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    
    # Status & Stage
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='New')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='Direct')
    
    # Additional Information
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='leads/', blank=True, null=True)
    
    # Ownership & Timestamps
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leads',
        null=True,
        blank=True,
        default=None,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.company or 'No Company'}"


class LeadNote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='lead_notes')
    text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.lead.name}"


class LeadActivity(models.Model):
    ACTIVITY_TYPES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('status_change', 'Status Change'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    activity_date = models.DateTimeField()
    
    class Meta:
        ordering = ['-activity_date']
        verbose_name_plural = 'Lead activities'
    
    def __str__(self):
        return f"{self.activity_type} - {self.lead.name}"