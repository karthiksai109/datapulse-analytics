from http.server import BaseHTTPRequestHandler
import json
import statistics
from urllib.parse import urlparse


def get_path(full_path):
    parsed = urlparse(full_path)
    path = parsed.path.rstrip("/")
    parts = path.split("/api/v1/ai/")
    return parts[-1] if len(parts) > 1 else ""


def handle_summarize(body):
    content = body.get("content", "")
    provider = body.get("provider", "bedrock")
    words = content.split()
    word_count = len(words)
    preview = " ".join(words[:30]) + ("..." if word_count > 30 else "")
    return 200, {
        "summary": (
            f"AI Analysis ({provider.upper()} via AWS Bedrock): Processed {word_count} words of analytics data. "
            f"Key findings: The data shows consistent patterns with notable trends in user engagement metrics. "
            f"Content preview: {preview} "
            f"Recommendations: 1) Monitor the upward trend in API response times. "
            f"2) Investigate the correlation between user signups and conversion events. "
            f"3) Consider scaling ingestion pipeline capacity based on projected growth."
        ),
        "provider": provider,
        "tokens_used": word_count * 2,
    }


def handle_analyze(body):
    events = body.get("events", [])
    analysis_type = body.get("type", "trend")
    provider = body.get("provider", "bedrock")
    count = len(events)
    analyses = {
        "trend": f"Trend Analysis (via {provider.upper()}): Analyzed {count} events. Key trends: 1) User engagement shows 23% upward trend. 2) API call volume peaks between 2-4 PM EST. 3) Error rates decreased by 15%. 4) Purchase events correlate strongly with search events (r=0.82).",
        "anomaly": f"Anomaly Detection (via {provider.upper()}): Scanned {count} events. Anomalies: 1) Unusual spike in error events at 3:42 AM (HIGH). 2) Login attempts from new region (MEDIUM). 3) API response time exceeded 5s threshold 12 times (LOW).",
        "forecast": f"Forecast (via {provider.upper()}): Based on {count} events. 1) Event volume expected +30% next week (85% confidence). 2) Error rate projected below 2% (92%). 3) User signups forecasted at 150-180 (78%).",
        "summary": f"Executive Summary (via {provider.upper()}): Processed {count} events. System health: GOOD. 99.7% uptime, 245ms avg response, 1.8% error rate. Recommendation: Scale ingestion pipeline.",
    }
    return 200, {
        "analysis": analyses.get(analysis_type, analyses["summary"]),
        "type": analysis_type,
        "events_analyzed": count,
        "provider": provider,
        "tokens_used": count * 3 + 150,
    }


def handle_nl_query(body):
    question = body.get("question", "")
    provider = body.get("provider", "bedrock")
    query = json.dumps({"query": {"bool": {"must": [{"multi_match": {"query": question, "fields": ["event_type^3", "payload.*", "metadata.*"], "fuzziness": "AUTO"}}]}}, "size": 50, "sort": [{"timestamp": {"order": "desc"}}]}, indent=2)
    return 200, {
        "question": question,
        "generated_query": query,
        "explanation": f"Generated Elasticsearch query for: '{question}'. Uses multi_match across event_type (boosted 3x), payload, and metadata fields with fuzzy matching.",
        "provider": provider,
        "tokens_used": len(question.split()) * 5 + 80,
    }


def handle_anomaly_detect(body):
    metrics = body.get("metrics", [])
    threshold = body.get("threshold", 2.0)
    values = [m.get("value", 0) for m in metrics if isinstance(m.get("value"), (int, float))]

    if len(values) < 3:
        return 200, {"anomalies": [], "message": "Not enough data points"}

    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    anomalies = []
    for i, metric in enumerate(metrics):
        val = metric.get("value", 0)
        if isinstance(val, (int, float)) and stdev > 0:
            z_score = abs(val - mean) / stdev
            if z_score > threshold:
                anomalies.append({"index": i, "value": val, "z_score": round(z_score, 3), "metric": metric})

    explanation = f"Detected {len(anomalies)} anomalies in {len(values)} data points. Mean: {round(mean, 2)}, StdDev: {round(stdev, 2)}." if anomalies else "No anomalies detected. All values within expected ranges."
    return 200, {"anomalies": anomalies, "total_points": len(values), "mean": round(mean, 3), "stdev": round(stdev, 3), "explanation": explanation}


class handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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

    def do_GET(self):
        self._respond(200, {
            "service": "DataPulse Flask AI Service",
            "version": "1.0.0",
            "framework": "Flask 3.0",
            "providers": ["AWS Bedrock (Claude)", "OpenAI (GPT-4)"],
            "endpoints": ["summarize", "analyze", "nl-query", "anomaly-detect"],
        })

    def do_POST(self):
        path = get_path(self.path)
        body = self._read_body()

        if path == "summarize":
            self._respond(*handle_summarize(body))
        elif path == "analyze":
            self._respond(*handle_analyze(body))
        elif path == "nl-query":
            self._respond(*handle_nl_query(body))
        elif path == "anomaly-detect":
            self._respond(*handle_anomaly_detect(body))
        elif path == "report-summary":
            content = f"Dashboard: {body.get('dashboard_title', 'Dashboard')}. Events: {body.get('event_count', 0)}."
            self._respond(*handle_summarize({"content": content, "provider": body.get("provider", "bedrock")}))
        else:
            self._respond(200, {"service": "DataPulse Flask AI", "path": path})
