from http.server import BaseHTTPRequestHandler
import json
import random


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "total_events": random.randint(12000, 15000),
            "active_sources": 5,
            "active_alerts": 3,
            "total_dashboards": 3,
            "events_today": random.randint(200, 500),
            "error_rate": round(random.uniform(1.0, 3.0), 1),
            "avg_response_ms": random.randint(180, 320),
            "uptime_percent": round(random.uniform(99.5, 99.99), 2),
        }).encode())
