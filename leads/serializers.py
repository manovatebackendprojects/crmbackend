from rest_framework import serializers
from .models import Lead

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"

    def validate_email(self, value):
        if Lead.objects.filter(email=value).exists():
            raise serializers.ValidationError("Lead with this email already exists.")
        return value

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value
