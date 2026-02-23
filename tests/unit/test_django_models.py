import uuid
from datetime import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from analytics.models import DataSource, Dashboard, Widget, AnalyticsEvent, Alert, Report

User = get_user_model()


class DataSourceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@datapulse.dev"
        )
        self.source = DataSource.objects.create(
            name="Test API Source",
            source_type="api",
            created_by=self.user,
        )

    def test_create_data_source(self):
        self.assertEqual(self.source.name, "Test API Source")
        self.assertEqual(self.source.source_type, "api")
        self.assertTrue(self.source.is_active)
        self.assertIsInstance(self.source.id, uuid.UUID)

    def test_data_source_str(self):
        self.assertEqual(str(self.source), "Test API Source (REST API)")

    def test_data_source_toggle(self):
        self.source.is_active = False
        self.source.save()
        self.source.refresh_from_db()
        self.assertFalse(self.source.is_active)


class DashboardModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dashuser", password="testpass123"
        )
        self.dashboard = Dashboard.objects.create(
            title="Sales Dashboard",
            description="Real-time sales metrics",
            owner=self.user,
        )

    def test_create_dashboard(self):
        self.assertEqual(self.dashboard.title, "Sales Dashboard")
        self.assertFalse(self.dashboard.is_public)
        self.assertEqual(self.dashboard.owner, self.user)

    def test_dashboard_str(self):
        self.assertEqual(str(self.dashboard), "Sales Dashboard")

    def test_dashboard_with_widgets(self):
        widget = Widget.objects.create(
            dashboard=self.dashboard,
            title="Revenue Chart",
            widget_type="line_chart",
        )
        self.assertEqual(self.dashboard.widgets.count(), 1)
        self.assertEqual(widget.dashboard, self.dashboard)


class AnalyticsEventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="eventuser", password="testpass123"
        )
        self.source = DataSource.objects.create(
            name="Event Source", source_type="webhook", created_by=self.user
        )

    def test_create_event(self):
        event = AnalyticsEvent.objects.create(
            event_type="page_view",
            source=self.source,
            payload={"page": "/dashboard", "duration": 3.5},
            timestamp=datetime.now(),
        )
        self.assertEqual(event.event_type, "page_view")
        self.assertFalse(event.processed)
        self.assertEqual(event.payload["page"], "/dashboard")

    def test_event_ordering(self):
        from django.utils import timezone
        e1 = AnalyticsEvent.objects.create(
            event_type="first", timestamp=timezone.now(), source=self.source
        )
        e2 = AnalyticsEvent.objects.create(
            event_type="second", timestamp=timezone.now(), source=self.source
        )
        events = list(AnalyticsEvent.objects.all())
        self.assertEqual(events[0].event_type, "second")


class AlertModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alertuser", password="testpass123"
        )

    def test_create_alert(self):
        alert = Alert.objects.create(
            name="High CPU Alert",
            severity="high",
            condition_config={"event_type": "cpu_usage", "field": "value", "operator": "gt", "threshold": 90},
            owner=self.user,
        )
        self.assertEqual(alert.name, "High CPU Alert")
        self.assertEqual(alert.severity, "high")
        self.assertTrue(alert.is_active)
        self.assertEqual(alert.trigger_count, 0)
