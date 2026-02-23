import json
import logging
import asyncio
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("datapulse-fastapi")
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: dict = {}

    async def connect(self, websocket: WebSocket, channel: str = "default"):
        await websocket.accept()
        self.active_connections.append(websocket)
        if channel not in self.subscriptions:
            self.subscriptions[channel] = []
        self.subscriptions[channel].append(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        for channel, connections in self.subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        logger.info("WebSocket disconnected")

    async def broadcast(self, message: dict, channel: str = "default"):
        connections = self.subscriptions.get(channel, [])
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/events/{channel}")
async def websocket_events(websocket: WebSocket, channel: str):
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "subscribe":
                new_channel = message.get("channel", channel)
                if new_channel not in manager.subscriptions:
                    manager.subscriptions[new_channel] = []
                manager.subscriptions[new_channel].append(websocket)
                await manager.send_personal(
                    websocket,
                    {"type": "subscribed", "channel": new_channel},
                )

            elif message.get("type") == "ping":
                await manager.send_personal(
                    websocket,
                    {"type": "pong", "timestamp": message.get("timestamp")},
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client disconnected from channel: {channel}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/dashboard/{dashboard_id}")
async def websocket_dashboard(websocket: WebSocket, dashboard_id: str):
    channel = f"dashboard-{dashboard_id}"
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await manager.broadcast(
                {"type": "dashboard_update", "data": message},
                channel=channel,
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def push_event_to_clients(event_data: dict, channel: str = "default"):
    await manager.broadcast(
        {"type": "new_event", "data": event_data},
        channel=channel,
    )
