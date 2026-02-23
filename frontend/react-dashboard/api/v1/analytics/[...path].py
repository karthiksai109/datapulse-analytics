from http.server import BaseHTTPRequestHandler
import json
import uuid
import random
from datetime import datetime, timedelta
from urllib.parse import urlparse

EVENT_TYPES = ["page_view", "click", "purchase", "signup", "api_call", "error", "login", "search"]

DEMO_SOURCES = [
    {"id": str(uuid.uuid4()), "name": "Production API", "source_type": "api", "is_active": True, "connection_config": {"url": "https://api.example.com"}, "created_by": "demo", "created_at": "2026-01-15T10:00:00Z", "updated_at": "2026-02-20T14:30:00Z"},
    {"id": str(uuid.uuid4()), "name": "User Events Webhook", "source_type": "webhook", "is_active": True, "connection_config": {"endpoint": "/webhooks/events"}, "created_by": "demo", "created_at": "2026-01-20T09:00:00Z", "updated_at": "2026-02-18T11:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "Sales Database", "source_type": "database", "is_active": False, "connection_config": {"host": "db.example.com", "port": 5432}, "created_by": "demo", "created_at": "2026-02-01T08:00:00Z", "updated_at": "2026-02-22T16:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "Clickstream Data", "source_type": "streaming", "is_active": True, "connection_config": {"topic": "clickstream"}, "created_by": "demo", "created_at": "2026-02-10T12:00:00Z", "updated_at": "2026-02-23T09:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "Monthly CSV Upload", "source_type": "csv", "is_active": True, "connection_config": {"delimiter": ","}, "created_by": "demo", "created_at": "2026-02-15T07:00:00Z", "updated_at": "2026-02-23T10:00:00Z"},
]

DEMO_DASHBOARDS = [
    {"id": str(uuid.uuid4()), "title": "Main Analytics", "description": "Primary analytics dashboard", "layout_config": {}, "is_public": True, "owner": "demo", "data_sources": [], "widgets": [], "created_at": "2026-01-10T08:00:00Z", "updated_at": "2026-02-23T12:00:00Z"},
    {"id": str(uuid.uuid4()), "title": "Sales Performance", "description": "Revenue and conversion tracking", "layout_config": {}, "is_public": False, "owner": "demo", "data_sources": [], "widgets": [], "created_at": "2026-01-25T10:00:00Z", "updated_at": "2026-02-22T15:00:00Z"},
    {"id": str(uuid.uuid4()), "title": "User Engagement", "description": "User behavior and retention metrics", "layout_config": {}, "is_public": True, "owner": "demo", "data_sources": [], "widgets": [], "created_at": "2026-02-05T09:00:00Z", "updated_at": "2026-02-21T11:00:00Z"},
]

DEMO_ALERTS = [
    {"id": str(uuid.uuid4()), "name": "High Error Rate", "description": "Triggered when error rate exceeds 5%", "condition_config": {"event_type": "error", "threshold": 5, "operator": "gt", "field": "value"}, "severity": "critical", "is_active": True, "owner": "demo", "dashboard": None, "last_triggered": "2026-02-23T14:30:00Z", "trigger_count": 12, "created_at": "2026-01-15T10:00:00Z", "updated_at": "2026-02-23T14:30:00Z"},
    {"id": str(uuid.uuid4()), "name": "Low Conversion", "description": "Conversion rate dropped below threshold", "condition_config": {"event_type": "purchase", "threshold": 2, "operator": "lt", "field": "value"}, "severity": "high", "is_active": True, "owner": "demo", "dashboard": None, "last_triggered": "2026-02-22T09:00:00Z", "trigger_count": 5, "created_at": "2026-01-20T08:00:00Z", "updated_at": "2026-02-22T09:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "Spike in Traffic", "description": "Unusual traffic spike detected", "condition_config": {"event_type": "page_view", "threshold": 10000, "operator": "gt", "field": "value"}, "severity": "medium", "is_active": False, "owner": "demo", "dashboard": None, "last_triggered": "2026-02-20T16:00:00Z", "trigger_count": 3, "created_at": "2026-02-01T12:00:00Z", "updated_at": "2026-02-20T16:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "API Latency Warning", "description": "API response time exceeds 2 seconds", "condition_config": {"event_type": "api_call", "threshold": 2000, "operator": "gt", "field": "duration_ms"}, "severity": "low", "is_active": True, "owner": "demo", "dashboard": None, "last_triggered": None, "trigger_count": 0, "created_at": "2026-02-10T14:00:00Z", "updated_at": "2026-02-10T14:00:00Z"},
]

DEMO_REPORTS = [
    {"id": str(uuid.uuid4()), "title": "Weekly Analytics Summary", "dashboard": None, "generated_by": "demo", "format": "pdf", "file_url": "", "ai_summary": "Dashboard 'Main Analytics' analysis: 1,247 events processed from 5 active sources. Key trends show 23% increase in user engagement.", "created_at": "2026-02-23T10:00:00Z"},
    {"id": str(uuid.uuid4()), "title": "Monthly Revenue Report", "dashboard": None, "generated_by": "demo", "format": "csv", "file_url": "", "ai_summary": "Revenue analysis shows steady growth of 18% MoM. Top performing segments: Enterprise (42%), SMB (35%).", "created_at": "2026-02-20T08:00:00Z"},
    {"id": str(uuid.uuid4()), "title": "Error Analysis Q1", "dashboard": None, "generated_by": "demo", "format": "json", "file_url": "", "ai_summary": "Error rate analysis: Overall error rate at 2.3%, down from 3.1% last quarter.", "created_at": "2026-02-15T14:00:00Z"},
]


def generate_events(count=50):
    events = []
    now = datetime.utcnow()
    for i in range(count):
        ts = now - timedelta(hours=random.randint(0, 168))
        etype = random.choice(EVENT_TYPES)
        events.append({
            "id": str(uuid.uuid4()), "event_type": etype, "source": None,
            "payload": {"value": random.randint(1, 1000), "page": f"/page/{random.randint(1,20)}", "duration_ms": random.randint(50, 5000)},
            "metadata": {"ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"},
            "timestamp": ts.isoformat() + "Z", "processed": random.choice([True, False]),
            "created_at": ts.isoformat() + "Z",
        })
    return sorted(events, key=lambda e: e["timestamp"], reverse=True)


def get_path(full_path):
    parsed = urlparse(full_path)
    path = parsed.path.rstrip("/")
    parts = path.split("/api/v1/analytics/")
    return parts[-1] if len(parts) > 1 else ""


class handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def _respond(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _route(self, method):
        path = get_path(self.path)
        body = self._read_body() if method in ("POST", "PUT", "PATCH") else {}

        if path.startswith("sources") and method == "GET":
            return self._respond(200, DEMO_SOURCES)
        elif path.startswith("sources") and method == "POST":
            new = {"id": str(uuid.uuid4()), "name": body.get("name", "New Source"), "source_type": body.get("source_type", "api"), "is_active": True, "connection_config": body.get("connection_config", {}), "created_by": "demo", "created_at": datetime.utcnow().isoformat() + "Z", "updated_at": datetime.utcnow().isoformat() + "Z"}
            return self._respond(201, new)
        elif path.startswith("events") and method == "GET":
            return self._respond(200, generate_events())
        elif path.startswith("events") and method == "POST":
            event = {"id": str(uuid.uuid4()), "event_type": body.get("event_type", "custom"), "source": body.get("source"), "payload": body.get("payload", {}), "metadata": body.get("metadata", {}), "timestamp": body.get("timestamp", datetime.utcnow().isoformat() + "Z"), "processed": False, "created_at": datetime.utcnow().isoformat() + "Z"}
            return self._respond(201, event)
        elif path.startswith("dashboards") and method == "GET":
            return self._respond(200, DEMO_DASHBOARDS)
        elif path.startswith("dashboards") and method == "POST":
            dash = {"id": str(uuid.uuid4()), "title": body.get("title", "New Dashboard"), "description": body.get("description", ""), "layout_config": {}, "is_public": False, "owner": "demo", "data_sources": [], "widgets": [], "created_at": datetime.utcnow().isoformat() + "Z", "updated_at": datetime.utcnow().isoformat() + "Z"}
            return self._respond(201, dash)
        elif path.startswith("alerts") and method == "GET":
            return self._respond(200, DEMO_ALERTS)
        elif path.startswith("alerts") and method == "POST":
            alert = {"id": str(uuid.uuid4()), "name": body.get("name", "New Alert"), "description": body.get("description", ""), "condition_config": body.get("condition_config", {}), "severity": body.get("severity", "medium"), "is_active": True, "owner": "demo", "dashboard": None, "last_triggered": None, "trigger_count": 0, "created_at": datetime.utcnow().isoformat() + "Z", "updated_at": datetime.utcnow().isoformat() + "Z"}
            return self._respond(201, alert)
        elif path.startswith("reports") and method == "GET":
            return self._respond(200, DEMO_REPORTS)
        elif path.startswith("reports") and method == "POST":
            report = {"id": str(uuid.uuid4()), "title": body.get("title", "New Report"), "dashboard": body.get("dashboard"), "generated_by": "demo", "format": body.get("format", "pdf"), "file_url": "", "ai_summary": f"Report generated. Analysis shows normal patterns.", "created_at": datetime.utcnow().isoformat() + "Z"}
            return self._respond(201, report)
        elif path.startswith("stats"):
            return self._respond(200, {"total_events": random.randint(12000, 15000), "active_sources": 5, "active_alerts": 3, "total_dashboards": 3})
        else:
            return self._respond(200, {"service": "DataPulse Django Analytics API", "path": path})

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_PATCH(self):
        self._route("PATCH")
