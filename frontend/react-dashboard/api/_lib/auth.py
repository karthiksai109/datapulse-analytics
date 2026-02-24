"""
JWT Authentication & Authorization module for DataPulse Analytics.
Uses HMAC-SHA256 for token signing, SHA-256 + salt for password hashing.
"""
import json
import hmac
import hashlib
import time
import uuid
import base64
import os

# Secret key for JWT signing - in production this would be an env var
JWT_SECRET = os.environ.get("JWT_SECRET", "datapulse-jwt-secret-k8s-2026-prod-key")
JWT_EXPIRY = 3600  # 1 hour
JWT_REFRESH_EXPIRY = 86400 * 7  # 7 days
PASSWORD_SALT = "datapulse-salt-v1"

# ─── Roles & Permissions ───────────────────────────────────────────────
ROLES = {
    "admin": {
        "level": 3,
        "permissions": [
            "read:all", "write:all", "delete:all",
            "manage:users", "manage:alerts", "manage:sources",
            "generate:reports", "view:ai", "manage:dashboards",
        ],
    },
    "analyst": {
        "level": 2,
        "permissions": [
            "read:all", "write:events", "write:dashboards",
            "generate:reports", "view:ai", "manage:alerts",
        ],
    },
    "viewer": {
        "level": 1,
        "permissions": [
            "read:dashboards", "read:events", "read:reports",
            "read:alerts", "view:ai",
        ],
    },
}


# ─── Password Hashing ──────────────────────────────────────────────────
def hash_password(password):
    salted = f"{PASSWORD_SALT}:{password}"
    return hashlib.sha256(salted.encode()).hexdigest()


def verify_password(password, hashed):
    return hash_password(password) == hashed


# ─── JWT Token Creation & Verification ─────────────────────────────────
def _b64encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(s):
    padding = 4 - len(s) % 4
    s += "=" * padding
    return base64.urlsafe_b64decode(s)


def create_token(user_id, username, role, token_type="access"):
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    expiry = JWT_EXPIRY if token_type == "access" else JWT_REFRESH_EXPIRY
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expiry,
        "jti": str(uuid.uuid4()),
    }
    header_b64 = _b64encode(json.dumps(header).encode())
    payload_b64 = _b64encode(json.dumps(payload).encode())
    signature = hmac.new(
        JWT_SECRET.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256
    ).digest()
    sig_b64 = _b64encode(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_token(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        expected_sig = hmac.new(
            JWT_SECRET.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256
        ).digest()
        actual_sig = _b64decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload = json.loads(_b64decode(payload_b64))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def get_user_from_request(headers):
    """Extract and verify user from Authorization header."""
    auth = headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    return verify_token(token)


def has_permission(role, permission):
    role_info = ROLES.get(role, ROLES["viewer"])
    return permission in role_info["permissions"] or "read:all" in role_info["permissions"] or "write:all" in role_info["permissions"]


def require_auth(headers):
    """Returns (user_payload, error_response). If error_response is not None, return it."""
    user = get_user_from_request(headers)
    if not user:
        return None, (401, {"detail": "Authentication credentials were not provided or are invalid.", "code": "not_authenticated"})
    return user, None


def require_role(headers, min_role="viewer"):
    """Check auth + minimum role level."""
    user, err = require_auth(headers)
    if err:
        return None, err
    role_levels = {"viewer": 1, "analyst": 2, "admin": 3}
    user_level = role_levels.get(user.get("role", "viewer"), 1)
    required_level = role_levels.get(min_role, 1)
    if user_level < required_level:
        return None, (403, {"detail": f"Insufficient permissions. Required role: {min_role}", "code": "permission_denied"})
    return user, None
