import os
import json
import logging
import asyncio
from typing import Optional

logger = logging.getLogger("datapulse-fastapi")

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_CONSUMER_GROUP = os.environ.get("KAFKA_CONSUMER_GROUP", "datapulse-fastapi-consumer")

_consumer_task: Optional[asyncio.Task] = None


async def start_consumer():
    global _consumer_task
    try:
        _consumer_task = asyncio.create_task(_consume_events())
        logger.info("Kafka consumer started")
    except Exception as e:
        logger.warning(f"Kafka consumer could not start: {e}")


async def stop_consumer():
    global _consumer_task
    if _consumer_task:
        _consumer_task.cancel()
        try:
            await _consumer_task
        except asyncio.CancelledError:
            pass
        logger.info("Kafka consumer stopped")


async def _consume_events():
    try:
        from kafka import KafkaConsumer
    except ImportError:
        logger.warning("kafka-python not installed, consumer disabled")
        return

    try:
        consumer = KafkaConsumer(
            "datapulse-events",
            "datapulse-alerts",
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            consumer_timeout_ms=1000,
        )

        logger.info("Kafka consumer connected, listening for events...")

        while True:
            messages = consumer.poll(timeout_ms=500)
            for topic_partition, records in messages.items():
                for record in records:
                    await _process_message(record.topic, record.value)
            await asyncio.sleep(0.1)

    except Exception as e:
        logger.error(f"Kafka consumer error: {e}")
        await asyncio.sleep(5)


async def _process_message(topic: str, message: dict):
    try:
        if topic == "datapulse-events":
            await _handle_event(message)
        elif topic == "datapulse-alerts":
            await _handle_alert(message)
        else:
            logger.warning(f"Unknown topic: {topic}")
    except Exception as e:
        logger.error(f"Error processing message from {topic}: {e}")


async def _handle_event(event_data: dict):
    from ..routers.websocket_router import push_event_to_clients

    event_type = event_data.get("event_type", "unknown")
    logger.info(f"Processing event: {event_type}")

    # Push to WebSocket clients for real-time updates
    await push_event_to_clients(event_data, channel=event_type)
    await push_event_to_clients(event_data, channel="default")


async def _handle_alert(alert_data: dict):
    from ..routers.websocket_router import push_event_to_clients

    alert_name = alert_data.get("alert_name", "unknown")
    severity = alert_data.get("severity", "medium")
    logger.warning(f"Alert triggered: {alert_name} (severity={severity})")

    await push_event_to_clients(
        {"type": "alert", "data": alert_data},
        channel="alerts",
    )
