from http.server import BaseHTTPRequestHandler
import json
import hashlib
import time
import uuid
import secrets
from urllib.parse import urlparse


DEMO_USER = {
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
}


def generate_token(seed):
    payload = f"{seed}:{time.time()}:{uuid.uuid4()}"
    return hashlib.sha256(payload.encode()).hexdigest()


def get_path(full_path):
    parsed = urlparse(full_path)
    path = parsed.path.rstrip("/")
    # Extract the part after /api/v1/users/
    parts = path.split("/api/v1/users/")
    return parts[-1] if len(parts) > 1 else ""


def handle_login(body):
    username = body.get("username", "demo")
    return 200, {
        "access": generate_token(username),
        "refresh": generate_token(username + "_refresh"),
        "user": {**DEMO_USER, "username": username, "email": f"{username}@datapulse.dev"},
    }


def handle_register(body):
    username = body.get("username", "newuser")
    return 201, {
        "access": generate_token(username),
        "refresh": generate_token(username + "_refresh"),
        "user": {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": body.get("email", f"{username}@datapulse.dev"),
            "first_name": body.get("first_name", ""),
            "last_name": body.get("last_name", ""),
            "role": "viewer",
            "organization": "",
        },
    }


def handle_profile_get():
    return 200, DEMO_USER


def handle_profile_update(body):
    updated = {**DEMO_USER}
    for key in ["first_name", "last_name", "email", "bio", "organization"]:
        if key in body:
            updated[key] = body[key]
    return 200, updated


def handle_change_password():
    return 200, {"detail": "Password updated successfully."}


def handle_api_key():
    return 200, {"api_key": "dp_" + secrets.token_hex(32)}


def handle_stats():
    import random
    return 200, {
        "dashboards": 3,
        "events_today": random.randint(200, 500),
        "active_alerts": 3,
        "reports_generated": 3,
    }


def handle_token_refresh():
    return 200, {"access": generate_token("refreshed")}


class handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
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

    def _route(self, method):
        path = get_path(self.path)
        body = self._read_body() if method in ("POST", "PUT", "PATCH") else {}

        if path == "login" and method == "POST":
            return self._respond(*handle_login(body))
        elif path == "register" and method == "POST":
            return self._respond(*handle_register(body))
        elif path == "profile" and method == "GET":
            return self._respond(*handle_profile_get())
        elif path == "profile" and method in ("PUT", "PATCH"):
            return self._respond(*handle_profile_update(body))
        elif path == "change-password" and method == "PUT":
            return self._respond(*handle_change_password())
        elif path == "api-key" and method == "POST":
            return self._respond(*handle_api_key())
        elif path == "stats" and method == "GET":
            return self._respond(*handle_stats())
        elif path == "token/refresh" and method == "POST":
            return self._respond(*handle_token_refresh())
        else:
            return self._respond(200, {"service": "DataPulse Django Users API", "path": path, "method": method})

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_PATCH(self):
        self._route("PATCH")
