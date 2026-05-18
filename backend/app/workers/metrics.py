import time
from typing import Optional

from prometheus_client import CollectorRegistry, Counter, Histogram, push_to_gateway

from app.core.config import Settings

registry = CollectorRegistry()

TASKS_TOTAL = Counter(
    "worker_tasks_total",
    "Total simulation tasks",
    ["status"],
    registry=registry,
)
TASK_DURATION = Histogram(
    "worker_task_duration_seconds",
    "Duration of simulation tasks",
    registry=registry,
)


def record_task(status: str, duration: float, settings: Settings) -> None:
    TASKS_TOTAL.labels(status=status).inc()
    TASK_DURATION.observe(duration)
    pushgateway = settings.worker_metrics_pushgateway
    if pushgateway:
        push_to_gateway(pushgateway, job=settings.worker_metrics_job, registry=registry)


def timer_start() -> float:
    return time.perf_counter()
