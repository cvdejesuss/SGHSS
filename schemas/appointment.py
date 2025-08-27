# schemas/appointment.py

from pydantic import BaseModel
from datetime import datetime


class AppointmentCreate(BaseModel):
    patient_id: int
    date: datetime
    reason: str


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    date: datetime
    reason: str

    class Config:
        from_attributes = True
