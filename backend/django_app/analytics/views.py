import logging
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import DataSource, Dashboard, Widget, AnalyticsEvent, Alert, Report
from .serializers import (
    DataSourceSerializer,
    DashboardSerializer,
    WidgetSerializer,
    AnalyticsEventSerializer,
    AlertSerializer,
    ReportSerializer,
    DashboardSummarySerializer,
)
from .tasks import process_analytics_event, generate_report_task
from .services.kafka_producer import publish_event
from .services.elasticsearch_service import search_events

logger = logging.getLogger("analytics")


class DataSourceViewSet(viewsets.ModelViewSet):
    serializer_class = DataSourceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["source_type", "is_active"]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        return DataSource.objects.filter(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        source = self.get_object()
        source.is_active = not source.is_active
        source.save(update_fields=["is_active"])
        logger.info(f"DataSource {source.id} toggled to {'active' if source.is_active else 'inactive'}")
        return Response(DataSourceSerializer(source).data)

    @action(detail=True, methods=["post"])
    def test_connection(self, request, pk=None):
        source = self.get_object()
        # Simulate connection test
        logger.info(f"Testing connection for DataSource {source.id}")
        return Response({"status": "connected", "latency_ms": 45})


class DashboardViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["is_public"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        user = self.request.user
        return Dashboard.objects.filter(owner=user) | Dashboard.objects.filter(is_public=True)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        dashboard = self.get_object()
        sources = dashboard.data_sources.filter(is_active=True)
        recent_events = AnalyticsEvent.objects.filter(
            source__in=sources
        ).order_by("-timestamp")[:10]

        data = {
            "total_events": AnalyticsEvent.objects.filter(source__in=sources).count(),
            "active_sources": sources.count(),
            "active_alerts": Alert.objects.filter(dashboard=dashboard, is_active=True).count(),
            "recent_events": AnalyticsEventSerializer(recent_events, many=True).data,
        }
        return Response(data)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        dashboard = self.get_object()
        new_dashboard = Dashboard.objects.create(
            title=f"{dashboard.title} (Copy)",
            description=dashboard.description,
            layout_config=dashboard.layout_config,
            is_public=False,
            owner=request.user,
        )
        new_dashboard.data_sources.set(dashboard.data_sources.all())

        for widget in dashboard.widgets.all():
            Widget.objects.create(
                dashboard=new_dashboard,
                title=widget.title,
                widget_type=widget.widget_type,
                query_config=widget.query_config,
                position_x=widget.position_x,
                position_y=widget.position_y,
                width=widget.width,
                height=widget.height,
                refresh_interval=widget.refresh_interval,
            )

        logger.info(f"Dashboard {dashboard.id} duplicated as {new_dashboard.id}")
        return Response(DashboardSerializer(new_dashboard).data, status=status.HTTP_201_CREATED)


class WidgetViewSet(viewsets.ModelViewSet):
    serializer_class = WidgetSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["dashboard", "widget_type"]

    def get_queryset(self):
        return Widget.objects.filter(dashboard__owner=self.request.user)


class AnalyticsEventViewSet(viewsets.ModelViewSet):
    serializer_class = AnalyticsEventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["event_type", "processed"]
    search_fields = ["event_type"]
    ordering_fields = ["timestamp"]
    http_method_names = ["get", "post", "head"]

    def get_queryset(self):
        return AnalyticsEvent.objects.filter(
            source__created_by=self.request.user
        )

    def perform_create(self, serializer):
        event = serializer.save()
        # Publish to Kafka for real-time processing
        publish_event(event)
        # Queue async processing via RabbitMQ/Celery
        process_analytics_event.delay(str(event.id))
        logger.info(f"Event {event.id} created and queued for processing")

    @action(detail=False, methods=["post"])
    def bulk_ingest(self, request):
        events_data = request.data.get("events", [])
        if not events_data:
            return Response(
                {"error": "No events provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsEventSerializer(data=events_data, many=True)
        serializer.is_valid(raise_exception=True)
        events = serializer.save()

        for event in events:
            publish_event(event)
            process_analytics_event.delay(str(event.id))

        logger.info(f"Bulk ingested {len(events)} events")
        return Response(
            {"ingested": len(events)},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = search_events(query, request.user)
        return Response(results)


class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["severity", "is_active"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        return Alert.objects.filter(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.is_active = False
        alert.save(update_fields=["is_active"])
        logger.info(f"Alert {alert.id} acknowledged by {request.user}")
        return Response(AlertSerializer(alert).data)


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["dashboard", "format"]
    ordering_fields = ["created_at"]
    http_method_names = ["get", "post", "head", "delete"]

    def get_queryset(self):
        return Report.objects.filter(generated_by=self.request.user)

    def perform_create(self, serializer):
        report = serializer.save()
        generate_report_task.delay(str(report.id))
        logger.info(f"Report {report.id} generation queued")
