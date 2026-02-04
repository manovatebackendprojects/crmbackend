from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import IntegrityError


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("email", "password", "full_name")

    def validate(self, data):
        # Validate full_name from initial_data
        if "full_name" in self.initial_data:
            full_name = self.initial_data.get("full_name", "").strip()
            # Add to data so create() can access it
            data["full_name"] = full_name
        return data

    def validate_email(self, value):
        if User.objects.filter(username=value).exists() or User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")
        full_name = validated_data.get("full_name", "").strip()
        
        first_name = ""
        last_name = ""
        if full_name:
            parts = full_name.split()
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except IntegrityError:
            raise serializers.ValidationError({"email": ["An account with this email already exists."]})
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)