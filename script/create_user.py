# script/create_user.py

import os
import re
import sys
from typing import Final

# Garante que a raiz do projeto esteja no PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from core.config import settings
from database import SessionLocal
from models.user import User

# Papéis permitidos
VALID_ROLES: Final = {"admin", "medico", "atendente", "user"}

def _only_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def _hash_password(plain: str) -> str:
    return settings.pwd_context.hash(plain)

def create_user(name: str, email: str, password: str, cpf: str, role: str = "atendente") -> None:
    """
    Cria um usuário diretamente no banco (uso de linha de comando).
    Requisitos do model User: name, email (único), password (hash), role, cpf (único).
    """
    email_norm = (email or "").strip().lower()
    cpf_digits = _only_digits(cpf)
    role_norm = (role or "").strip().lower()

    if role_norm not in VALID_ROLES:
        print(f"[ERRO] Cargo '{role}' inválido. Use: {', '.join(sorted(VALID_ROLES))}")
        return

    if len(cpf_digits) != 11:
        print("[ERRO] CPF deve conter 11 dígitos.")
        return

    db: Session = SessionLocal()
    try:
        # Checa conflitos
        if db.query(User).filter(User.email == email_norm).first():
            print(f"[ERRO] E-mail '{email_norm}' já cadastrado.")
            return
        if db.query(User).filter(User.cpf == cpf_digits).first():
            print(f"[ERRO] CPF '{cpf_digits}' já cadastrado.")
            return

        user = User(
            name=name.strip(),
            email=email_norm,
            password=_hash_password(password),
            role=role_norm,
            cpf=cpf_digits,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[OK] Usuário criado! ID: {user.id} | {user.name} | {user.email} | role={user.role}")
    finally:
        db.close()

if __name__ == "__main__":
    print("== Criar usuário SGHSS ==")
    nome = input("Nome: ").strip()
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()
    cpf = input("CPF (somente números ou com máscara): ").strip()
    role = input("Cargo (admin, medico, atendente, user) [atendente]: ").strip() or "atendente"
    create_user(nome, email, senha, cpf, role)
