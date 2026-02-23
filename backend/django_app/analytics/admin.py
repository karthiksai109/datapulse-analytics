from django.contrib import admin
from .models import DataSource, Dashboard, Widget, AnalyticsEvent, Alert, Report


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "source_type", "is_active", "created_by", "created_at"]
    list_filter = ["source_type", "is_active"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "is_public", "created_at"]
    list_filter = ["is_public"]
    search_fields = ["title", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ["title", "widget_type", "dashboard", "created_at"]
    list_filter = ["widget_type"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "source", "timestamp", "processed"]
    list_filter = ["event_type", "processed"]
    readonly_fields = ["id", "created_at"]
    date_hierarchy = "timestamp"


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ["name", "severity", "is_active", "owner", "last_triggered", "trigger_count"]
    list_filter = ["severity", "is_active"]
    search_fields = ["name"]
    readonly_fields = ["id", "last_triggered", "trigger_count", "created_at", "updated_at"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["title", "dashboard", "generated_by", "format", "created_at"]
    list_filter = ["format"]
    readonly_fields = ["id", "file_url", "ai_summary", "created_at"]
