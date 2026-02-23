import secrets
import logging
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()
logger = logging.getLogger("analytics")


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        user = self.request.user
        user.last_active = timezone.now()
        user.save(update_fields=["last_active"])
        return user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        logger.info(f"Password changed for user {request.user.username}")
        return Response({"detail": "Password updated successfully."})


@api_view(["POST"])
def generate_api_key(request):
    user = request.user
    user.api_key = secrets.token_hex(32)
    user.save(update_fields=["api_key"])
    logger.info(f"API key generated for user {user.username}")
    return Response({"api_key": user.api_key})


@api_view(["GET"])
def user_stats(request):
    user = request.user
    from analytics.models import Dashboard, AnalyticsEvent, Alert, Report

    stats = {
        "dashboards": Dashboard.objects.filter(owner=user).count(),
        "events_today": AnalyticsEvent.objects.filter(
            source__created_by=user,
            timestamp__date=timezone.now().date(),
        ).count(),
        "active_alerts": Alert.objects.filter(owner=user, is_active=True).count(),
        "reports_generated": Report.objects.filter(generated_by=user).count(),
    }
    return Response(stats)
