# schemas/common.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)
    total: int
