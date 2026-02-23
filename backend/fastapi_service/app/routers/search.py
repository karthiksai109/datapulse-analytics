import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from ..services.elasticsearch_client import search_documents, aggregate_data

logger = logging.getLogger("datapulse-fastapi")
router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    index: str = "datapulse-events"
    size: int = 50
    from_offset: int = 0
    sort_by: Optional[str] = "timestamp"
    sort_order: Optional[str] = "desc"


@router.post("/query")
async def search_events(request: SearchRequest):
    try:
        results = search_documents(
            index=request.index,
            query=request.query,
            size=request.size,
            from_offset=request.from_offset,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
        )
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events")
async def search_events_get(
    q: str = Query(..., min_length=1),
    event_type: Optional[str] = None,
    size: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        filters = {}
        if event_type:
            filters["event_type"] = event_type

        results = search_documents(
            index="datapulse-events",
            query=q,
            size=size,
            from_offset=offset,
            filters=filters,
        )
        return results
    except Exception as e:
        logger.error(f"Event search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aggregate")
async def aggregate_events(
    field: str = Query(default="event_type"),
    interval: str = Query(default="day"),
    size: int = Query(default=30, le=100),
):
    try:
        results = aggregate_data(
            index="datapulse-events",
            field=field,
            interval=interval,
            size=size,
        )
        return results
    except Exception as e:
        logger.error(f"Aggregation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest")
async def suggest_queries(q: str = Query(..., min_length=1)):
    try:
        from ..services.elasticsearch_client import get_suggestions
        suggestions = get_suggestions("datapulse-events", q)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
