from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime


DEMO_DASHBOARDS = [
    {"id": str(uuid.uuid4()), "title": "Main Analytics", "description": "Primary analytics dashboard with key metrics", "layout_config": {}, "is_public": True, "owner": "demo", "data_sources": [], "widgets": [], "created_at": "2026-01-10T08:00:00Z", "updated_at": "2026-02-23T12:00:00Z"},
    {"id": str(uuid.uuid4()), "title": "Sales Performance", "description": "Revenue and conversion tracking", "layout_config": {}, "is_public": False, "owner": "demo", "data_sources": [], "widgets": [], "created_at": "2026-01-25T10:00:00Z", "updated_at": "2026-02-22T15:00:00Z"},
    {"id": str(uuid.uuid4()), "title": "User Engagement", "description": "User behavior and retention metrics", "layout_config": {}, "is_public": True, "owner": "demo", "data_sources": [], "widgets": [], "created_at": "2026-02-05T09:00:00Z", "updated_at": "2026-02-21T11:00:00Z"},
]


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(DEMO_DASHBOARDS).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}
        dashboard = {
            "id": str(uuid.uuid4()),
            "title": body.get("title", "New Dashboard"),
            "description": body.get("description", ""),
            "layout_config": body.get("layout_config", {}),
            "is_public": body.get("is_public", False),
            "owner": "demo",
            "data_sources": [],
            "widgets": [],
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(dashboard).encode())
