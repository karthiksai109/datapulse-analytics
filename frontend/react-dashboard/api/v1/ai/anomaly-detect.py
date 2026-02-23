from http.server import BaseHTTPRequestHandler
import json
import statistics
import random


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

        metrics = body.get("metrics", [])
        threshold = body.get("threshold", 2.0)

        values = [m.get("value", 0) for m in metrics if isinstance(m.get("value"), (int, float))]

        if len(values) < 3:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"anomalies": [], "message": "Not enough data points"}).encode())
            return

        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        anomalies = []
        for i, metric in enumerate(metrics):
            val = metric.get("value", 0)
            if isinstance(val, (int, float)) and stdev > 0:
                z_score = abs(val - mean) / stdev
                if z_score > threshold:
                    anomalies.append({
                        "index": i,
                        "value": val,
                        "z_score": round(z_score, 3),
                        "metric": metric,
                    })

        if anomalies:
            explanation = (
                f"Detected {len(anomalies)} anomalies in {len(values)} data points. "
                f"Mean: {round(mean, 2)}, StdDev: {round(stdev, 2)}. "
                f"The anomalous values deviate significantly from the expected range "
                f"({round(mean - threshold * stdev, 2)} to {round(mean + threshold * stdev, 2)}). "
                f"Recommendation: Investigate the root cause of these outliers, particularly "
                f"checking for system errors or unusual user behavior patterns."
            )
        else:
            explanation = "No anomalies detected in the provided data. All values fall within expected ranges."

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "anomalies": anomalies,
            "total_points": len(values),
            "mean": round(mean, 3),
            "stdev": round(stdev, 3),
            "explanation": explanation,
        }).encode())
