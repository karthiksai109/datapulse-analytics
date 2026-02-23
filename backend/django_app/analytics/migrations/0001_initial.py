import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DataSource",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("source_type", models.CharField(choices=[("api", "REST API"), ("webhook", "Webhook"), ("csv", "CSV Upload"), ("database", "Database Connection"), ("streaming", "Streaming Source")], max_length=20)),
                ("connection_config", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="data_sources", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Dashboard",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("layout_config", models.JSONField(default=dict)),
                ("is_public", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dashboards", to=settings.AUTH_USER_MODEL)),
                ("data_sources", models.ManyToManyField(blank=True, related_name="dashboards", to="analytics.datasource")),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="Widget",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("widget_type", models.CharField(choices=[("line_chart", "Line Chart"), ("bar_chart", "Bar Chart"), ("pie_chart", "Pie Chart"), ("metric_card", "Metric Card"), ("table", "Data Table"), ("heatmap", "Heatmap"), ("scatter", "Scatter Plot")], max_length=20)),
                ("query_config", models.JSONField(default=dict)),
                ("position_x", models.IntegerField(default=0)),
                ("position_y", models.IntegerField(default=0)),
                ("width", models.IntegerField(default=6)),
                ("height", models.IntegerField(default=4)),
                ("refresh_interval", models.IntegerField(default=30, help_text="Refresh interval in seconds")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("dashboard", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="widgets", to="analytics.dashboard")),
            ],
            options={
                "ordering": ["position_y", "position_x"],
            },
        ),
        migrations.CreateModel(
            name="AnalyticsEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_type", models.CharField(db_index=True, max_length=100)),
                ("payload", models.JSONField(default=dict)),
                ("metadata", models.JSONField(default=dict)),
                ("timestamp", models.DateTimeField(db_index=True)),
                ("processed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("source", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="analytics.datasource")),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
        migrations.CreateModel(
            name="Alert",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("condition_config", models.JSONField(default=dict)),
                ("severity", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")], default="medium", max_length=10)),
                ("is_active", models.BooleanField(default=True)),
                ("last_triggered", models.DateTimeField(blank=True, null=True)),
                ("trigger_count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to=settings.AUTH_USER_MODEL)),
                ("dashboard", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="analytics.dashboard")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("format", models.CharField(choices=[("pdf", "PDF"), ("csv", "CSV"), ("json", "JSON")], default="pdf", max_length=10)),
                ("file_url", models.URLField(blank=True, help_text="S3 URL of the generated report")),
                ("ai_summary", models.TextField(blank=True, help_text="AI-generated summary of the report")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("dashboard", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reports", to="analytics.dashboard")),
                ("generated_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="datasource",
            index=models.Index(fields=["source_type", "is_active"], name="analytics_d_source__idx"),
        ),
        migrations.AddIndex(
            model_name="datasource",
            index=models.Index(fields=["created_by", "-created_at"], name="analytics_d_created_idx"),
        ),
        migrations.AddIndex(
            model_name="analyticsevent",
            index=models.Index(fields=["event_type", "-timestamp"], name="analytics_a_event_t_idx"),
        ),
        migrations.AddIndex(
            model_name="analyticsevent",
            index=models.Index(fields=["processed", "-timestamp"], name="analytics_a_process_idx"),
        ),
    ]
