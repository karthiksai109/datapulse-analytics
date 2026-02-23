import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from ..services.kafka_producer import produce_event
from ..services.elasticsearch_client import index_document, bulk_index

logger = logging.getLogger("datapulse-fastapi")
router = APIRouter()


class EventPayload(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=100)
    source_id: Optional[str] = None
    payload: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
    timestamp: Optional[datetime] = None


class BulkIngestRequest(BaseModel):
    events: List[EventPayload] = Field(..., min_length=1, max_length=1000)


class IngestResponse(BaseModel):
    status: str
    event_id: Optional[str] = None
    message: str


@router.post("/event", response_model=IngestResponse)
async def ingest_event(event: EventPayload, background_tasks: BackgroundTasks):
    try:
        if not event.timestamp:
            event.timestamp = datetime.utcnow()

        event_dict = event.model_dump()

        # Publish to Kafka for downstream consumers
        background_tasks.add_task(produce_event, "datapulse-events", event_dict)

        # Index in Elasticsearch for search
        background_tasks.add_task(
            index_document, "datapulse-events", event_dict
        )

        logger.info(f"Event ingested: type={event.event_type}")
        return IngestResponse(
            status="accepted",
            message=f"Event '{event.event_type}' queued for processing",
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=dict)
async def bulk_ingest(request: BulkIngestRequest, background_tasks: BackgroundTasks):
    try:
        events = []
        for event in request.events:
            if not event.timestamp:
                event.timestamp = datetime.utcnow()
            events.append(event.model_dump())

        # Bulk publish to Kafka
        for event_dict in events:
            background_tasks.add_task(produce_event, "datapulse-events", event_dict)

        # Bulk index in Elasticsearch
        background_tasks.add_task(bulk_index, "datapulse-events", events)

        logger.info(f"Bulk ingested {len(events)} events")
        return {"status": "accepted", "count": len(events)}
    except Exception as e:
        logger.error(f"Bulk ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/{source_id}")
async def webhook_ingest(source_id: str, payload: dict, background_tasks: BackgroundTasks):
    try:
        event_dict = {
            "event_type": "webhook",
            "source_id": source_id,
            "payload": payload,
            "metadata": {"ingestion_method": "webhook"},
            "timestamp": datetime.utcnow().isoformat(),
        }

        background_tasks.add_task(produce_event, "datapulse-events", event_dict)
        background_tasks.add_task(index_document, "datapulse-events", event_dict)

        logger.info(f"Webhook event from source {source_id}")
        return {"status": "accepted", "source_id": source_id}
    except Exception as e:
        logger.error(f"Webhook ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
