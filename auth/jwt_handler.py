# auth/jwt_handler.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(sub: str, extra: dict | None = None):
    to_encode = {"sub": sub, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    if extra:
        to_encode.update(extra)  # ex: {"role": "medico", "uid": 1}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

