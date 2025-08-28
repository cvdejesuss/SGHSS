# schemas/patient.py
from pydantic import BaseModel, constr
from typing import Optional
from datetime import date

class PatientCreate(BaseModel):
    name: constr(min_length=2, max_length=160)
    cpf: Optional[constr(min_length=11, max_length=14)] = None  # pode vir formatado; valide como preferir
    birth_date: Optional[date] = None

class PatientUpdate(BaseModel):
    name: constr(min_length=2, max_length=160) | None = None
    cpf: Optional[constr(min_length=11, max_length=14)] = None
    birth_date: Optional[date] = None

class PatientOut(BaseModel):
    id: int
    name: str
    cpf: Optional[str] = None
    birth_date: Optional[date] = None

    class Config:
        from_attributes = True

