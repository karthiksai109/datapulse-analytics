import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DataSource(models.Model):
    SOURCE_TYPES = [
        ("api", "REST API"),
        ("webhook", "Webhook"),
        ("csv", "CSV Upload"),
        ("database", "Database Connection"),
        ("streaming", "Streaming Source"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    connection_config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="data_sources")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["source_type", "is_active"]),
            models.Index(fields=["created_by", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class Dashboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    layout_config = models.JSONField(default=dict)
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dashboards")
    data_sources = models.ManyToManyField(DataSource, blank=True, related_name="dashboards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class Widget(models.Model):
    WIDGET_TYPES = [
        ("line_chart", "Line Chart"),
        ("bar_chart", "Bar Chart"),
        ("pie_chart", "Pie Chart"),
        ("metric_card", "Metric Card"),
        ("table", "Data Table"),
        ("heatmap", "Heatmap"),
        ("scatter", "Scatter Plot"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="widgets")
    title = models.CharField(max_length=255)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    query_config = models.JSONField(default=dict)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=6)
    height = models.IntegerField(default=4)
    refresh_interval = models.IntegerField(default=30, help_text="Refresh interval in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position_y", "position_x"]

    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"


class AnalyticsEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, db_index=True)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    payload = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(db_index=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["event_type", "-timestamp"]),
            models.Index(fields=["processed", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    condition_config = models.JSONField(default=dict)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="medium")
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alerts")
    dashboard = models.ForeignKey(Dashboard, on_delete=models.SET_NULL, null=True, blank=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class Report(models.Model):
    FORMAT_CHOICES = [
        ("pdf", "PDF"),
        ("csv", "CSV"),
        ("json", "JSON"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="reports")
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default="pdf")
    file_url = models.URLField(blank=True, help_text="S3 URL of the generated report")
    ai_summary = models.TextField(blank=True, help_text="AI-generated summary of the report")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_format_display()})"
