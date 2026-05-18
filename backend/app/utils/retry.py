import asyncio
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


async def retry_async(
    func: Callable[[], Awaitable[T]],
    *,
    attempts: int,
    delay: float,
) -> T:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            return await func()
        except Exception as exc:
            last_error = exc
            if delay > 0:
                await asyncio.sleep(delay)
    if last_error is None:
        raise RuntimeError("retry failed")
    raise last_error
