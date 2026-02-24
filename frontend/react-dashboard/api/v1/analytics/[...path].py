from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime
from urllib.parse import urlparse

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from api._lib.auth import require_auth, require_role, has_permission
from api._lib.data import SOURCES, DASHBOARDS, ALERTS, REPORTS, generate_events, get_dashboard_stats


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

    def _auth(self, min_role="viewer"):
        user, err = require_role(self.headers, min_role)
        if err:
            self._respond(*err)
            return None
        return user

    # ─── Sources ────────────────────────────────────────────────────
    def _handle_sources_get(self, user):
        return self._respond(200, {
            "count": len(SOURCES),
            "results": SOURCES,
        })

    def _handle_sources_post(self, user, body):
        if not has_permission(user["role"], "manage:sources"):
            return self._respond(403, {"detail": "You don't have permission to create data sources.", "code": "permission_denied"})
        name = body.get("name", "").strip()
        if not name:
            return self._respond(400, {"detail": "Source name is required.", "code": "invalid_input"})
        new = {
            "id": str(uuid.uuid4()),
            "name": name,
            "source_type": body.get("source_type", "api"),
            "is_active": True,
            "connection_config": body.get("connection_config", {}),
            "created_by": user["sub"],
            "events_count": 0,
            "last_sync": None,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        return self._respond(201, new)

    # ─── Events ─────────────────────────────────────────────────────
    def _handle_events_get(self, user):
        events = generate_events(100)
        return self._respond(200, {
            "count": len(events),
            "results": events,
        })

    def _handle_events_post(self, user, body):
        if not has_permission(user["role"], "write:events"):
            return self._respond(403, {"detail": "You don't have permission to create events.", "code": "permission_denied"})
        event = {
            "id": str(uuid.uuid4()),
            "event_type": body.get("event_type", "custom"),
            "source": body.get("source"),
            "source_name": "Manual Entry",
            "payload": body.get("payload", {}),
            "metadata": body.get("metadata", {}),
            "timestamp": body.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "processed": False,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        return self._respond(201, event)

    # ─── Dashboards ─────────────────────────────────────────────────
    def _handle_dashboards_get(self, user):
        role = user.get("role", "viewer")
        if role == "viewer":
            visible = [d for d in DASHBOARDS if d["is_public"]]
        else:
            visible = DASHBOARDS
        return self._respond(200, {
            "count": len(visible),
            "results": visible,
        })

    def _handle_dashboards_post(self, user, body):
        if not has_permission(user["role"], "manage:dashboards"):
            return self._respond(403, {"detail": "You don't have permission to create dashboards.", "code": "permission_denied"})
        title = body.get("title", "").strip()
        if not title:
            return self._respond(400, {"detail": "Dashboard title is required.", "code": "invalid_input"})
        dash = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": body.get("description", ""),
            "layout_config": body.get("layout_config", {"columns": 3, "rows": 3}),
            "is_public": body.get("is_public", False),
            "owner": user["sub"],
            "data_sources": [],
            "widget_count": 0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        return self._respond(201, dash)

    # ─── Alerts ─────────────────────────────────────────────────────
    def _handle_alerts_get(self, user):
        return self._respond(200, {
            "count": len(ALERTS),
            "results": ALERTS,
        })

    def _handle_alerts_post(self, user, body):
        if not has_permission(user["role"], "manage:alerts"):
            return self._respond(403, {"detail": "You don't have permission to create alerts.", "code": "permission_denied"})
        name = body.get("name", "").strip()
        if not name:
            return self._respond(400, {"detail": "Alert name is required.", "code": "invalid_input"})
        alert = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": body.get("description", ""),
            "condition_config": body.get("condition_config", {}),
            "severity": body.get("severity", "medium"),
            "is_active": True,
            "owner": user["sub"],
            "dashboard": body.get("dashboard"),
            "last_triggered": None,
            "trigger_count": 0,
            "notification_channels": body.get("notification_channels", ["slack"]),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        return self._respond(201, alert)

    # ─── Reports ────────────────────────────────────────────────────
    def _handle_reports_get(self, user):
        return self._respond(200, {
            "count": len(REPORTS),
            "results": REPORTS,
        })

    def _handle_reports_post(self, user, body):
        if not has_permission(user["role"], "generate:reports"):
            return self._respond(403, {"detail": "You don't have permission to generate reports.", "code": "permission_denied"})
        title = body.get("title", "").strip()
        if not title:
            return self._respond(400, {"detail": "Report title is required.", "code": "invalid_input"})
        report = {
            "id": str(uuid.uuid4()),
            "title": title,
            "dashboard": body.get("dashboard"),
            "generated_by": user["sub"],
            "format": body.get("format", "pdf"),
            "file_url": "",
            "ai_summary": f"Generating AI summary for report '{title}'... Analysis of dashboard data shows normal operational patterns with key metrics within expected thresholds.",
            "status": "processing",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        return self._respond(201, report)

    # ─── Stats ──────────────────────────────────────────────────────
    def _handle_stats_get(self, user):
        return self._respond(200, get_dashboard_stats())

    # ─── Router ─────────────────────────────────────────────────────
    def _route(self, method):
        path = get_path(self.path)
        body = self._read_body() if method in ("POST", "PUT", "PATCH") else {}

        user = self._auth("viewer")
        if not user:
            return

        if path.startswith("sources") and method == "GET":
            return self._handle_sources_get(user)
        elif path.startswith("sources") and method == "POST":
            return self._handle_sources_post(user, body)
        elif path.startswith("events") and method == "GET":
            return self._handle_events_get(user)
        elif path.startswith("events") and method == "POST":
            return self._handle_events_post(user, body)
        elif path.startswith("dashboards") and method == "GET":
            return self._handle_dashboards_get(user)
        elif path.startswith("dashboards") and method == "POST":
            return self._handle_dashboards_post(user, body)
        elif path.startswith("alerts") and method == "GET":
            return self._handle_alerts_get(user)
        elif path.startswith("alerts") and method == "POST":
            return self._handle_alerts_post(user, body)
        elif path.startswith("reports") and method == "GET":
            return self._handle_reports_get(user)
        elif path.startswith("reports") and method == "POST":
            return self._handle_reports_post(user, body)
        elif path.startswith("stats"):
            return self._handle_stats_get(user)
        else:
            return self._respond(404, {"detail": f"Endpoint /analytics/{path} not found.", "code": "not_found"})

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_PATCH(self):
        self._route("PATCH")
