# schemas/item.py
from pydantic import BaseModel, Field, constr
from typing import Optional, Literal

Unit = Literal["un", "ml", "cx", "pct"]  # ajuste se tiver mais

class ItemBase(BaseModel):
    name: constr(min_length=2, max_length=160)
    category: Optional[constr(min_length=2, max_length=80)] = None
    unit: Unit = "un"
    min_stock: int = Field(0, ge=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: constr(min_length=2, max_length=160) | None = None
    category: Optional[constr(min_length=2, max_length=80)] = None
    unit: Unit | None = None
    min_stock: int | None = Field(None, ge=0)

class ItemOut(ItemBase):
    id: int

    class Config:
        from_attributes = True

