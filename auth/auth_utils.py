# auth/auth_utils.py

from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from core.config import settings
from .jwt_handler import verify_access_token

# Swagger: fluxo OAuth2 Password (form) — permite "Authorize" com username/password
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/token",
    auto_error=False,  # deixamos False para podermos cair no HTTPBearer se não vier token por aqui
)

# Swagger: esquema HTTP Bearer — permite "Authorize" colando apenas o token (Value)
bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_token(
    oauth2_token: Optional[str] = Depends(oauth2_scheme),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> str:
    """
    Aceita token via:
      - OAuth2PasswordBearer (após login no cadeado com username/password)
      - HTTPBearer (colando o JWT no cadeado)
    Dá preferência ao Bearer explícito; se não houver, usa o OAuth2.
    """
    if bearer and bearer.scheme.lower() == "bearer" and bearer.credentials:
        return bearer.credentials
    if oauth2_token:
        return oauth2_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais ausentes.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(_resolve_token), db: Session = Depends(get_db)) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exc

    email = payload.get("sub")
    if not email:
        raise credentials_exc

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exc

    return user


def require_role(required_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Você não tem permissão para acessar este recurso.")
        return current_user
    return role_checker


