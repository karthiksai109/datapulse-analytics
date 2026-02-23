import pytest
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
FASTAPI_URL = "http://localhost:8001"
FLASK_URL = "http://localhost:5001"


class TestDjangoAPIIntegration:
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/health/live/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_readiness_endpoint(self):
        response = requests.get(f"{BASE_URL}/health/ready/")
        assert response.status_code in [200, 503]

    def test_register_and_login(self):
        reg_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@datapulse.dev",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
        }
        reg_response = requests.post(f"{BASE_URL}/users/register/", json=reg_data)
        assert reg_response.status_code == 201

        login_response = requests.post(f"{BASE_URL}/users/login/", json={
            "username": reg_data["username"],
            "password": reg_data["password"],
        })
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access" in tokens
        assert "refresh" in tokens
        return tokens["access"]

    def test_authenticated_endpoints(self):
        token = self.test_register_and_login()
        headers = {"Authorization": f"Bearer {token}"}

        profile = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
        assert profile.status_code == 200

        stats = requests.get(f"{BASE_URL}/users/stats/", headers=headers)
        assert stats.status_code == 200

        sources = requests.get(f"{BASE_URL}/analytics/sources/", headers=headers)
        assert sources.status_code == 200

        dashboards = requests.get(f"{BASE_URL}/analytics/dashboards/", headers=headers)
        assert dashboards.status_code == 200


class TestFastAPIIntegration:
    def test_health(self):
        response = requests.get(f"{FASTAPI_URL}/health")
        assert response.status_code == 200

    def test_ingest_event(self):
        event = {
            "event_type": "integration_test",
            "payload": {"test": True},
            "metadata": {"source": "integration"},
        }
        response = requests.post(f"{FASTAPI_URL}/api/v1/ingest/event", json=event)
        assert response.status_code == 200


class TestFlaskAIIntegration:
    def test_health(self):
        response = requests.get(f"{FLASK_URL}/api/v1/health")
        assert response.status_code == 200

    def test_summarize(self):
        response = requests.post(f"{FLASK_URL}/api/v1/ai/summarize", json={
            "content": "Integration test data for summarization",
        })
        assert response.status_code == 200
