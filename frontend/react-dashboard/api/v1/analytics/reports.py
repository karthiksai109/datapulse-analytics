from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime


DEMO_REPORTS = [
    {"id": str(uuid.uuid4()), "title": "Weekly Analytics Summary", "dashboard": None, "generated_by": "demo", "format": "pdf", "file_url": "", "ai_summary": "Dashboard 'Main Analytics' analysis: 1,247 events processed from 5 active sources. Key trends show 23% increase in user engagement and 15% improvement in conversion rates. Recommendation: Focus on optimizing API response times.", "created_at": "2026-02-23T10:00:00Z"},
    {"id": str(uuid.uuid4()), "title": "Monthly Revenue Report", "dashboard": None, "generated_by": "demo", "format": "csv", "file_url": "", "ai_summary": "Revenue analysis shows steady growth of 18% MoM. Top performing segments: Enterprise (42%), SMB (35%), Individual (23%). Alert: 3 data sources showing intermittent connectivity.", "created_at": "2026-02-20T08:00:00Z"},
    {"id": str(uuid.uuid4()), "title": "Error Analysis Q1", "dashboard": None, "generated_by": "demo", "format": "json", "file_url": "", "ai_summary": "Error rate analysis: Overall error rate at 2.3%, down from 3.1% last quarter. Most common: timeout errors (45%), validation errors (30%), auth errors (25%). Recommendation: Implement retry logic for timeout-prone endpoints.", "created_at": "2026-02-15T14:00:00Z"},
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
        self.wfile.write(json.dumps(DEMO_REPORTS).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}
        report = {
            "id": str(uuid.uuid4()),
            "title": body.get("title", "New Report"),
            "dashboard": body.get("dashboard"),
            "generated_by": "demo",
            "format": body.get("format", "pdf"),
            "file_url": "",
            "ai_summary": f"Report '{body.get('title', 'New Report')}' generated. Analysis of dashboard data shows normal patterns with no critical anomalies detected.",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(report).encode())
