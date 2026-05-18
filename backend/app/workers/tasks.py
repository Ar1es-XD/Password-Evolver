import asyncio
import json
import logging
import random
import time

import redis

from app.core.config import get_settings
from app.core.db import build_engine, build_session_maker
from app.services.metrics_service import MetricsService
from app.services.simulation_store import SimulationStore
from app.workers.celery_app import celery_app
from app.workers.metrics import record_task, timer_start

logger = logging.getLogger(__name__)


def _redis_client(settings):
    return redis.Redis.from_url(settings.redis_url)


async def _run_simulation(simulation_id: str) -> None:
    settings = get_settings()
    engine = build_engine(settings)
    sessionmaker = build_session_maker(engine)
    store = SimulationStore(sessionmaker)
    metrics = MetricsService()
    redis_client = _redis_client(settings)

    simulation = await store.get(simulation_id)
    if simulation is None:
        return

    await store.mark_status(simulation_id, "running")

    charset = simulation.charset or settings.default_charset
    update_every = simulation.update_every or settings.update_every
    target = list(simulation.target)
    current = list(simulation.current) if simulation.current else [random.choice(charset) for _ in target]
    attempts = simulation.attempts
    start_time = time.time()

    try:
        matched = sum(1 for c, w in zip(current, target) if c == w)
        metric = metrics.compute(
            matched=matched,
            total=len(target),
            elapsed=0.0,
            attempts=attempts,
        )
        status = await store.update_progress(
            simulation_id,
            current="".join(current),
            attempts=attempts,
            matched=metric.matched,
            progress=metric.progress,
            elapsed=metric.elapsed,
            speed=metric.speed,
            status="running",
            completed=False,
        )
        if status:
            redis_client.publish(
                f"{settings.redis_channel_prefix}{simulation_id}",
                status.model_dump_json(),
            )

        while current != target:
            attempts += 1
            for i, wanted in enumerate(target):
                if current[i] != wanted:
                    current[i] = random.choice(charset)

            should_update = attempts % update_every == 0
            if should_update:
                if await store.is_canceled(simulation_id):
                    await store.mark_status(simulation_id, "canceled")
                    canceled_status = await store.get_status(simulation_id)
                    if canceled_status:
                        redis_client.publish(
                            f"{settings.redis_channel_prefix}{simulation_id}",
                            canceled_status.model_dump_json(),
                        )
                    return

                matched = sum(1 for c, w in zip(current, target) if c == w)
                elapsed = max(time.time() - start_time, 0.0)
                metric = metrics.compute(
                    matched=matched,
                    total=len(target),
                    elapsed=elapsed,
                    attempts=attempts,
                )
                status = await store.update_progress(
                    simulation_id,
                    current="".join(current),
                    attempts=attempts,
                    matched=metric.matched,
                    progress=metric.progress,
                    elapsed=metric.elapsed,
                    speed=metric.speed,
                    status="running",
                    completed=False,
                )
                if status:
                    redis_client.publish(
                        f"{settings.redis_channel_prefix}{simulation_id}",
                        status.model_dump_json(),
                    )

            if settings.step_delay:
                await asyncio.sleep(settings.step_delay)

        matched = len(target)
        elapsed = max(time.time() - start_time, 0.0)
        metric = metrics.compute(
            matched=matched,
            total=len(target),
            elapsed=elapsed,
            attempts=attempts,
        )
        status = await store.update_progress(
            simulation_id,
            current="".join(current),
            attempts=attempts,
            matched=metric.matched,
            progress=metric.progress,
            elapsed=metric.elapsed,
            speed=metric.speed,
            status="completed",
            completed=True,
        )
        if status:
            redis_client.publish(
                f"{settings.redis_channel_prefix}{simulation_id}",
                status.model_dump_json(),
            )
    finally:
        await engine.dispose()


async def _mark_failed(simulation_id: str) -> None:
    settings = get_settings()
    engine = build_engine(settings)
    sessionmaker = build_session_maker(engine)
    store = SimulationStore(sessionmaker)
    await store.mark_status(simulation_id, "failed")
    status = await store.get_status(simulation_id)
    if status:
        redis_client = _redis_client(settings)
        redis_client.publish(
            f"{settings.redis_channel_prefix}{simulation_id}",
            status.model_dump_json(),
        )
    await engine.dispose()


@celery_app.task(bind=True, name="app.workers.tasks.run_simulation")
def run_simulation(self, simulation_id: str) -> None:
    settings = get_settings()
    start = timer_start()
    try:
        asyncio.run(_run_simulation(simulation_id))
        record_task("success", time.perf_counter() - start, settings)
    except Exception:
        logger.exception("simulation task failed", extra={"simulation_id": simulation_id})
        try:
            asyncio.run(_mark_failed(simulation_id))
        except Exception:
            logger.exception("failed to mark simulation failed", extra={"simulation_id": simulation_id})
        record_task("failed", time.perf_counter() - start, settings)
        raise


@celery_app.task(name="app.workers.tasks.emit_worker_heartbeat")
def emit_worker_heartbeat() -> None:
    settings = get_settings()
    redis_client = _redis_client(settings)
    payload = {
        "timestamp": time.time(),
        "worker": celery_app.connection().as_uri(),
    }
    redis_client.publish(
        settings.worker_heartbeat_channel,
        json.dumps(payload),
    )
