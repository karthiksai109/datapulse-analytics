import logging
from .bedrock_service import generate_bedrock_summary
from .openai_service import generate_openai_insights

logger = logging.getLogger("datapulse-flask-ai")


def analyze_data(events: list, analysis_type: str = "trend", provider: str = "bedrock") -> dict:
    if not events:
        return {"analysis": "No events provided for analysis.", "type": analysis_type}

    event_summary = _prepare_event_summary(events)

    prompts = {
        "trend": (
            f"Analyze the following analytics events and identify trends, patterns, and notable changes:\n\n"
            f"{event_summary}\n\nProvide a trend analysis with key findings."
        ),
        "anomaly": (
            f"Review the following analytics events and identify any anomalies or unusual patterns:\n\n"
            f"{event_summary}\n\nHighlight anomalies with severity levels."
        ),
        "forecast": (
            f"Based on the following analytics events, provide a forecast and predictions:\n\n"
            f"{event_summary}\n\nInclude confidence levels for each prediction."
        ),
        "summary": (
            f"Provide an executive summary of the following analytics data:\n\n"
            f"{event_summary}\n\nInclude key metrics, highlights, and recommendations."
        ),
    }

    prompt = prompts.get(analysis_type, prompts["summary"])

    if provider == "openai":
        result = generate_openai_insights(prompt, max_tokens=600)
    else:
        result = generate_bedrock_summary(prompt, max_tokens=600)

    return {
        "analysis": result["text"],
        "type": analysis_type,
        "events_analyzed": len(events),
        "provider": result.get("provider", provider),
        "tokens_used": result.get("tokens_used", 0),
    }


def generate_natural_language_query(
    question: str, schema_context: str = "", provider: str = "bedrock"
) -> dict:
    prompt = (
        f"Convert the following natural language question into an Elasticsearch query.\n\n"
        f"Question: {question}\n\n"
    )
    if schema_context:
        prompt += f"Available fields and schema:\n{schema_context}\n\n"

    prompt += (
        "Return a valid Elasticsearch JSON query body. "
        "Also provide a brief explanation of what the query does."
    )

    if provider == "openai":
        result = generate_openai_insights(prompt, max_tokens=400)
    else:
        result = generate_bedrock_summary(prompt, max_tokens=400)

    return {
        "question": question,
        "generated_query": result["text"],
        "provider": result.get("provider", provider),
        "tokens_used": result.get("tokens_used", 0),
    }


def _prepare_event_summary(events: list) -> str:
    if len(events) > 100:
        events = events[:100]

    event_types = {}
    for event in events:
        etype = event.get("event_type", "unknown")
        event_types[etype] = event_types.get(etype, 0) + 1

    lines = [
        f"Total events: {len(events)}",
        f"Event types distribution: {event_types}",
        "",
        "Sample events:",
    ]

    for event in events[:10]:
        lines.append(
            f"  - Type: {event.get('event_type', 'N/A')}, "
            f"Timestamp: {event.get('timestamp', 'N/A')}, "
            f"Payload: {str(event.get('payload', {}))[:200]}"
        )

    return "\n".join(lines)
