import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket

from app.core.config import Settings, get_settings
from app.models.schemas import SimulationCreate, SimulationStatus
from app.services.simulation_store import SimulationStore
from app.services.task_queue import enqueue_simulation, revoke_task
from app.websocket.manager import WebSocketManager

router = APIRouter()


def get_store(request: Request) -> SimulationStore:
    return request.app.state.store


def get_ws_manager(request: Request) -> WebSocketManager:
    return request.app.state.websocket_manager


def get_settings_dep() -> Settings:
    return get_settings()


@router.post("/simulations", response_model=SimulationStatus)
async def create_simulation(
    payload: SimulationCreate,
    store: SimulationStore = Depends(get_store),
    settings: Settings = Depends(get_settings_dep),
) -> SimulationStatus:
    if await store.count_active() >= settings.max_active_simulations:
        raise HTTPException(status_code=429, detail="simulation capacity reached")
    if len(payload.target) > settings.max_target_length:
        raise HTTPException(status_code=422, detail="target too long")
    if payload.charset and len(payload.charset) > settings.max_charset_length:
        raise HTTPException(status_code=422, detail="charset too long")
    state = await store.create(payload, default_charset=settings.default_charset, update_every=settings.update_every)
    task_id = enqueue_simulation(state.id)
    await store.update_task_id(state.id, task_id)
    status = await store.get_status(state.id)
    if status is None:
        raise HTTPException(status_code=404, detail="simulation not found")
    return status


@router.get("/simulations/{simulation_id}", response_model=SimulationStatus)
async def get_simulation(
    simulation_id: str,
    store: SimulationStore = Depends(get_store),
) -> SimulationStatus:
    status = await store.get_status(simulation_id)
    if status is None:
        raise HTTPException(status_code=404, detail="simulation not found")
    return status


@router.delete("/simulations/{simulation_id}")
async def stop_simulation(
    simulation_id: str,
    store: SimulationStore = Depends(get_store),
) -> dict:
    simulation = await store.get(simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail="simulation not found")
    if simulation.task_id:
        revoke_task(simulation.task_id)
    await store.mark_status(simulation_id, "canceled")
    return {"status": "stopped"}


@router.websocket("/ws/simulations/{simulation_id}")
async def simulation_ws(
    websocket: WebSocket,
    simulation_id: str,
    ws_manager: WebSocketManager = Depends(get_ws_manager),
    store: SimulationStore = Depends(get_store),
    settings: Settings = Depends(get_settings_dep),
) -> None:
    await ws_manager.connect(simulation_id, websocket)
    try:
        status = await store.get_status(simulation_id)
        if status is not None:
            await websocket.send_json(status.model_dump())
        missed = 0
        interval = settings.websocket_heartbeat_interval
        max_missed = settings.websocket_max_missed
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=interval)
                if message == "pong":
                    missed = 0
                elif message == "ping":
                    await websocket.send_text("pong")
                else:
                    missed = 0
            except asyncio.TimeoutError:
                missed += 1
                await websocket.send_text("ping")
                if missed >= max_missed:
                    break
    except Exception:
        pass
    finally:
        await ws_manager.disconnect(simulation_id, websocket)
