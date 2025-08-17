from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user import User
from database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(email: str, password: str, role: str = "user"):
    db = next(get_db())

    # Verifica se já existe
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"Usuário '{email}' já existe.")
        return

    # Criptografa a senha
    hashed_password = pwd_context.hash(password)

    # Cria o usuário
    user = User(email=email, password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"Usuário '{email}' criado com sucesso (id={user.id}).")

if __name__ == "__main__":
    email = input("Email: ")
    password = input("Senha: ")
    role = input("Cargo (ex: admin, medico): ").strip() or "user"
    create_user(email, password, role)
