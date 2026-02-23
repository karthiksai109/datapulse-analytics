from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(blank=True)
    organization = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ("admin", "Admin"),
            ("analyst", "Analyst"),
            ("viewer", "Viewer"),
        ],
        default="viewer",
    )
    avatar_url = models.URLField(blank=True)
    api_key = models.CharField(max_length=64, blank=True, unique=True, null=True)
    last_active = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
