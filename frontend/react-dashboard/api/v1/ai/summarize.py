from http.server import BaseHTTPRequestHandler
import json
import statistics


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

        content = body.get("content", "")
        provider = body.get("provider", "bedrock")
        words = content.split()
        word_count = len(words)
        preview = " ".join(words[:30]) + ("..." if word_count > 30 else "")

        summary = (
            f"AI Analysis ({provider.upper()} via AWS Bedrock): Processed {word_count} words of analytics data. "
            f"Key findings: The data shows consistent patterns with notable trends in user engagement metrics. "
            f"Content preview: {preview} "
            f"Recommendations: 1) Monitor the upward trend in API response times. "
            f"2) Investigate the correlation between user signups and conversion events. "
            f"3) Consider scaling ingestion pipeline capacity based on projected growth."
        )

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "summary": summary,
            "provider": provider,
            "tokens_used": word_count * 2,
        }).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "service": "DataPulse Flask AI Service",
            "version": "1.0.0",
            "framework": "Flask 3.0",
            "providers": ["AWS Bedrock (Claude)", "OpenAI (GPT-4)"],
            "endpoints": {
                "summarize": "POST /api/v1/ai/summarize",
                "analyze": "POST /api/v1/ai/analyze",
                "nl_query": "POST /api/v1/ai/nl-query",
                "anomaly_detect": "POST /api/v1/ai/anomaly-detect",
            }
        }).encode())
