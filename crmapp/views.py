from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import DatabaseError
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .serializers import SignupSerializer, LoginSerializer

from django.conf import settings
from google.auth.exceptions import GoogleAuthError

import logging

logger = logging.getLogger(__name__)


class SignupAPIView(APIView):
    """
    User registration endpoint.
    Create a new user account with email and password.
    """

    @extend_schema(request=SignupSerializer, tags=["Authentication"], description="Register a new user")
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            refresh = RefreshToken.for_user(user)
            logger.info(f"Token generated for user {user.email}")
        except Exception as e:
            logger.exception("Token generation failed during signup")
            return Response(
                {"detail": "Signup successful but token generation failed. Please login."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "detail": "User registered successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": "Admin" if user.is_superuser else "User",
                },
            },
            status=status.HTTP_201_CREATED
        )


class LoginAPIView(APIView):
    @extend_schema(request=LoginSerializer, tags=["Authentication"])
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user_obj = User.objects.filter(
                Q(email__iexact=email) | Q(username__iexact=email)
            ).first()
        except DatabaseError:
            logger.exception("Database error while looking up user for login")
            return Response(
                {"detail": "Login unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if not user_obj:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(
            request=request,
            username=user_obj.username,
            password=password
        )

        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken.for_user(user)
        except Exception:
            logger.exception("Token generation failed during login")
            return Response(
                {"detail": "Login failed. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": "Admin" if user.is_superuser else "User",
                },
            },
            status=status.HTTP_200_OK
        )


GOOGLE_CLIENT_ID = "716629866713-sdb355kgro0uh3pm4o1r3jlmcssohgab.apps.googleusercontent.com"

class GoogleLoginAPIView(APIView):
    """
    Google OAuth login endpoint.
    Authenticate user with Google ID token.
    """

    @extend_schema(tags=["Authentication"], description="Login with Google OAuth token")
    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"detail": "id_token is required"}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
        except (ValueError, GoogleAuthError):
            return Response({"detail": "Invalid Google token"}, status=401)

        email = idinfo.get("email")
        if not email:
            return Response({"detail": "Google token missing email"}, status=400)

        user, _ = User.objects.get_or_create(username=email, defaults={"email": email})

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Google login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "role": "Admin" if user.is_superuser else "User",
            },
        }, status=200)