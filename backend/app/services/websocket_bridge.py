import asyncio
import json
import logging

from app.services.event_bus import RedisEventBus
from app.websocket.manager import WebSocketManager

logger = logging.getLogger(__name__)


class WebSocketBridge:
    def __init__(self, manager: WebSocketManager, event_bus: RedisEventBus, channel_prefix: str) -> None:
        self._manager = manager
        self._event_bus = event_bus
        self._pattern = f"{channel_prefix}*"
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._task:
            return
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
            self._task = None
        await self._event_bus.close()

    async def _run(self) -> None:
        try:
            async for message in self._event_bus.subscribe(self._pattern):
                channel = message.get("channel")
                if not channel:
                    continue
                if isinstance(channel, bytes):
                    channel = channel.decode("utf-8")
                simulation_id = channel.split(":")[-1]
                data = message.get("data")
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                try:
                    payload = json.loads(data)
                except Exception:
                    continue
                await self._manager.broadcast(simulation_id, payload)
        except asyncio.CancelledError:
            logger.info("websocket bridge stopped")
        except Exception:
            logger.exception("websocket bridge failed")
