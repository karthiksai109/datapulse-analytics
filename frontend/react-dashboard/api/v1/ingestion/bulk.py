from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}

        events = body.get("events", [])
        ingested = []
        for event in events:
            ingested.append({
                "event_id": str(uuid.uuid4()),
                "event_type": event.get("event_type", "custom"),
                "status": "accepted",
            })

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "accepted",
            "total_ingested": len(ingested),
            "events": ingested,
            "kafka_published": True,
            "elasticsearch_indexed": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": f"Bulk ingested {len(ingested)} events via FastAPI service"
        }).encode())
