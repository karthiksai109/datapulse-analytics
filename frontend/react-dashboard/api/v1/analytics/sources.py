from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime

DEMO_SOURCES = [
    {"id": str(uuid.uuid4()), "name": "Production API", "source_type": "api", "is_active": True, "connection_config": {"url": "https://api.example.com", "method": "POST"}, "created_by": "demo", "created_at": "2026-01-15T10:00:00Z", "updated_at": "2026-02-20T14:30:00Z"},
    {"id": str(uuid.uuid4()), "name": "User Events Webhook", "source_type": "webhook", "is_active": True, "connection_config": {"endpoint": "/webhooks/events"}, "created_by": "demo", "created_at": "2026-01-20T09:00:00Z", "updated_at": "2026-02-18T11:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "Sales Database", "source_type": "database", "is_active": False, "connection_config": {"host": "db.example.com", "port": 5432}, "created_by": "demo", "created_at": "2026-02-01T08:00:00Z", "updated_at": "2026-02-22T16:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "Clickstream Data", "source_type": "streaming", "is_active": True, "connection_config": {"topic": "clickstream", "broker": "kafka:9092"}, "created_by": "demo", "created_at": "2026-02-10T12:00:00Z", "updated_at": "2026-02-23T09:00:00Z"},
    {"id": str(uuid.uuid4()), "name": "Monthly CSV Upload", "source_type": "csv", "is_active": True, "connection_config": {"delimiter": ",", "encoding": "utf-8"}, "created_by": "demo", "created_at": "2026-02-15T07:00:00Z", "updated_at": "2026-02-23T10:00:00Z"},
]


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(DEMO_SOURCES).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}
        new_source = {
            "id": str(uuid.uuid4()),
            "name": body.get("name", "New Source"),
            "source_type": body.get("source_type", "api"),
            "is_active": True,
            "connection_config": body.get("connection_config", {}),
            "created_by": "demo",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(new_source).encode())
