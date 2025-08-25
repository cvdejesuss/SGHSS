from passlib.context import CryptContext
from models.user import User
from database import get_db

# Funções permitidas no hospital
VALID_ROLES = ["admin", "medico", "atendente"]

# Contexto de senha com bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(email: str, password: str, role: str = "atendente"):
    db = next(get_db())

    # Verifica se já existe
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"Usuário '{email}' já existe.")
        return

    # Verifica se o cargo é válido
    if role not in VALID_ROLES:
        print(f"Cargo '{role}' inválido. Use: {', '.join(VALID_ROLES)}")
        return

    # Criptografa a senha
    hashed_password = pwd_context.hash(password)

    # Cria o usuário
    user = User(email=email, password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"Usuário '{email}' criado com sucesso! ID: {user.id} | Cargo: {user.role}")


# Execução direta via terminal
if __name__ == "__main__":
    email = input("Email: ").strip()
    password = input("Senha: ").strip()
    role = input("Cargo (admin, medico, atendente): ").strip() or "atendente"
    create_user(email, password, role)
