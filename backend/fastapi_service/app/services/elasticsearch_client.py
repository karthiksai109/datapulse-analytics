import os
import logging
from typing import Optional

logger = logging.getLogger("datapulse-fastapi")

ES_HOST = os.environ.get("ELASTICSEARCH_HOST", "localhost:9200")


def get_es_client():
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch(hosts=[ES_HOST], request_timeout=30)
        if es.ping():
            return es
        logger.warning("Elasticsearch ping failed")
        return None
    except Exception as e:
        logger.warning(f"Elasticsearch unavailable: {e}")
        return None


def index_document(index: str, document: dict):
    es = get_es_client()
    if not es:
        return False
    try:
        es.index(index=index, document=document)
        return True
    except Exception as e:
        logger.error(f"ES index failed: {e}")
        return False


def bulk_index(index: str, documents: list):
    es = get_es_client()
    if not es:
        return False
    try:
        from elasticsearch.helpers import bulk
        actions = [
            {"_index": index, "_source": doc}
            for doc in documents
        ]
        success, errors = bulk(es, actions)
        logger.info(f"Bulk indexed {success} documents, {len(errors)} errors")
        return True
    except Exception as e:
        logger.error(f"ES bulk index failed: {e}")
        return False


def search_documents(
    index: str,
    query: str,
    size: int = 50,
    from_offset: int = 0,
    sort_by: Optional[str] = "timestamp",
    sort_order: Optional[str] = "desc",
    filters: Optional[dict] = None,
):
    es = get_es_client()
    if not es:
        return {"results": [], "total": 0, "error": "Elasticsearch unavailable"}

    try:
        must_clauses = [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["event_type^3", "payload.*", "metadata.*"],
                    "fuzziness": "AUTO",
                }
            }
        ]

        filter_clauses = []
        if filters:
            for field, value in filters.items():
                filter_clauses.append({"term": {f"{field}.keyword": value}})

        body = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses,
                }
            },
            "size": size,
            "from": from_offset,
            "highlight": {
                "fields": {"event_type": {}, "payload.*": {}}
            },
        }

        if sort_by:
            body["sort"] = [{sort_by: {"order": sort_order}}]

        response = es.search(index=index, body=body)
        hits = response["hits"]

        results = []
        for hit in hits["hits"]:
            result = hit["_source"]
            result["_score"] = hit["_score"]
            if "highlight" in hit:
                result["_highlights"] = hit["highlight"]
            results.append(result)

        return {
            "results": results,
            "total": hits["total"]["value"],
            "max_score": hits.get("max_score"),
        }
    except Exception as e:
        logger.error(f"ES search failed: {e}")
        return {"results": [], "total": 0, "error": str(e)}


def aggregate_data(index: str, field: str, interval: str = "day", size: int = 30):
    es = get_es_client()
    if not es:
        return {}
    try:
        body = {
            "size": 0,
            "aggs": {
                "over_time": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": interval,
                    }
                },
                "by_field": {
                    "terms": {"field": f"{field}.keyword", "size": size}
                },
            },
        }
        response = es.search(index=index, body=body)
        return response["aggregations"]
    except Exception as e:
        logger.error(f"ES aggregation failed: {e}")
        return {}


def get_suggestions(index: str, query: str):
    es = get_es_client()
    if not es:
        return []
    try:
        body = {
            "suggest": {
                "event_suggest": {
                    "prefix": query,
                    "completion": {"field": "event_type.suggest", "size": 5},
                }
            }
        }
        response = es.search(index=index, body=body)
        suggestions = []
        for option in response.get("suggest", {}).get("event_suggest", [{}])[0].get("options", []):
            suggestions.append(option["text"])
        return suggestions
    except Exception as e:
        logger.error(f"ES suggest failed: {e}")
        return []
