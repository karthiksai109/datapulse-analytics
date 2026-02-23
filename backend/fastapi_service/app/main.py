import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import ingestion, search, websocket_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("datapulse-fastapi")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DataPulse FastAPI ingestion service")
    if os.environ.get("KAFKA_BOOTSTRAP_SERVERS"):
        try:
            from .services.kafka_consumer import start_consumer, stop_consumer
            await start_consumer()
        except Exception as e:
            logger.warning(f"Kafka consumer not started: {e}")
    yield
    logger.info("Shutting down DataPulse FastAPI ingestion service")


app = FastAPI(
    title="DataPulse Ingestion Service",
    description="High-performance data ingestion and real-time streaming service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ingestion.router, prefix="/api/v1/ingest", tags=["Ingestion"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(websocket_router.router, prefix="/ws", tags=["WebSocket"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "datapulse-fastapi-ingestion"}


@app.get("/")
async def root():
    return {
        "service": "DataPulse Ingestion Service",
        "version": "1.0.0",
        "docs": "/docs",
    }
