# schemas/user.py
from pydantic import BaseModel, EmailStr, constr
from typing import Optional, Literal

Role = Literal["user", "admin", "medico", "atendente"]  # alinhe com o que o sistema usa

class UserBase(BaseModel):
    name: constr(min_length=2, max_length=160)
    email: EmailStr
    cpf: constr(min_length=11, max_length=14)
    role: Role = "user"

class UserCreate(UserBase):
    password: constr(min_length=6, max_length=255)

class UserUpdate(BaseModel):
    name: constr(min_length=2, max_length=160) | None = None
    email: EmailStr | None = None
    cpf: constr(min_length=11, max_length=14) | None = None
    role: Role | None = None
    password: constr(min_length=6, max_length=255) | None = None

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True
