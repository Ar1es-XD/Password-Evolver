from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.utils.sanitize import sanitize_text


class SimulationCreate(BaseModel):
    target: str = Field(min_length=1, max_length=2048)
    charset: Optional[str] = None
    update_every: Optional[int] = Field(default=None, ge=1, le=10000)

    @field_validator("target")
    @classmethod
    def sanitize_target(cls, value: str) -> str:
        cleaned = sanitize_text(value)
        if not cleaned:
            raise ValueError("target must not be empty")
        return cleaned

    @field_validator("charset")
    @classmethod
    def sanitize_charset(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = sanitize_text(value)
        if not cleaned:
            raise ValueError("charset must not be empty")
        if len(cleaned) > 4096:
            raise ValueError("charset too long")
        return cleaned


class SimulationStatus(BaseModel):
    id: str
    target: str
    current: str
    attempts: int
    matched: int
    progress: float
    elapsed: float
    speed: float
    completed: bool


class SimulationEvent(BaseModel):
    type: str
    data: SimulationStatus
