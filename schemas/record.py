# schemas/record.py

from pydantic import BaseModel
from datetime import datetime


class RecordCreate(BaseModel):
    notes: str


class RecordOut(BaseModel):
    id: int
    patient_id: int
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True
