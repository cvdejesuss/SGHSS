# routers/auth_router.py

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from core.config import settings
from auth.jwt_handler import create_access_token
from auth.auth_utils import get_current_user  # retorna User a partir do token

router = APIRouter(prefix="/auth", tags=["Auth"])


# ======== SCHEMAS ========

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


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
        from_attributes = True  # pydantic v2


# ======== HELPERS ========

def _verify_password(plain: str, hashed: str) -> bool:
    try:
        return settings.pwd_context.verify(plain, hashed)
    except Exception:
        return False


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


# ======== ROUTES ========

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Autentica por e-mail/senha (JSON) e retorna um JWT.
    Token inclui claims úteis: uid, role.
    """
    email = _normalize_email(data.email)
    user = db.query(User).filter(User.email == email).first()

    if not user or not _verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    token = create_access_token(
        sub=user.email,
        extra={"uid": user.id, "role": user.role},
    )

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        role=user.role,
    )


@router.post("/token", response_model=TokenResponse)
def token(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)) -> TokenResponse:
    """
    Fluxo OAuth2 Password (usado pelo cadeado do Swagger).
    Recebe username/password como form-data e retorna JWT.
    """
    email = _normalize_email(form.username)
    user = db.query(User).filter(User.email == email).first()

    if not user or not _verify_password(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    token = create_access_token(
        sub=user.email,
        extra={"uid": user.id, "role": user.role},
    )

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        role=user.role,
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """Retorna o usuário autenticado a partir do token de acesso."""
    return current_user



