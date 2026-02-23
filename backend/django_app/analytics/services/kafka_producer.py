import json
import logging
from django.conf import settings

logger = logging.getLogger("analytics")


def get_kafka_producer():
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=3,
            max_in_flight_requests_per_connection=1,
        )
        return producer
    except Exception as e:
        logger.warning(f"Kafka producer unavailable: {e}")
        return None


def publish_event(event):
    producer = get_kafka_producer()
    if not producer:
        logger.warning(f"Skipping Kafka publish for event {event.id} - producer unavailable")
        return False

    try:
        payload = {
            "event_id": str(event.id),
            "event_type": event.event_type,
            "payload": event.payload,
            "metadata": event.metadata,
            "timestamp": str(event.timestamp),
        }
        future = producer.send(
            settings.KAFKA_TOPIC_EVENTS,
            key=event.event_type,
            value=payload,
        )
        record_metadata = future.get(timeout=10)
        logger.info(
            f"Event {event.id} published to Kafka topic={record_metadata.topic} "
            f"partition={record_metadata.partition} offset={record_metadata.offset}"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to publish event {event.id} to Kafka: {e}")
        return False
    finally:
        producer.close()


def publish_alert_trigger(alert, event):
    producer = get_kafka_producer()
    if not producer:
        return False

    try:
        payload = {
            "alert_id": str(alert.id),
            "alert_name": alert.name,
            "severity": alert.severity,
            "triggered_by_event": str(event.id),
            "timestamp": str(event.timestamp),
        }
        producer.send(
            "datapulse-alerts",
            key=alert.severity,
            value=payload,
        )
        producer.flush()
        logger.info(f"Alert trigger published for alert {alert.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish alert trigger: {e}")
        return False
    finally:
        producer.close()
