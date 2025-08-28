# auth/jwt_bearer.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .jwt_handler import verify_access_token

# Mantém o mesmo endpoint de login que você já expôs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Lê o Bearer token, valida/decodifica e retorna o payload.
    Erros levantam 401 com header 'WWW-Authenticate: Bearer'.
    """
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
