import asyncio
import logging
from typing import Awaitable, Callable, Dict

logger = logging.getLogger(__name__)


class TaskSupervisor:
    def __init__(self) -> None:
        self._tasks: Dict[str, asyncio.Task] = {}

    def create(self, name: str, coroutine: Callable[[], Awaitable[None]]) -> None:
        if name in self._tasks:
            return
        task = asyncio.create_task(coroutine())
        task.add_done_callback(lambda t: self._handle_done(name, t))
        self._tasks[name] = task

    def _handle_done(self, name: str, task: asyncio.Task) -> None:
        try:
            task.result()
        except asyncio.CancelledError:
            logger.info("task cancelled", extra={"task": name})
        except Exception:
            logger.exception("task failed", extra={"task": name})
        finally:
            self._tasks.pop(name, None)

    async def shutdown(self) -> None:
        for task in list(self._tasks.values()):
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()
