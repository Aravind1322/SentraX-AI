"""
SentraX AI Backend — utils/connection_manager.py
WebSocket connection manager for real-time alert, dashboard, and scan-feed broadcasts.

Supports named channels so different streams can fan-out independently:
  - "alerts"    → security alert toasts
  - "dashboard" → live KPI metric updates
  - "scans"     → live recent-scan feed updates
"""

from fastapi import WebSocket
from typing import Dict, List
import asyncio


class ConnectionManager:
    """
    Manages active WebSocket connections per named channel.
    Thread-safe broadcast to all listeners on a channel.
    Dead connections are silently removed.
    """

    def __init__(self):
        # channel -> list of active websockets
        self.channels: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "alerts"):
        await websocket.accept()
        self.channels.setdefault(channel, []).append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "alerts"):
        conns = self.channels.get(channel, [])
        if websocket in conns:
            conns.remove(websocket)

    async def broadcast(self, message: dict, channel: str = "alerts"):
        """Send JSON message to every connected client on the given channel."""
        for ws in list(self.channels.get(channel, [])):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws, channel)

    def connection_count(self, channel: str = "alerts") -> int:
        return len(self.channels.get(channel, []))


# Global singleton used across all route modules and services
manager = ConnectionManager()
