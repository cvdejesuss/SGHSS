# schemas/user_admin.py
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

RoleLiteral = Literal["admin", "doctor", "nurse", "technician"]

class UserAdminBase(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    role: RoleLiteral = "technician"
    # Pode vir com máscara; normalizamos para 11 dígitos no router
    cpf: str = Field(min_length=11, max_length=14)

class UserAdminCreate(UserAdminBase):
    password: str = Field(min_length=4)

class UserAdminUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=4)
    role: Optional[RoleLiteral] = None
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=14)

class UserAdminOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleLiteral
    cpf: Optional[str] = None

    class Config:
        from_attributes = True

