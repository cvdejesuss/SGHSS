# schemas/item.py

from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    category: Optional[str] = None
    unit: str = "un"
    min_stock: int = 0

class ItemCreate(ItemBase): pass

class ItemOut(ItemBase):
    id: int
    class Config:
        from_attributes = True
