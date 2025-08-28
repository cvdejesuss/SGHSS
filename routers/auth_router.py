# routers/auth_router.py

from datetime import timedelta
from typing import Annotated, Literal
import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from core.config import settings   # 👈 agora usamos settings
from auth.jwt_handler import create_access_token
from auth.auth_utils import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


# ======== SCHEMAS ========

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


RoleLiteral = Literal["admin", "medico", "atendente", "user"]

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=4)
    cpf: str = Field(min_length=11, max_length=14)  # pode vir formatado ###.###.###-##
    role: RoleLiteral = "user"   # valor default seguro


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    user_id: int
    role: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True  # Pydantic v2


# ======== HELPERS ========

def _verify_password(plain: str, hashed: str) -> bool:
    """Confere senha em texto puro com hash armazenado."""
    try:
        return settings.pwd_context.verify(plain, hashed)
    except Exception:
        return False


def _hash_password(plain: str) -> str:
    """Gera hash da senha para salvar no banco."""
    return settings.pwd_context.hash(plain)


def _only_digits(s: str) -> str:
    """Remove caracteres não numéricos (útil para CPF)."""
    return re.sub(r"\D", "", s or "")


def require_role(allowed: list[str]):
    """
    Dependência para proteger rotas por papel.
    Exemplo:
        @router.get("/admin-only")
        def admin_only(current=Depends(require_role(["admin"]))):
            return {"ok": True}
    """
    def _dep(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed:
            raise HTTPException(status_code=403, detail="Permissão negada")
        return current_user
    return _dep


# ======== ROUTES ========

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Autentica por e-mail/senha e retorna um JWT.
    """
    email = str(data.email).strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user or not _verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    # expiração real baseada no settings
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = create_access_token(
        sub=user.email,
        extra={"uid": user.id, "role": user.role},
        expires_delta=expires_delta,
    )

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        role=user.role,
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)) -> UserOut:
    """
    Registra um novo usuário.
    """
    name = data.name.strip()
    email = str(data.email).strip().lower()
    role = str(data.role).strip().lower()
    cpf_digits = _only_digits(data.cpf)

    if len(cpf_digits) != 11:
        raise HTTPException(status_code=400, detail="CPF deve conter 11 dígitos.")

    # Verifica duplicidade
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    if db.query(User).filter(User.cpf == cpf_digits).first():
        raise HTTPException(status_code=409, detail="CPF já cadastrado")

    user = User(
        name=name,
        email=email,
        password=_hash_password(data.password),
        role=role,
        cpf=cpf_digits,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """Retorna o usuário autenticado a partir do token."""
    return current_user


