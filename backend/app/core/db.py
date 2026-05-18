from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings


def build_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        pool_pre_ping=True,
    )


def build_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def validate_migrations(engine: AsyncEngine, *, alembic_ini_path: str) -> None:
    from alembic.config import Config
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory

    def _check(connection) -> None:
        config = Config(alembic_ini_path)
        script = ScriptDirectory.from_config(config)
        context = MigrationContext.configure(connection)
        current_heads = context.get_current_heads()
        target_heads = script.get_heads()
        if not current_heads:
            raise RuntimeError("database is not migrated")
        for head in target_heads:
            if head not in current_heads:
                raise RuntimeError("database migration is out of date")

    async with engine.connect() as connection:
        await connection.run_sync(_check)
