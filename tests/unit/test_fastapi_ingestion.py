import pytest
from fastapi.testclient import TestClient
from datetime import datetime


def get_test_client():
    from app.main import app
    return TestClient(app)


class TestIngestionEndpoints:
    def test_health_check(self):
        client = get_test_client()
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "datapulse-fastapi-ingestion"

    def test_root_endpoint(self):
        client = get_test_client()
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["version"] == "1.0.0"

    def test_ingest_single_event(self):
        client = get_test_client()
        event = {
            "event_type": "test_event",
            "payload": {"key": "value", "count": 42},
            "metadata": {"source": "unit_test"},
            "timestamp": datetime.utcnow().isoformat(),
        }
        response = client.post("/api/v1/ingest/event", json=event)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

    def test_ingest_event_missing_type(self):
        client = get_test_client()
        event = {"payload": {"key": "value"}}
        response = client.post("/api/v1/ingest/event", json=event)
        assert response.status_code == 422

    def test_bulk_ingest(self):
        client = get_test_client()
        events = {
            "events": [
                {"event_type": "bulk_test_1", "payload": {"i": 1}, "timestamp": datetime.utcnow().isoformat()},
                {"event_type": "bulk_test_2", "payload": {"i": 2}, "timestamp": datetime.utcnow().isoformat()},
            ]
        }
        response = client.post("/api/v1/ingest/bulk", json=events)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

    def test_bulk_ingest_empty(self):
        client = get_test_client()
        response = client.post("/api/v1/ingest/bulk", json={"events": []})
        assert response.status_code == 422

    def test_webhook_ingest(self):
        client = get_test_client()
        payload = {"action": "push", "repository": "datapulse"}
        response = client.post("/api/v1/ingest/webhook/source-123", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == "source-123"

    def test_search_events_missing_query(self):
        client = get_test_client()
        response = client.get("/api/v1/search/events")
        assert response.status_code == 422
