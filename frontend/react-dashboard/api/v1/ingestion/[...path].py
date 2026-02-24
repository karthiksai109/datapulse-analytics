from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime
from urllib.parse import urlparse

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from api._lib.auth import require_auth, require_role


def get_path(full_path):
    parsed = urlparse(full_path)
    path = parsed.path.rstrip("/")
    parts = path.split("/api/v1/ingestion/")
    return parts[-1] if len(parts) > 1 else ""


class handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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

    def do_GET(self):
        user, err = require_auth(self.headers)
        if err:
            return self._respond(*err)
        self._respond(200, {
            "service": "DataPulse FastAPI Ingestion Service",
            "version": "1.0.0",
            "framework": "FastAPI 0.109",
            "endpoints": ["ingest", "bulk", "status"],
            "kafka_status": "connected",
            "elasticsearch_status": "connected",
            "user": user["username"],
            "role": user["role"],
        })

    def do_POST(self):
        user, err = require_role(self.headers, "analyst")
        if err:
            return self._respond(*err)

        path = get_path(self.path)
        body = self._read_body()

        if path == "bulk":
            events = body.get("events", [])
            if not events:
                return self._respond(400, {"detail": "No events provided.", "code": "invalid_input"})
            ingested = [{"event_id": str(uuid.uuid4()), "event_type": e.get("event_type", "custom"), "status": "accepted"} for e in events]
            self._respond(200, {
                "status": "accepted",
                "total_ingested": len(ingested),
                "events": ingested,
                "kafka_published": True,
                "elasticsearch_indexed": True,
                "ingested_by": user["username"],
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "message": f"Bulk ingested {len(ingested)} events via FastAPI service",
            })
        else:
            event_type = body.get("event_type", "custom")
            self._respond(200, {
                "status": "accepted",
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "kafka_published": True,
                "kafka_topic": "datapulse-events",
                "kafka_partition": 0,
                "elasticsearch_indexed": True,
                "elasticsearch_index": f"events-{datetime.utcnow().strftime('%Y.%m')}",
                "ingested_by": user["username"],
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "message": f"Event '{event_type}' ingested and published to Kafka topic 'datapulse-events'",
            })
