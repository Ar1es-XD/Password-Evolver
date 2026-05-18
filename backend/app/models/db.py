from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Simulation(Base):
    __tablename__ = "simulations"
    __table_args__ = (
        Index("ix_simulations_status", "status"),
        Index("ix_simulations_created_at", "created_at"),
        Index("ix_simulations_task_id", "task_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    target: Mapped[str] = mapped_column(String(2048))
    charset: Mapped[str] = mapped_column(String(4096))
    update_every: Mapped[int] = mapped_column(Integer)
    current: Mapped[str] = mapped_column(String(2048), default="")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    matched: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    elapsed: Mapped[float] = mapped_column(Float, default=0.0)
    speed: Mapped[float] = mapped_column(Float, default=0.0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    task_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
