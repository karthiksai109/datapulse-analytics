import logging
from django.conf import settings

logger = logging.getLogger("analytics")


def get_mongo_client():
    try:
        from pymongo import MongoClient
        client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        return client
    except Exception as e:
        logger.warning(f"MongoDB client unavailable: {e}")
        return None


def get_mongo_db():
    client = get_mongo_client()
    if client:
        return client[settings.MONGODB_DB_NAME]
    return None


def store_raw_event(event_data):
    db = get_mongo_db()
    if not db:
        logger.warning("MongoDB unavailable, skipping raw event storage")
        return None

    try:
        collection = db["raw_events"]
        result = collection.insert_one(event_data)
        logger.info(f"Raw event stored in MongoDB: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Failed to store raw event in MongoDB: {e}")
        return None


def store_aggregated_metrics(metrics_data):
    db = get_mongo_db()
    if not db:
        return None

    try:
        collection = db["aggregated_metrics"]
        result = collection.insert_one(metrics_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Failed to store aggregated metrics: {e}")
        return None


def get_event_timeline(source_id, limit=100):
    db = get_mongo_db()
    if not db:
        return []

    try:
        collection = db["raw_events"]
        cursor = collection.find(
            {"source_id": source_id}
        ).sort("timestamp", -1).limit(limit)
        return list(cursor)
    except Exception as e:
        logger.error(f"Failed to fetch event timeline: {e}")
        return []


def get_aggregation_pipeline(event_type, group_by="hour"):
    db = get_mongo_db()
    if not db:
        return []

    try:
        collection = db["raw_events"]
        date_format = {
            "hour": {"$dateToString": {"format": "%Y-%m-%d %H:00", "date": "$timestamp"}},
            "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "month": {"$dateToString": {"format": "%Y-%m", "date": "$timestamp"}},
        }

        pipeline = [
            {"$match": {"event_type": event_type}},
            {"$group": {
                "_id": date_format.get(group_by, date_format["hour"]),
                "count": {"$sum": 1},
                "avg_value": {"$avg": "$payload.value"},
            }},
            {"$sort": {"_id": 1}},
        ]

        result = list(collection.aggregate(pipeline))
        return result
    except Exception as e:
        logger.error(f"MongoDB aggregation failed: {e}")
        return []
