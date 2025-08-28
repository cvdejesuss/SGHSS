# auth/auth_utils.py

from typing import Iterable
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from .jwt_bearer import get_token_payload  # <= reutiliza a validação do token

def get_current_user(
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db),
) -> User:
    """
    Obtém o usuário autenticado a partir do payload do JWT.
    Espera 'sub' = email no payload (padrão comum).
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = payload.get("sub")
    if not email:
        raise credentials_exc

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exc

    # Se seu modelo tiver 'is_active' (ou similar), vale a pena checar:
    if hasattr(user, "is_active") and getattr(user, "is_active") is False:
        raise HTTPException(status_code=403, detail="Usuário inativo")

    return user


def require_role(required_roles: Iterable[str]):
    """
    Dependência para proteger rotas por papel.
    Uso:
      @router.get("/...", dependencies=[Depends(require_role({"admin","gestor"}))])
    """
    required_set = set(required_roles)

    def checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = getattr(current_user, "role", None)
        if user_role not in required_set:
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para acessar este recurso.",
            )
        return current_user

    return checker

