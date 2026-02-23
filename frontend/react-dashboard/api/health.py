from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "healthy",
            "services": {
                "django": {"status": "running", "framework": "Django 4.2", "type": "REST API"},
                "fastapi": {"status": "running", "framework": "FastAPI 0.109", "type": "Ingestion Service"},
                "flask": {"status": "running", "framework": "Flask 3.0", "type": "AI Service"},
            },
            "version": "1.0.0",
            "platform": "Vercel Serverless"
        }).encode())
