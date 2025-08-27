# routers/auth_router.py

from datetime import timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from core.config import pwd_context, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.jwt_handler import create_access_token  # deve aceitar expires_delta=timedelta(...) (seu handler)
from auth.auth_utils import get_current_user  # retorna User a partir do token

router = APIRouter(prefix="/auth", tags=["Auth"])


# ======== SCHEMAS ========

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


# Ajuste as opções de role ao seu domínio:
RoleLiteral = Literal["admin", "medico", "atendente", "user"]

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=4)
    role: RoleLiteral = "user"   # evita valores inválidos por engano


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES
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
        return pwd_context.verify(plain, hashed)
    except Exception:
        # evita levantar erro de algoritmo ausente, etc.
        return False


def _hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


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
    O token inclui:
      - sub = e-mail do usuário
      - extra claims: uid, role (úteis no front)
    """
    email = str(data.email).strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user or not _verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    # expiração real com base na config
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token = create_access_token(
        sub=user.email,
        extra={"uid": user.id, "role": user.role},
        expires_delta=expires_delta,  # seu handler deve usar isso ao assinar
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
    Se quiser restringir a admins:
        current = Depends(require_role(["admin"]))
    e adicione como parâmetro da função.
    """
    name = data.name.strip()
    email = str(data.email).strip().lower()
    role = str(data.role).strip().lower()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado"
        )

    user = User(
        name=name,
        email=email,
        password=_hash_password(data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """Retorna o usuário autenticado a partir do token de acesso."""
    return current_user

