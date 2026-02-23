from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "organization", "role", "is_active", "last_active"]
    list_filter = ["role", "is_active", "organization"]
    search_fields = ["username", "email", "organization"]
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("bio", "organization", "role", "avatar_url", "api_key")}),
    )
