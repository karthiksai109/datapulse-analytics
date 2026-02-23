from http.server import BaseHTTPRequestHandler
import json
import uuid
import time
import hashlib


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

        username = body.get("username", "newuser")
        email = body.get("email", f"{username}@datapulse.dev")
        payload = f"{username}:{time.time()}:{uuid.uuid4()}"
        token = hashlib.sha256(payload.encode()).hexdigest()

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "access": token,
            "refresh": hashlib.sha256((payload + "_r").encode()).hexdigest(),
            "user": {
                "id": str(uuid.uuid4()),
                "username": username,
                "email": email,
                "first_name": body.get("first_name", ""),
                "last_name": body.get("last_name", ""),
                "role": "viewer",
                "organization": "",
            }
        }).encode())
