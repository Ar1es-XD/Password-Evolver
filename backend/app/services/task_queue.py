from app.workers.celery_app import celery_app


def enqueue_simulation(simulation_id: str) -> str:
    result = celery_app.send_task("app.workers.tasks.run_simulation", args=[simulation_id])
    return result.id


def revoke_task(task_id: str) -> None:
    celery_app.control.revoke(task_id, terminate=False)
