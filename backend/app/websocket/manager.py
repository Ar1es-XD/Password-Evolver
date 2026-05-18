import asyncio
from typing import Dict, Set

from fastapi import WebSocket

from app.utils.retry import retry_async


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, simulation_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(simulation_id, set()).add(websocket)

    async def disconnect(self, simulation_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            group = self._connections.get(simulation_id)
            if not group:
                return
            group.discard(websocket)
            if not group:
                self._connections.pop(simulation_id, None)

    async def broadcast(self, simulation_id: str, message: dict) -> None:
        async with self._lock:
            group = list(self._connections.get(simulation_id, set()))
        for websocket in group:
            try:
                await retry_async(lambda: websocket.send_json(message), attempts=2, delay=0.05)
            except Exception:
                await self.disconnect(simulation_id, websocket)

    async def send_to(self, simulation_id: str, message: dict) -> None:
        await self.broadcast(simulation_id, message)

    async def close_all(self) -> None:
        async with self._lock:
            connections = [(sid, list(sockets)) for sid, sockets in self._connections.items()]
            self._connections.clear()
        for simulation_id, sockets in connections:
            for websocket in sockets:
                try:
                    await websocket.close()
                except Exception:
                    pass
