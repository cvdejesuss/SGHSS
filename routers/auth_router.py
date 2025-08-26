# routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from core.config import pwd_context, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.jwt_handler import create_access_token
from auth.auth_utils import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


# ======== SCHEMAS ========
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=4)
    # Ajuste conforme seu domínio: "admin", "medico", "atendente", etc.
    role: str = Field(default="user")


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
        from_attributes = True


# ======== HELPERS ========
def _verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def _hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


# ======== ROUTES ========
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica um usuário por e-mail/senha e retorna um access token (JWT).
    O token contém:
      - sub = e-mail do usuário (chave padrão para identificação)
      - uid, role = metadados úteis para o front
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not _verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    token = create_access_token(
        sub=user.email,
        extra={"uid": user.id, "role": user.role}
    )

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        role=user.role,
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registra um novo usuário.
    OBS: por padrão está aberto. Se quiser, troque a dependência
    para exigir um admin: `current=Depends(require_role(["admin"]))`.
    """
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado"
        )

    user = User(
        name=data.name.strip(),
        email=str(data.email).lower(),
        password=_hash_password(data.password),
        role=data.role.strip().lower(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Retorna o usuário autenticado a partir do token de acesso."""
    return current_user
