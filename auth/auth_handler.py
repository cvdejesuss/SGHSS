from datetime import datetime, timedelta
from jose import jwt
from decouple import config

SECRET_KEY = config("SECRET_KEY", default="meusegredo")
ALGORITHM = "HS256"


# Gera o token JWT
def sign_jwt(user_id: int, role: str):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}


# Decodifica e valida o token
def decode_jwt(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except:
        return None
