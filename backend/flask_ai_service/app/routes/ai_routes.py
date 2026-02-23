import logging
from flask import Blueprint, request, jsonify
from ..services.bedrock_service import generate_bedrock_summary
from ..services.openai_service import generate_openai_insights
from ..services.llm_orchestrator import analyze_data, generate_natural_language_query

logger = logging.getLogger("datapulse-flask-ai")
ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/summarize", methods=["POST"])
def summarize_data():
    data = request.get_json()
    if not data or "content" not in data:
        return jsonify({"error": "Missing 'content' field"}), 400

    provider = data.get("provider", "bedrock")
    content = data["content"]
    max_tokens = data.get("max_tokens", 500)

    try:
        if provider == "openai":
            result = generate_openai_insights(content, max_tokens=max_tokens)
        else:
            result = generate_bedrock_summary(content, max_tokens=max_tokens)

        return jsonify({
            "summary": result["text"],
            "provider": provider,
            "tokens_used": result.get("tokens_used", 0),
        })
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/analyze", methods=["POST"])
def analyze_analytics_data():
    data = request.get_json()
    if not data or "events" not in data:
        return jsonify({"error": "Missing 'events' field"}), 400

    try:
        analysis = analyze_data(
            events=data["events"],
            analysis_type=data.get("type", "trend"),
            provider=data.get("provider", "bedrock"),
        )
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/nl-query", methods=["POST"])
def natural_language_query():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' field"}), 400

    try:
        result = generate_natural_language_query(
            question=data["question"],
            schema_context=data.get("schema", ""),
            provider=data.get("provider", "bedrock"),
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"NL query generation failed: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/anomaly-detect", methods=["POST"])
def detect_anomalies():
    data = request.get_json()
    if not data or "metrics" not in data:
        return jsonify({"error": "Missing 'metrics' field"}), 400

    try:
        metrics = data["metrics"]
        threshold = data.get("threshold", 2.0)

        # Statistical anomaly detection
        import statistics
        values = [m.get("value", 0) for m in metrics if isinstance(m.get("value"), (int, float))]

        if len(values) < 3:
            return jsonify({"anomalies": [], "message": "Not enough data points"})

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

        # Get AI explanation for anomalies
        if anomalies:
            explanation = generate_bedrock_summary(
                f"Explain these anomalies in analytics data: {anomalies[:5]}",
                max_tokens=300,
            )
        else:
            explanation = {"text": "No anomalies detected in the provided data."}

        return jsonify({
            "anomalies": anomalies,
            "total_points": len(values),
            "mean": round(mean, 3),
            "stdev": round(stdev, 3),
            "explanation": explanation["text"],
        })
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/report-summary", methods=["POST"])
def generate_report_summary():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    try:
        dashboard_title = data.get("dashboard_title", "Dashboard")
        event_count = data.get("event_count", 0)
        source_count = data.get("source_count", 0)
        alert_count = data.get("alert_count", 0)
        top_events = data.get("top_events", [])

        prompt = (
            f"Generate a professional executive summary for the analytics dashboard '{dashboard_title}'. "
            f"Key metrics: {event_count} total events processed from {source_count} data sources. "
            f"{alert_count} alerts triggered. Top event types: {', '.join(top_events[:5])}. "
            f"Provide insights, trends, and actionable recommendations."
        )

        result = generate_bedrock_summary(prompt, max_tokens=600)
        return jsonify({
            "summary": result["text"],
            "dashboard": dashboard_title,
            "tokens_used": result.get("tokens_used", 0),
        })
    except Exception as e:
        logger.error(f"Report summary generation failed: {e}")
        return jsonify({"error": str(e)}), 500
