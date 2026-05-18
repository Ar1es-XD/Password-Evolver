from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "password-evolver",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue="simulations",
    broker_transport_options={"visibility_timeout": 3600},
    beat_schedule={
        "worker-heartbeat": {
            "task": "app.workers.tasks.emit_worker_heartbeat",
            "schedule": settings.worker_heartbeat_interval,
        }
    },
)

celery_app.autodiscover_tasks(["app.workers"])
