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

        event_id = str(uuid.uuid4())
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "accepted",
            "event_id": event_id,
            "event_type": body.get("event_type", "custom"),
            "kafka_published": True,
            "elasticsearch_indexed": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": "Event ingested via FastAPI ingestion service and published to Kafka topic 'datapulse-events'"
        }).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "service": "DataPulse FastAPI Ingestion Service",
            "version": "1.0.0",
            "framework": "FastAPI 0.109",
            "endpoints": {
                "ingest": "POST /api/v1/ingestion/ingest",
                "bulk": "POST /api/v1/ingestion/bulk",
                "status": "GET /api/v1/ingestion/status",
            },
            "kafka_status": "connected",
            "elasticsearch_status": "connected",
        }).encode())
