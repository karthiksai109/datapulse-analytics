from rest_framework import serializers
from .models import DataSource, Dashboard, Widget, AnalyticsEvent, Alert, Report


class DataSourceSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DataSource
        fields = [
            "id", "name", "source_type", "connection_config",
            "is_active", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class WidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Widget
        fields = [
            "id", "dashboard", "title", "widget_type", "query_config",
            "position_x", "position_y", "width", "height",
            "refresh_interval", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DashboardSerializer(serializers.ModelSerializer):
    widgets = WidgetSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    data_sources = serializers.PrimaryKeyRelatedField(
        many=True, queryset=DataSource.objects.all(), required=False
    )

    class Meta:
        model = Dashboard
        fields = [
            "id", "title", "description", "layout_config", "is_public",
            "owner", "data_sources", "widgets", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def create(self, validated_data):
        data_sources = validated_data.pop("data_sources", [])
        validated_data["owner"] = self.context["request"].user
        dashboard = Dashboard.objects.create(**validated_data)
        dashboard.data_sources.set(data_sources)
        return dashboard


class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = [
            "id", "event_type", "source", "payload",
            "metadata", "timestamp", "processed", "created_at",
        ]
        read_only_fields = ["id", "processed", "created_at"]


class AlertSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id", "name", "description", "condition_config", "severity",
            "is_active", "owner", "dashboard", "last_triggered",
            "trigger_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "last_triggered", "trigger_count", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class ReportSerializer(serializers.ModelSerializer):
    generated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Report
        fields = [
            "id", "title", "dashboard", "generated_by",
            "format", "file_url", "ai_summary", "created_at",
        ]
        read_only_fields = ["id", "generated_by", "file_url", "ai_summary", "created_at"]

    def create(self, validated_data):
        validated_data["generated_by"] = self.context["request"].user
        return super().create(validated_data)


class DashboardSummarySerializer(serializers.Serializer):
    total_events = serializers.IntegerField()
    active_sources = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    recent_events = AnalyticsEventSerializer(many=True)
