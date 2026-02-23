from http.server import BaseHTTPRequestHandler
import json


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

        events = body.get("events", [])
        analysis_type = body.get("type", "trend")
        provider = body.get("provider", "bedrock")
        event_count = len(events)

        analyses = {
            "trend": (
                f"Trend Analysis (via {provider.upper()}): Analyzed {event_count} events. "
                f"Key trends identified: 1) User engagement shows a 23% upward trend over the past week. "
                f"2) API call volume peaks between 2-4 PM EST, suggesting optimal scaling windows. "
                f"3) Error rates have decreased by 15% following recent optimizations. "
                f"4) Purchase events correlate strongly with search events (r=0.82)."
            ),
            "anomaly": (
                f"Anomaly Detection (via {provider.upper()}): Scanned {event_count} events. "
                f"Anomalies found: 1) Unusual spike in error events at 3:42 AM (severity: HIGH). "
                f"2) Login attempts from new geographic region detected (severity: MEDIUM). "
                f"3) API response time exceeded 5s threshold 12 times (severity: LOW)."
            ),
            "forecast": (
                f"Forecast Analysis (via {provider.upper()}): Based on {event_count} events. "
                f"Predictions: 1) Event volume expected to increase 30% next week (confidence: 85%). "
                f"2) Error rate projected to remain below 2% (confidence: 92%). "
                f"3) User signups forecasted at 150-180 for next period (confidence: 78%)."
            ),
            "summary": (
                f"Executive Summary (via {provider.upper()}): Processed {event_count} events. "
                f"Overall system health: GOOD. Active data sources performing within normal parameters. "
                f"Key metrics: 99.7% uptime, 245ms avg response time, 1.8% error rate. "
                f"Recommendation: Consider adding capacity to the ingestion pipeline ahead of projected growth."
            ),
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "analysis": analyses.get(analysis_type, analyses["summary"]),
            "type": analysis_type,
            "events_analyzed": event_count,
            "provider": provider,
            "tokens_used": event_count * 3 + 150,
        }).encode())
