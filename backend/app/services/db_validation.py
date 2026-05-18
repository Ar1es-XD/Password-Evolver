import logging

from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.db import validate_migrations

logger = logging.getLogger(__name__)


async def ensure_migrations(engine: AsyncEngine, alembic_ini_path: str) -> None:
    try:
        await validate_migrations(engine, alembic_ini_path=alembic_ini_path)
    except Exception as exc:
        logger.error("migration validation failed", extra={"error": str(exc)})
        raise
