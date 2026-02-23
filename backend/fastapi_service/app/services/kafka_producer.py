import os
import json
import logging

logger = logging.getLogger("datapulse-fastapi")

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def get_producer():
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=3,
        )
        return producer
    except Exception as e:
        logger.warning(f"Kafka producer unavailable: {e}")
        return None


async def produce_event(topic: str, event_data: dict):
    producer = get_producer()
    if not producer:
        logger.warning(f"Skipping Kafka publish - producer unavailable")
        return False

    try:
        key = event_data.get("event_type", "unknown")
        future = producer.send(topic, key=key, value=event_data)
        record_metadata = future.get(timeout=10)
        logger.info(
            f"Published to {record_metadata.topic}[{record_metadata.partition}] "
            f"offset={record_metadata.offset}"
        )
        return True
    except Exception as e:
        logger.error(f"Kafka publish failed: {e}")
        return False
    finally:
        producer.close()
