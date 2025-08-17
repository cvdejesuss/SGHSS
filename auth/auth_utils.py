from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.user import User
from sqlalchemy.orm import Session
from database import get_db
from passlib.context import CryptContext


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = "qH7vL9gXTr1eW3fPzM0yVcB2NaK8JdRu"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def encrypt_admin_password(db: Session):
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if user and not user.password.startswith("$2b$"):
        user.password = pwd_context.hash("admin123")
        db.commit()
        print("Senha criptografada com sucesso.")
    else:
        print("Usuário não encontrado ou senha já está criptografada.")

