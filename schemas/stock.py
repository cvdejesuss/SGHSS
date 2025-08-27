# schemas/stock.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class MovementCreate(BaseModel):
    item_id: int
    type: str  # "IN" | "OUT"
    quantity: int = Field(gt=0)
    reason: Optional[str] = None
    lot: Optional[str] = None
    expiration_date: Optional[date] = None

class MovementOut(MovementCreate):
    id: int
    class Config:
        from_attributes = True
