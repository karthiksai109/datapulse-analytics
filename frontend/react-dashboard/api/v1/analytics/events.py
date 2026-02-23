from http.server import BaseHTTPRequestHandler
import json
import uuid
import random
from datetime import datetime, timedelta

EVENT_TYPES = ["page_view", "click", "purchase", "signup", "api_call", "error", "login", "search"]

def generate_demo_events(count=50):
    events = []
    now = datetime.utcnow()
    for i in range(count):
        ts = now - timedelta(hours=random.randint(0, 168))
        etype = random.choice(EVENT_TYPES)
        events.append({
            "id": str(uuid.uuid4()),
            "event_type": etype,
            "source": None,
            "payload": {"value": random.randint(1, 1000), "page": f"/page/{random.randint(1,20)}", "duration_ms": random.randint(50, 5000)},
            "metadata": {"ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}", "user_agent": "Mozilla/5.0"},
            "timestamp": ts.isoformat() + "Z",
            "processed": random.choice([True, False]),
            "created_at": ts.isoformat() + "Z",
        })
    return sorted(events, key=lambda e: e["timestamp"], reverse=True)


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
        self.wfile.write(json.dumps(generate_demo_events()).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}
        event = {
            "id": str(uuid.uuid4()),
            "event_type": body.get("event_type", "custom"),
            "source": body.get("source"),
            "payload": body.get("payload", {}),
            "metadata": body.get("metadata", {}),
            "timestamp": body.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "processed": False,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(event).encode())
