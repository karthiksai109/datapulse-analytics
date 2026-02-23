from http.server import BaseHTTPRequestHandler
import json
import uuid


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "id": str(uuid.uuid4()),
            "username": "demo",
            "email": "demo@datapulse.dev",
            "first_name": "Karthik",
            "last_name": "Ramadugu",
            "role": "admin",
            "organization": "DataPulse Analytics",
            "bio": "Full-stack developer specializing in Python, Django, FastAPI, Flask, and React",
            "avatar_url": "",
            "last_active": "2026-02-23T20:00:00Z",
        }).encode())

    def do_PUT(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {
            "id": str(uuid.uuid4()),
            "username": body.get("username", "demo"),
            "email": body.get("email", "demo@datapulse.dev"),
            "first_name": body.get("first_name", "Karthik"),
            "last_name": body.get("last_name", "Ramadugu"),
            "role": body.get("role", "admin"),
            "organization": body.get("organization", "DataPulse Analytics"),
            "bio": body.get("bio", ""),
        }
        self.wfile.write(json.dumps(response).encode())
