import logging
from django.conf import settings

logger = logging.getLogger("analytics")


def get_es_client():
    es_host = getattr(settings, "ELASTICSEARCH_HOST", "")
    if not es_host:
        return None
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch(
            hosts=[es_host],
            request_timeout=30,
        )
        if es.ping():
            return es
        logger.warning("Elasticsearch ping failed")
        return None
    except Exception as e:
        logger.warning(f"Elasticsearch client unavailable: {e}")
        return None


def index_event(event):
    es = get_es_client()
    if not es:
        return False

    try:
        doc = {
            "event_id": str(event.id),
            "event_type": event.event_type,
            "payload": event.payload,
            "metadata": event.metadata,
            "timestamp": event.timestamp.isoformat(),
            "source_id": str(event.source_id) if event.source else None,
        }
        es.index(
            index="datapulse-events",
            id=str(event.id),
            document=doc,
        )
        logger.info(f"Event {event.id} indexed in Elasticsearch")
        return True
    except Exception as e:
        logger.error(f"Failed to index event {event.id}: {e}")
        return False


def search_events(query, user, size=50):
    es = get_es_client()
    if not es:
        return {"results": [], "total": 0, "error": "Elasticsearch unavailable"}

    try:
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "event_type^3",
                                    "payload.*",
                                    "metadata.*",
                                ],
                                "fuzziness": "AUTO",
                            }
                        }
                    ]
                }
            },
            "sort": [{"timestamp": {"order": "desc"}}],
            "size": size,
            "highlight": {
                "fields": {
                    "event_type": {},
                    "payload.*": {},
                }
            },
        }

        response = es.search(index="datapulse-events", body=body)
        hits = response["hits"]

        results = []
        for hit in hits["hits"]:
            result = hit["_source"]
            result["score"] = hit["_score"]
            if "highlight" in hit:
                result["highlights"] = hit["highlight"]
            results.append(result)

        return {
            "results": results,
            "total": hits["total"]["value"],
            "max_score": hits.get("max_score"),
        }
    except Exception as e:
        logger.error(f"Elasticsearch search failed: {e}")
        return {"results": [], "total": 0, "error": str(e)}


def aggregate_events(field, interval="day", size=30):
    es = get_es_client()
    if not es:
        return {}

    try:
        body = {
            "size": 0,
            "aggs": {
                "events_over_time": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": interval,
                    }
                },
                "by_event_type": {
                    "terms": {
                        "field": "event_type.keyword",
                        "size": size,
                    }
                },
            },
        }

        response = es.search(index="datapulse-events", body=body)
        return response["aggregations"]
    except Exception as e:
        logger.error(f"Elasticsearch aggregation failed: {e}")
        return {}
