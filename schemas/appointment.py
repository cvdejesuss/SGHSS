# schemas/appointment.py
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class AppointmentCreate(BaseModel):
    patient_id: int
    professional_id: int
    date: datetime
    reason: str | None = None
    status: Literal["SCHEDULED", "DONE", "CANCELED", "NOSHOW"] = "SCHEDULED"

class AppointmentUpdate(BaseModel):
    # permite remarcação, alterar status/motivo
    date: datetime | None = None
    reason: str | None = None
    status: Literal["SCHEDULED", "DONE", "CANCELED", "NOSHOW"] | None = None

class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    professional_id: int
    date: datetime
    status: str
    reason: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

