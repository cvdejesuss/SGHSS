# schemas/stock.py
from pydantic import BaseModel, Field, constr
from typing import Optional, Literal
from datetime import date, datetime

MovementType = Literal["IN", "OUT"]

class MovementCreate(BaseModel):
    item_id: int
    type: MovementType  # "IN" | "OUT"
    quantity: int = Field(..., gt=0)
    reason: Optional[constr(max_length=160)] = None
    lot: Optional[constr(max_length=64)] = None
    expiration_date: Optional[date] = None

class MovementOut(BaseModel):
    id: int
    item_id: int
    type: MovementType
    quantity: int
    reason: Optional[str] = None
    lot: Optional[str] = None
    expiration_date: Optional[date] = None
    created_at: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

