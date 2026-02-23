import pytest
import json


def get_test_client():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


class TestFlaskAIService:
    def test_health_check(self):
        client = get_test_client()
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["service"] == "datapulse-flask-ai"

    def test_summarize_missing_content(self):
        client = get_test_client()
        response = client.post("/api/v1/ai/summarize", json={})
        assert response.status_code == 400

    def test_summarize_with_content(self):
        client = get_test_client()
        response = client.post("/api/v1/ai/summarize", json={
            "content": "Sales increased by 25% in Q4 compared to Q3. Revenue hit $2.5M.",
            "provider": "bedrock",
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "summary" in data
        assert "provider" in data

    def test_analyze_missing_events(self):
        client = get_test_client()
        response = client.post("/api/v1/ai/analyze", json={})
        assert response.status_code == 400

    def test_analyze_with_events(self):
        client = get_test_client()
        response = client.post("/api/v1/ai/analyze", json={
            "events": [
                {"event_type": "page_view", "payload": {"page": "/home"}, "timestamp": "2024-01-15T10:00:00"},
                {"event_type": "click", "payload": {"button": "signup"}, "timestamp": "2024-01-15T10:05:00"},
            ],
            "type": "trend",
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "analysis" in data
        assert data["events_analyzed"] == 2

    def test_nl_query_missing_question(self):
        client = get_test_client()
        response = client.post("/api/v1/ai/nl-query", json={})
        assert response.status_code == 400

    def test_nl_query_with_question(self):
        client = get_test_client()
        response = client.post("/api/v1/ai/nl-query", json={
            "question": "Show me all error events from last week",
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "generated_query" in data
        assert data["question"] == "Show me all error events from last week"

    def test_anomaly_detect_missing_metrics(self):
        client = get_test_client()
        response = client.post("/api/v1/ai/anomaly-detect", json={})
        assert response.status_code == 400

    def test_anomaly_detect_with_metrics(self):
        client = get_test_client()
        response = client.post("/api/v1/ai/anomaly-detect", json={
            "metrics": [
                {"value": 10}, {"value": 12}, {"value": 11},
                {"value": 100}, {"value": 13}, {"value": 10},
            ],
            "threshold": 2.0,
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "anomalies" in data
        assert "mean" in data
        assert "stdev" in data
        assert len(data["anomalies"]) > 0

    def test_report_summary(self):
        client = get_test_client()
        response = client.post("/api/v1/ai/report-summary", json={
            "dashboard_title": "Sales Dashboard",
            "event_count": 5000,
            "source_count": 3,
            "alert_count": 2,
            "top_events": ["page_view", "purchase", "signup"],
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "summary" in data
        assert data["dashboard"] == "Sales Dashboard"
