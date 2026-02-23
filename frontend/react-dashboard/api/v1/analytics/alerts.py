from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime


DEMO_ALERTS = [
    {"id": str(uuid.uuid4()), "name": "High Error Rate", "description": "Triggered when error rate exceeds 5%", "condition_config": {"event_type": "error", "threshold": 5, "operator": "gt", "field": "value"}, "severity": "critical", "is_active": True, "owner": "demo", "dashboard": None, "last_triggered": "2026-02-23T14:30:00Z", "trigger_count": 12, "created_at": "2026-01-15T10:00:00Z", "updated_at": "2026-02-23T14:30:00Z"},
    {"id": str(uuid.uuid4()), "name": "Low Conversion", "description": "Conversion rate dropped below threshold", "condition_config": {"event_type": "purchase", "threshold": 2, "operator": "lt", "field": "value"}, "severity": "high", "is_active": True, "owner": "demo", "dashboard": None, "last_triggered": "2026-02-22T09:00:00Z", "trigger_count": 5, "created_at": "2026-01-20T08:00:00Z", "updated_at": "2026-02-22T09:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "Spike in Traffic", "description": "Unusual traffic spike detected", "condition_config": {"event_type": "page_view", "threshold": 10000, "operator": "gt", "field": "value"}, "severity": "medium", "is_active": False, "owner": "demo", "dashboard": None, "last_triggered": "2026-02-20T16:00:00Z", "trigger_count": 3, "created_at": "2026-02-01T12:00:00Z", "updated_at": "2026-02-20T16:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "API Latency Warning", "description": "API response time exceeds 2 seconds", "condition_config": {"event_type": "api_call", "threshold": 2000, "operator": "gt", "field": "duration_ms"}, "severity": "low", "is_active": True, "owner": "demo", "dashboard": None, "last_triggered": None, "trigger_count": 0, "created_at": "2026-02-10T14:00:00Z", "updated_at": "2026-02-10T14:00:00Z"},
]


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(DEMO_ALERTS).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}
        alert = {
            "id": str(uuid.uuid4()),
            "name": body.get("name", "New Alert"),
            "description": body.get("description", ""),
            "condition_config": body.get("condition_config", {}),
            "severity": body.get("severity", "medium"),
            "is_active": True,
            "owner": "demo",
            "dashboard": body.get("dashboard"),
            "last_triggered": None,
            "trigger_count": 0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(alert).encode())
