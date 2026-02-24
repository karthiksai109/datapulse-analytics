"""
Realistic demo data for DataPulse Analytics.
All data is deterministic (seeded) so it's consistent across requests.
"""
import random
import uuid
import hashlib
from datetime import datetime, timedelta

# Seed for reproducible data
_rng = random.Random(42)

def _uuid(seed):
    return str(uuid.UUID(hashlib.md5(seed.encode()).hexdigest()))


# ─── Users ──────────────────────────────────────────────────────────────
PASSWORD_SALT = "datapulse-salt-v1"
def hash_password(password):
    salted = f"{PASSWORD_SALT}:{password}"
    return hashlib.sha256(salted.encode()).hexdigest()

USERS = {
    "karthik": {
        "id": _uuid("user-karthik"),
        "username": "karthik",
        "email": "karthik@datapulse.dev",
        "password_hash": hash_password("Admin@123"),
        "first_name": "Karthik",
        "last_name": "Ramadugu",
        "role": "admin",
        "organization": "DataPulse Analytics",
        "bio": "Full-stack developer | Python, Django, FastAPI, Flask, React | Cloud & DevOps",
        "avatar_url": "",
        "api_key": "dp_a1b2c3d4e5f6789012345678abcdef01",
        "is_active": True,
        "last_active": "2026-02-23T21:30:00Z",
        "created_at": "2025-11-01T08:00:00Z",
        "updated_at": "2026-02-23T21:30:00Z",
    },
    "sarah": {
        "id": _uuid("user-sarah"),
        "username": "sarah",
        "email": "sarah.chen@datapulse.dev",
        "password_hash": hash_password("Analyst@123"),
        "first_name": "Sarah",
        "last_name": "Chen",
        "role": "analyst",
        "organization": "DataPulse Analytics",
        "bio": "Data analyst specializing in business intelligence and predictive modeling",
        "avatar_url": "",
        "api_key": "dp_b2c3d4e5f6789012345678abcdef02",
        "is_active": True,
        "last_active": "2026-02-23T18:45:00Z",
        "created_at": "2025-12-15T10:00:00Z",
        "updated_at": "2026-02-23T18:45:00Z",
    },
    "mike": {
        "id": _uuid("user-mike"),
        "username": "mike",
        "email": "mike.johnson@datapulse.dev",
        "password_hash": hash_password("Viewer@123"),
        "first_name": "Mike",
        "last_name": "Johnson",
        "role": "viewer",
        "organization": "DataPulse Analytics",
        "bio": "Product manager reviewing analytics dashboards",
        "avatar_url": "",
        "api_key": None,
        "is_active": True,
        "last_active": "2026-02-23T16:00:00Z",
        "created_at": "2026-01-10T14:00:00Z",
        "updated_at": "2026-02-23T16:00:00Z",
    },
    "demo": {
        "id": _uuid("user-demo"),
        "username": "demo",
        "email": "demo@datapulse.dev",
        "password_hash": hash_password("demo"),
        "first_name": "Demo",
        "last_name": "User",
        "role": "admin",
        "organization": "DataPulse Analytics",
        "bio": "Demo account with full admin access",
        "avatar_url": "",
        "api_key": "dp_demo_key_0123456789abcdef",
        "is_active": True,
        "last_active": "2026-02-23T21:00:00Z",
        "created_at": "2025-11-01T08:00:00Z",
        "updated_at": "2026-02-23T21:00:00Z",
    },
}

def get_user_safe(username):
    """Return user dict without password_hash."""
    user = USERS.get(username)
    if not user:
        return None
    return {k: v for k, v in user.items() if k != "password_hash"}

def find_user_by_id(user_id):
    for u in USERS.values():
        if u["id"] == user_id:
            return {k: v for k, v in u.items() if k != "password_hash"}
    return None


# ─── Data Sources ───────────────────────────────────────────────────────
SOURCES = [
    {"id": _uuid("src-1"), "name": "Production REST API", "source_type": "api", "is_active": True, "connection_config": {"url": "https://api.datapulse.dev/v2", "method": "POST", "auth": "bearer_token", "rate_limit": "1000/min"}, "created_by": _uuid("user-karthik"), "events_count": 45230, "last_sync": "2026-02-23T21:15:00Z", "created_at": "2025-11-15T10:00:00Z", "updated_at": "2026-02-23T21:15:00Z"},
    {"id": _uuid("src-2"), "name": "GitHub Webhooks", "source_type": "webhook", "is_active": True, "connection_config": {"endpoint": "/webhooks/github", "secret": "whsec_***", "events": ["push", "pull_request", "issues"]}, "created_by": _uuid("user-karthik"), "events_count": 8920, "last_sync": "2026-02-23T20:42:00Z", "created_at": "2025-12-01T09:00:00Z", "updated_at": "2026-02-23T20:42:00Z"},
    {"id": _uuid("src-3"), "name": "PostgreSQL Analytics DB", "source_type": "database", "is_active": True, "connection_config": {"host": "analytics-db.datapulse.dev", "port": 5432, "database": "analytics_prod", "ssl": True}, "created_by": _uuid("user-sarah"), "events_count": 128450, "last_sync": "2026-02-23T21:00:00Z", "created_at": "2025-11-20T08:00:00Z", "updated_at": "2026-02-23T21:00:00Z"},
    {"id": _uuid("src-4"), "name": "Kafka Event Stream", "source_type": "streaming", "is_active": True, "connection_config": {"brokers": "kafka-1.datapulse.dev:9092,kafka-2.datapulse.dev:9092", "topic": "user-events", "consumer_group": "analytics-pipeline"}, "created_by": _uuid("user-karthik"), "events_count": 312800, "last_sync": "2026-02-23T21:29:55Z", "created_at": "2025-12-10T12:00:00Z", "updated_at": "2026-02-23T21:29:55Z"},
    {"id": _uuid("src-5"), "name": "Monthly Sales CSV", "source_type": "csv", "is_active": True, "connection_config": {"delimiter": ",", "encoding": "utf-8", "has_header": True, "s3_bucket": "datapulse-imports"}, "created_by": _uuid("user-sarah"), "events_count": 2150, "last_sync": "2026-02-20T08:00:00Z", "created_at": "2026-01-05T07:00:00Z", "updated_at": "2026-02-20T08:00:00Z"},
    {"id": _uuid("src-6"), "name": "Stripe Payment Webhooks", "source_type": "webhook", "is_active": True, "connection_config": {"endpoint": "/webhooks/stripe", "events": ["payment_intent.succeeded", "charge.failed", "subscription.updated"]}, "created_by": _uuid("user-karthik"), "events_count": 15780, "last_sync": "2026-02-23T21:28:00Z", "created_at": "2026-01-15T11:00:00Z", "updated_at": "2026-02-23T21:28:00Z"},
    {"id": _uuid("src-7"), "name": "CloudWatch Metrics", "source_type": "api", "is_active": False, "connection_config": {"region": "us-east-1", "namespace": "DataPulse/Production", "metrics": ["CPUUtilization", "NetworkIn", "NetworkOut"]}, "created_by": _uuid("user-karthik"), "events_count": 67200, "last_sync": "2026-02-22T16:00:00Z", "created_at": "2025-12-20T14:00:00Z", "updated_at": "2026-02-22T16:00:00Z"},
]


# ─── Dashboards ─────────────────────────────────────────────────────────
DASHBOARDS = [
    {"id": _uuid("dash-1"), "title": "Executive Overview", "description": "High-level KPIs and business metrics for leadership team", "layout_config": {"columns": 4, "rows": 3}, "is_public": True, "owner": _uuid("user-karthik"), "data_sources": [_uuid("src-1"), _uuid("src-3")], "widget_count": 8, "created_at": "2025-11-20T08:00:00Z", "updated_at": "2026-02-23T12:00:00Z"},
    {"id": _uuid("dash-2"), "title": "Sales & Revenue", "description": "Revenue tracking, conversion funnels, and payment analytics", "layout_config": {"columns": 3, "rows": 4}, "is_public": False, "owner": _uuid("user-sarah"), "data_sources": [_uuid("src-5"), _uuid("src-6")], "widget_count": 12, "created_at": "2025-12-15T10:00:00Z", "updated_at": "2026-02-22T15:00:00Z"},
    {"id": _uuid("dash-3"), "title": "User Engagement", "description": "User behavior, retention cohorts, and session analytics", "layout_config": {"columns": 4, "rows": 3}, "is_public": True, "owner": _uuid("user-karthik"), "data_sources": [_uuid("src-1"), _uuid("src-4")], "widget_count": 10, "created_at": "2026-01-05T09:00:00Z", "updated_at": "2026-02-21T11:00:00Z"},
    {"id": _uuid("dash-4"), "title": "Infrastructure Monitoring", "description": "System health, API latency, error rates, and resource utilization", "layout_config": {"columns": 3, "rows": 3}, "is_public": False, "owner": _uuid("user-karthik"), "data_sources": [_uuid("src-7"), _uuid("src-4")], "widget_count": 9, "created_at": "2026-01-20T14:00:00Z", "updated_at": "2026-02-23T21:00:00Z"},
    {"id": _uuid("dash-5"), "title": "Real-time Event Stream", "description": "Live event monitoring with Kafka consumer metrics", "layout_config": {"columns": 2, "rows": 4}, "is_public": True, "owner": _uuid("user-karthik"), "data_sources": [_uuid("src-4")], "widget_count": 6, "created_at": "2026-02-01T08:00:00Z", "updated_at": "2026-02-23T21:29:00Z"},
]


# ─── Alerts ─────────────────────────────────────────────────────────────
ALERTS = [
    {"id": _uuid("alert-1"), "name": "High Error Rate", "description": "API error rate exceeds 5% over 5-minute window", "condition_config": {"metric": "error_rate", "threshold": 5.0, "operator": "gt", "window_minutes": 5, "aggregation": "avg"}, "severity": "critical", "is_active": True, "owner": _uuid("user-karthik"), "dashboard": _uuid("dash-4"), "last_triggered": "2026-02-23T14:32:00Z", "trigger_count": 12, "notification_channels": ["slack", "pagerduty"], "created_at": "2025-12-01T10:00:00Z", "updated_at": "2026-02-23T14:32:00Z"},
    {"id": _uuid("alert-2"), "name": "Payment Failure Spike", "description": "Payment failure count exceeds 10 in 15-minute window", "condition_config": {"metric": "payment_failures", "threshold": 10, "operator": "gt", "window_minutes": 15, "aggregation": "count"}, "severity": "high", "is_active": True, "owner": _uuid("user-sarah"), "dashboard": _uuid("dash-2"), "last_triggered": "2026-02-22T09:15:00Z", "trigger_count": 5, "notification_channels": ["slack", "email"], "created_at": "2026-01-15T08:00:00Z", "updated_at": "2026-02-22T09:15:00Z"},
    {"id": _uuid("alert-3"), "name": "Kafka Consumer Lag", "description": "Consumer lag exceeds 10,000 messages", "condition_config": {"metric": "consumer_lag", "threshold": 10000, "operator": "gt", "window_minutes": 10, "aggregation": "max"}, "severity": "medium", "is_active": True, "owner": _uuid("user-karthik"), "dashboard": _uuid("dash-5"), "last_triggered": "2026-02-20T16:45:00Z", "trigger_count": 3, "notification_channels": ["slack"], "created_at": "2026-01-20T12:00:00Z", "updated_at": "2026-02-20T16:45:00Z"},
    {"id": _uuid("alert-4"), "name": "API Latency P99", "description": "P99 API response time exceeds 2 seconds", "condition_config": {"metric": "response_time_p99", "threshold": 2000, "operator": "gt", "window_minutes": 5, "aggregation": "p99"}, "severity": "medium", "is_active": True, "owner": _uuid("user-karthik"), "dashboard": _uuid("dash-4"), "last_triggered": "2026-02-21T11:20:00Z", "trigger_count": 8, "notification_channels": ["slack"], "created_at": "2025-12-10T14:00:00Z", "updated_at": "2026-02-21T11:20:00Z"},
    {"id": _uuid("alert-5"), "name": "Low Conversion Rate", "description": "Conversion rate drops below 2% over 1-hour window", "condition_config": {"metric": "conversion_rate", "threshold": 2.0, "operator": "lt", "window_minutes": 60, "aggregation": "avg"}, "severity": "high", "is_active": False, "owner": _uuid("user-sarah"), "dashboard": _uuid("dash-2"), "last_triggered": "2026-02-18T10:00:00Z", "trigger_count": 2, "notification_channels": ["email"], "created_at": "2026-02-01T09:00:00Z", "updated_at": "2026-02-18T10:00:00Z"},
    {"id": _uuid("alert-6"), "name": "New User Signup Surge", "description": "Signup rate exceeds 50 per hour (potential bot attack)", "condition_config": {"metric": "signup_rate", "threshold": 50, "operator": "gt", "window_minutes": 60, "aggregation": "count"}, "severity": "low", "is_active": True, "owner": _uuid("user-karthik"), "dashboard": _uuid("dash-3"), "last_triggered": None, "trigger_count": 0, "notification_channels": ["slack"], "created_at": "2026-02-10T14:00:00Z", "updated_at": "2026-02-10T14:00:00Z"},
]


# ─── Reports ────────────────────────────────────────────────────────────
REPORTS = [
    {"id": _uuid("report-1"), "title": "Weekly Executive Summary - Feb 17-23", "dashboard": _uuid("dash-1"), "generated_by": _uuid("user-karthik"), "format": "pdf", "file_url": "https://s3.amazonaws.com/datapulse-reports/weekly-exec-2026-02-23.pdf", "ai_summary": "Platform processed 89,247 events this week (+12% WoW). Revenue up 18% MoM driven by Enterprise segment. API uptime: 99.97%. Key risk: Kafka consumer lag spiked twice during peak hours. Recommendation: Scale consumer group from 3 to 5 partitions before March traffic surge.", "status": "completed", "created_at": "2026-02-23T10:00:00Z"},
    {"id": _uuid("report-2"), "title": "Monthly Revenue Analysis - January 2026", "dashboard": _uuid("dash-2"), "generated_by": _uuid("user-sarah"), "format": "pdf", "file_url": "https://s3.amazonaws.com/datapulse-reports/revenue-jan-2026.pdf", "ai_summary": "Total revenue: $2.4M (+22% YoY). Enterprise: $1.01M (42%), SMB: $840K (35%), Individual: $552K (23%). Churn rate: 3.2% (down from 4.1%). Top growth region: APAC (+34%). Payment failure rate: 1.8% (within SLA). 47 new enterprise accounts onboarded.", "status": "completed", "created_at": "2026-02-01T08:00:00Z"},
    {"id": _uuid("report-3"), "title": "Q4 2025 Performance Report", "dashboard": _uuid("dash-1"), "generated_by": _uuid("user-karthik"), "format": "pdf", "file_url": "https://s3.amazonaws.com/datapulse-reports/q4-2025-performance.pdf", "ai_summary": "Q4 highlights: 1.2M total events processed. Platform uptime: 99.95%. Average API latency: 142ms (P50), 890ms (P99). User base grew 28% to 12,400 active users. Infrastructure cost reduced 15% via auto-scaling optimizations. 3 critical incidents, all resolved within SLA.", "status": "completed", "created_at": "2026-01-15T14:00:00Z"},
    {"id": _uuid("report-4"), "title": "Error Analysis - February 2026", "dashboard": _uuid("dash-4"), "generated_by": _uuid("user-karthik"), "format": "json", "file_url": "https://s3.amazonaws.com/datapulse-reports/errors-feb-2026.json", "ai_summary": "Total errors: 4,521 (error rate: 2.1%). Breakdown: Timeout errors 45% (mostly Stripe webhook retries), Validation errors 28% (malformed CSV uploads), Auth errors 18% (expired tokens), Server errors 9% (memory pressure during peak). Recommendation: Implement circuit breaker for Stripe calls, add CSV pre-validation.", "status": "completed", "created_at": "2026-02-20T08:00:00Z"},
    {"id": _uuid("report-5"), "title": "User Engagement Cohort Analysis", "dashboard": _uuid("dash-3"), "generated_by": _uuid("user-sarah"), "format": "csv", "file_url": "https://s3.amazonaws.com/datapulse-reports/cohort-analysis-feb.csv", "ai_summary": "30-day retention: 68% (up from 62%). Power users (>5 sessions/week): 23% of base, generating 71% of events. Feature adoption: AI Insights 45%, Custom Dashboards 67%, Alerts 52%, Reports 38%. Recommendation: Improve AI Insights onboarding flow to increase adoption.", "status": "completed", "created_at": "2026-02-18T11:00:00Z"},
]


# ─── Events Generator ───────────────────────────────────────────────────
EVENT_TYPES = [
    ("page_view", "Web App"),
    ("api_call", "REST API"),
    ("purchase", "Payment Service"),
    ("signup", "Auth Service"),
    ("login", "Auth Service"),
    ("error", "Error Tracker"),
    ("search", "Search Service"),
    ("click", "Web App"),
    ("webhook", "GitHub"),
    ("data_sync", "ETL Pipeline"),
    ("alert_trigger", "Monitoring"),
    ("report_generated", "Report Service"),
]

PAGES = ["/dashboard", "/analytics", "/reports", "/settings", "/events", "/alerts", "/ai-insights", "/data-sources", "/login", "/register"]
ENDPOINTS = ["/api/v1/events", "/api/v1/users", "/api/v1/dashboards", "/api/v1/reports", "/api/v1/sources", "/api/v1/alerts", "/api/v1/ai/summarize"]
ERROR_TYPES = ["TimeoutError", "ValidationError", "AuthenticationError", "RateLimitExceeded", "DatabaseConnectionError", "KafkaProducerError"]
BROWSERS = ["Chrome/121.0", "Firefox/122.0", "Safari/17.3", "Edge/121.0"]
REGIONS = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]


def generate_events(count=100, seed=None):
    rng = random.Random(seed or 42)
    events = []
    now = datetime(2026, 2, 23, 21, 30, 0)
    source_ids = [s["id"] for s in SOURCES]

    for i in range(count):
        hours_ago = rng.randint(0, 336)  # up to 14 days
        ts = now - timedelta(hours=hours_ago, minutes=rng.randint(0, 59), seconds=rng.randint(0, 59))
        etype, esource = rng.choice(EVENT_TYPES)

        if etype == "page_view":
            payload = {"page": rng.choice(PAGES), "duration_ms": rng.randint(200, 12000), "referrer": rng.choice(["google", "direct", "twitter", "linkedin", ""])}
        elif etype == "api_call":
            status = rng.choices([200, 201, 400, 401, 404, 500], weights=[60, 15, 8, 5, 7, 5])[0]
            payload = {"endpoint": rng.choice(ENDPOINTS), "method": rng.choice(["GET", "POST", "PUT", "DELETE"]), "status_code": status, "response_ms": rng.randint(12, 4500)}
        elif etype == "purchase":
            payload = {"amount": round(rng.uniform(9.99, 499.99), 2), "currency": "USD", "product": f"plan_{rng.choice(['starter', 'pro', 'enterprise'])}", "payment_method": rng.choice(["card", "paypal", "wire"])}
        elif etype == "error":
            payload = {"error_type": rng.choice(ERROR_TYPES), "message": f"Error in {rng.choice(['payment', 'auth', 'ingestion', 'query'])} service", "stack_trace": "...", "severity": rng.choice(["warning", "error", "critical"])}
        elif etype == "signup":
            payload = {"method": rng.choice(["email", "google_oauth", "github_oauth"]), "plan": rng.choice(["free", "starter", "pro"]), "referral": rng.choice(["organic", "paid_ad", "referral", ""])}
        elif etype == "login":
            payload = {"method": rng.choice(["password", "oauth", "sso"]), "success": rng.choices([True, False], weights=[95, 5])[0], "mfa": rng.choice([True, False])}
        elif etype == "search":
            payload = {"query": rng.choice(["error events", "revenue dashboard", "user signups", "api latency", "payment failures"]), "results_count": rng.randint(0, 250), "response_ms": rng.randint(15, 800)}
        elif etype == "webhook":
            payload = {"provider": rng.choice(["github", "stripe", "slack"]), "event": rng.choice(["push", "payment_intent.succeeded", "message.posted"]), "status": "processed"}
        elif etype == "data_sync":
            payload = {"records": rng.randint(100, 50000), "source_db": rng.choice(["postgres", "mongodb", "redis"]), "duration_ms": rng.randint(500, 30000), "status": rng.choice(["completed", "partial", "failed"])}
        else:
            payload = {"value": rng.randint(1, 1000)}

        metadata = {
            "ip": f"{rng.randint(10,200)}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
            "user_agent": rng.choice(BROWSERS),
            "region": rng.choice(REGIONS),
            "session_id": str(uuid.UUID(int=rng.getrandbits(128))),
        }

        events.append({
            "id": str(uuid.UUID(int=rng.getrandbits(128))),
            "event_type": etype,
            "source": rng.choice(source_ids),
            "source_name": esource,
            "payload": payload,
            "metadata": metadata,
            "timestamp": ts.isoformat() + "Z",
            "processed": rng.choices([True, False], weights=[85, 15])[0],
            "created_at": ts.isoformat() + "Z",
        })

    return sorted(events, key=lambda e: e["timestamp"], reverse=True)


# ─── Stats ──────────────────────────────────────────────────────────────
def get_dashboard_stats():
    return {
        "dashboards": len(DASHBOARDS),
        "events_today": 12847,
        "active_alerts": sum(1 for a in ALERTS if a["is_active"]),
        "reports_generated": len(REPORTS),
        "total_events": 497550,
        "active_sources": sum(1 for s in SOURCES if s["is_active"]),
        "error_rate": 2.1,
        "avg_response_ms": 245,
        "uptime_percent": 99.97,
        "events_this_week": 89247,
        "events_last_week": 79684,
        "weekly_growth": 12.0,
    }
