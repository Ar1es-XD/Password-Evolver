from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.system import router as system_router
from app.api.router import api_router
from app.core.config import get_settings
from app.core.db import build_engine, build_session_maker
from app.core.exceptions import add_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import (
    BodySizeLimitMiddleware,
    MetricsMiddleware,
    RateLimitMiddleware,
    RequestIdMiddleware,
)
from app.core.observability import configure_tracing
from app.services.event_bus import RedisEventBus
from app.services.db_validation import ensure_migrations
from app.services.simulation_store import SimulationStore
from app.services.websocket_bridge import WebSocketBridge
from app.websocket.manager import WebSocketManager


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await ensure_migrations(app.state.db_engine, settings.alembic_ini_path)
        await app.state.websocket_bridge.start()
        yield
        await app.state.websocket_bridge.stop()
        await app.state.websocket_manager.close_all()
        await app.state.db_engine.dispose()

    app = FastAPI(title="Password Evolver API", version="1.0.0", lifespan=lifespan)

    app.state.settings = settings
    app.state.db_engine = build_engine(settings)
    app.state.db_sessionmaker = build_session_maker(app.state.db_engine)
    app.state.store = SimulationStore(app.state.db_sessionmaker)
    app.state.websocket_manager = WebSocketManager()
    app.state.event_bus = RedisEventBus(settings.redis_url, settings.redis_channel_prefix)
    app.state.websocket_bridge = WebSocketBridge(
        app.state.websocket_manager,
        app.state.event_bus,
        settings.redis_channel_prefix,
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(BodySizeLimitMiddleware, max_body_bytes=settings.max_body_bytes)
    app.add_middleware(RateLimitMiddleware, settings=settings)
    app.add_middleware(MetricsMiddleware)

    add_exception_handlers(app)
    configure_tracing(app, settings)

    app.include_router(api_router)
    app.include_router(system_router)

    return app


app = create_app()
