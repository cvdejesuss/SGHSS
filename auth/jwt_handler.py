# auth/jwt_handler.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from core.config import settings


def create_access_token(
    sub: str,
    extra: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Gera um JWT com:
      - sub: identificador do usuário (email)
      - iat: emitido em (epoch seconds)
      - exp: expiração (epoch seconds)
      - campos extras opcionais (ex.: {"uid": 1, "role": "medico"})
    """
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    payload: Dict[str, Any] = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra:
        payload.update(extra)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica e valida o JWT. Retorna o payload se válido; senão, None.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


