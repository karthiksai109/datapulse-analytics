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

        question = body.get("question", "")
        provider = body.get("provider", "bedrock")

        generated_query = json.dumps({
            "query": {
                "bool": {
                    "must": [
                        {"multi_match": {"query": question, "fields": ["event_type^3", "payload.*", "metadata.*"], "fuzziness": "AUTO"}}
                    ]
                }
            },
            "size": 50,
            "sort": [{"timestamp": {"order": "desc"}}]
        }, indent=2)

        explanation = (
            f"Generated Elasticsearch query for: '{question}'. "
            f"This query uses multi_match across event_type (boosted 3x), payload, and metadata fields "
            f"with fuzzy matching enabled. Results sorted by timestamp descending, limited to 50 documents."
        )

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "question": question,
            "generated_query": generated_query,
            "explanation": explanation,
            "provider": provider,
            "tokens_used": len(question.split()) * 5 + 80,
        }).encode())
