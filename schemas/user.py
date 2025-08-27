# schemas/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    role: Optional[str] = "atendente"  # admin, medico, atendente


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True  # ou orm_mode = True se Pydantic v1
