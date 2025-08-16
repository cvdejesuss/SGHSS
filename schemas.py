from pydantic import BaseModel
from datetime import datetime

# --- SCHEMAS DE PACIENTE ---
class PatientCreate(BaseModel):
    name: str
    age: int

class PatientOut(BaseModel):
    id: int
    name: str
    age: int

    class Config:
        from_attributes = True

# --- SCHEMAS DE CONSULTA ---
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

# --- SCHEMAS DE PRONTUÁRIO MÉDICO ---
class RecordCreate(BaseModel):
    notes: str

class RecordOut(BaseModel):
    id: int
    patient_id: int
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True  # ou orm_mode = True se estiver usando Pydantic v1