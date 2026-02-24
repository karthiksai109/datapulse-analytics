from http.server import BaseHTTPRequestHandler
import json
import secrets
import uuid
from urllib.parse import urlparse

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from api._lib.auth import (
    hash_password, verify_password, create_token, verify_token,
    require_auth, require_role, get_user_from_request, ROLES,
)
from api._lib.data import USERS, get_user_safe, find_user_by_id, get_dashboard_stats


def get_path(full_path):
    parsed = urlparse(full_path)
    path = parsed.path.rstrip("/")
    parts = path.split("/api/v1/users/")
    return parts[-1] if len(parts) > 1 else ""


def handle_login(body):
    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        return 400, {"detail": "Username and password are required.", "code": "invalid_input"}

    user = USERS.get(username)
    if not user:
        return 401, {"detail": "Invalid credentials. No account found for this username.", "code": "invalid_credentials"}

    if not verify_password(password, user["password_hash"]):
        return 401, {"detail": "Invalid credentials. Incorrect password.", "code": "invalid_credentials"}

    if not user.get("is_active", True):
        return 403, {"detail": "Account is deactivated. Contact an administrator.", "code": "account_inactive"}

    access = create_token(user["id"], user["username"], user["role"], "access")
    refresh = create_token(user["id"], user["username"], user["role"], "refresh")
    safe_user = get_user_safe(username)

    return 200, {
        "access": access,
        "refresh": refresh,
        "user": safe_user,
        "permissions": ROLES.get(user["role"], ROLES["viewer"])["permissions"],
    }


def handle_register(body):
    username = body.get("username", "").strip()
    email = body.get("email", "").strip()
    password = body.get("password", "")

    if not username or not password:
        return 400, {"detail": "Username and password are required.", "code": "invalid_input"}

    if username in USERS:
        return 409, {"detail": f"Username '{username}' is already taken.", "code": "username_exists"}

    new_user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "email": email or f"{username}@datapulse.dev",
        "first_name": body.get("first_name", ""),
        "last_name": body.get("last_name", ""),
        "role": "viewer",
        "organization": body.get("organization", ""),
        "bio": "",
        "avatar_url": "",
        "is_active": True,
    }

    access = create_token(new_user["id"], username, "viewer", "access")
    refresh = create_token(new_user["id"], username, "viewer", "refresh")

    return 201, {
        "access": access,
        "refresh": refresh,
        "user": new_user,
        "permissions": ROLES["viewer"]["permissions"],
        "message": "Account created successfully. Welcome to DataPulse!",
    }


def handle_profile_get(headers):
    user_payload, err = require_auth(headers)
    if err:
        return err

    user_data = get_user_safe(user_payload["username"])
    if not user_data:
        user_data = find_user_by_id(user_payload["sub"])
    if not user_data:
        return 404, {"detail": "User profile not found.", "code": "not_found"}

    return 200, user_data


def handle_profile_update(headers, body):
    user_payload, err = require_auth(headers)
    if err:
        return err

    user_data = get_user_safe(user_payload["username"])
    if not user_data:
        return 404, {"detail": "User profile not found.", "code": "not_found"}

    allowed_fields = ["first_name", "last_name", "email", "bio", "organization", "avatar_url"]
    updated = {**user_data}
    changed = []
    for key in allowed_fields:
        if key in body:
            updated[key] = body[key]
            changed.append(key)

    return 200, {**updated, "message": f"Profile updated. Changed: {', '.join(changed) if changed else 'no changes'}"}


def handle_change_password(headers, body):
    user_payload, err = require_auth(headers)
    if err:
        return err

    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")

    if not old_password or not new_password:
        return 400, {"detail": "Both old_password and new_password are required.", "code": "invalid_input"}

    user = USERS.get(user_payload["username"])
    if not user:
        return 404, {"detail": "User not found.", "code": "not_found"}

    if not verify_password(old_password, user["password_hash"]):
        return 400, {"detail": "Current password is incorrect.", "code": "wrong_password"}

    if len(new_password) < 6:
        return 400, {"detail": "New password must be at least 6 characters.", "code": "weak_password"}

    return 200, {"detail": "Password updated successfully.", "message": "Your password has been changed. Please log in again with your new password."}


def handle_api_key(headers):
    user_payload, err = require_role(headers, "analyst")
    if err:
        return err

    new_key = "dp_" + secrets.token_hex(32)
    return 200, {
        "api_key": new_key,
        "message": "New API key generated. Store it securely — it won't be shown again.",
        "permissions": ROLES.get(user_payload.get("role", "viewer"), ROLES["viewer"])["permissions"],
    }


def handle_stats(headers):
    user_payload, err = require_auth(headers)
    if err:
        return err

    stats = get_dashboard_stats()
    return 200, stats


def handle_token_refresh(body):
    refresh_token = body.get("refresh", "")
    if not refresh_token:
        return 400, {"detail": "Refresh token is required.", "code": "invalid_input"}

    payload = verify_token(refresh_token)
    if not payload:
        return 401, {"detail": "Invalid or expired refresh token. Please log in again.", "code": "token_expired"}

    if payload.get("type") != "refresh":
        return 401, {"detail": "Invalid token type. Expected refresh token.", "code": "invalid_token_type"}

    new_access = create_token(payload["sub"], payload["username"], payload["role"], "access")
    return 200, {"access": new_access}


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
            return self._respond(*handle_profile_get(self.headers))
        elif path == "profile" and method in ("PUT", "PATCH"):
            return self._respond(*handle_profile_update(self.headers, body))
        elif path == "change-password" and method == "PUT":
            return self._respond(*handle_change_password(self.headers, body))
        elif path == "api-key" and method == "POST":
            return self._respond(*handle_api_key(self.headers))
        elif path == "stats" and method == "GET":
            return self._respond(*handle_stats(self.headers))
        elif path == "token/refresh" and method == "POST":
            return self._respond(*handle_token_refresh(body))
        else:
            return self._respond(404, {"detail": f"Endpoint /users/{path} not found.", "code": "not_found"})

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_PATCH(self):
        self._route("PATCH")
