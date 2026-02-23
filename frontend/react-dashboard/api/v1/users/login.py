from http.server import BaseHTTPRequestHandler
import json
import hashlib
import time
import uuid

# In-memory user store for demo (Vercel serverless is stateless, so this resets)
DEMO_USERS = {
    "demo": {
        "id": str(uuid.uuid4()),
        "username": "demo",
        "email": "demo@datapulse.dev",
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "first_name": "Karthik",
        "last_name": "Ramadugu",
        "role": "admin",
        "organization": "DataPulse Analytics",
        "bio": "Full-stack developer specializing in Python, Django, FastAPI, Flask, and React",
    }
}


def generate_token(username):
    payload = f"{username}:{time.time()}:{uuid.uuid4()}"
    return hashlib.sha256(payload.encode()).hexdigest()


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

        username = body.get("username", "")
        password = body.get("password", "")

        # Accept demo credentials or any user
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = DEMO_USERS.get(username)

        if user and user["password_hash"] == password_hash:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "access": generate_token(username),
                "refresh": generate_token(username + "_refresh"),
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "role": user["role"],
                    "organization": user["organization"],
                }
            }).encode())
        else:
            # Auto-accept any credentials for demo purposes
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "access": generate_token(username or "user"),
                "refresh": generate_token((username or "user") + "_refresh"),
                "user": {
                    "id": str(uuid.uuid4()),
                    "username": username or "demo",
                    "email": f"{username or 'demo'}@datapulse.dev",
                    "first_name": "Karthik",
                    "last_name": "Ramadugu",
                    "role": "admin",
                    "organization": "DataPulse Analytics",
                }
            }).encode())
