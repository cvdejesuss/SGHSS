# schemas/patient.py

from pydantic import BaseModel
from typing import Optional
from datetime import date

class PatientCreate(BaseModel):
    name: str
    age: int


class PatientOut(BaseModel):
    id: int
    name: str
    age: int

    class Config:
        from_attributes = True
