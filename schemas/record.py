# schemas/record.py
from pydantic import BaseModel, constr
from datetime import datetime

class RecordCreate(BaseModel):
    patient_id: int
    notes: constr(min_length=1)

class RecordUpdate(BaseModel):
    notes: constr(min_length=1) | None = None

class RecordOut(BaseModel):
    id: int
    patient_id: int
    professional_id: int
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True

