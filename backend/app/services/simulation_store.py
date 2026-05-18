from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.db import Simulation
from app.models.schemas import SimulationCreate, SimulationStatus
from app.utils.id import generate_id


class SimulationStore:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker

    async def create(self, payload: SimulationCreate, *, default_charset: str, update_every: int) -> Simulation:
        simulation_id = generate_id()
        charset = payload.charset or default_charset
        update_every_value = payload.update_every or update_every
        simulation = Simulation(
            id=simulation_id,
            target=payload.target,
            charset=charset,
            update_every=update_every_value,
            status="queued",
        )
        async with self._sessionmaker() as session:
            session.add(simulation)
            await session.commit()
        return simulation

    async def count_active(self) -> int:
        async with self._sessionmaker() as session:
            result = await session.execute(
                select(func.count()).select_from(Simulation).where(
                    Simulation.status.in_(["queued", "running"])
                )
            )
            return int(result.scalar() or 0)

    async def get(self, simulation_id: str) -> Optional[Simulation]:
        async with self._sessionmaker() as session:
            result = await session.execute(
                select(Simulation).where(Simulation.id == simulation_id)
            )
            return result.scalar_one_or_none()

    async def update_task_id(self, simulation_id: str, task_id: str) -> None:
        async with self._sessionmaker() as session:
            result = await session.execute(
                select(Simulation).where(Simulation.id == simulation_id)
            )
            simulation = result.scalar_one_or_none()
            if simulation is None:
                return
            simulation.task_id = task_id
            simulation.updated_at = datetime.utcnow()
            await session.commit()

    async def mark_status(self, simulation_id: str, status: str, *, completed: bool = False) -> None:
        async with self._sessionmaker() as session:
            result = await session.execute(
                select(Simulation).where(Simulation.id == simulation_id)
            )
            simulation = result.scalar_one_or_none()
            if simulation is None:
                return
            simulation.status = status
            simulation.completed = completed
            simulation.updated_at = datetime.utcnow()
            await session.commit()

    async def update_progress(
        self,
        simulation_id: str,
        *,
        current: str,
        attempts: int,
        matched: int,
        progress: float,
        elapsed: float,
        speed: float,
        status: str,
        completed: bool,
    ) -> Optional[SimulationStatus]:
        async with self._sessionmaker() as session:
            result = await session.execute(
                select(Simulation).where(Simulation.id == simulation_id)
            )
            simulation = result.scalar_one_or_none()
            if simulation is None:
                return None
            simulation.current = current
            simulation.attempts = attempts
            simulation.matched = matched
            simulation.progress = progress
            simulation.elapsed = elapsed
            simulation.speed = speed
            simulation.status = status
            simulation.completed = completed
            simulation.updated_at = datetime.utcnow()
            await session.commit()
            return self._to_status(simulation)

    async def get_status(self, simulation_id: str) -> Optional[SimulationStatus]:
        simulation = await self.get(simulation_id)
        if simulation is None:
            return None
        return self._to_status(simulation)

    async def is_canceled(self, simulation_id: str) -> bool:
        simulation = await self.get(simulation_id)
        return simulation is not None and simulation.status == "canceled"

    def _to_status(self, simulation: Simulation) -> SimulationStatus:
        return SimulationStatus(
            id=simulation.id,
            target=simulation.target,
            current=simulation.current,
            attempts=simulation.attempts,
            matched=simulation.matched,
            progress=simulation.progress,
            elapsed=simulation.elapsed,
            speed=simulation.speed,
            completed=simulation.completed,
        )
