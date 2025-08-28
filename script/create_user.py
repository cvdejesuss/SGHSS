# script/create_user.py

import os
import re
import sys
import argparse
import getpass
from typing import Final, Optional
from contextlib import redirect_stderr
from io import StringIO

# Garante que a raiz do projeto esteja no PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from core.config import settings
from database import SessionLocal
from models.user import User

# Papéis permitidos
VALID_ROLES: Final = {"admin", "medico", "atendente", "user"}


def _only_digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _hash_password_silently(plain: str) -> str:
    """
    Faz o hash da senha usando o mesmo pwd_context do app,
    suprimindo o aviso "(trapped) error reading bcrypt version"
    que algumas combinações passlib/bcrypt imprimem no stderr.
    """
    buf = StringIO()
    with redirect_stderr(buf):
        return settings.pwd_context.hash(plain)


def create_user(
    name: str,
    email: str,
    password: str,
    cpf: str,
    role: str = "atendente",
) -> Optional[int]:
    """
    Cria um usuário diretamente no banco (uso CLI).
    Requisitos do model User: name, email (único), password (hash), role, cpf (único).
    Retorna o ID criado ou None em caso de erro de validação.
    """
    name_clean = (name or "").strip()
    email_norm = _normalize_email(email)
    cpf_digits = _only_digits(cpf)
    role_norm = (role or "").strip().lower()

    # Validações simples
    if not name_clean:
        print("[ERRO] Nome é obrigatório.")
        return None
    if not email_norm or "@" not in email_norm:
        print("[ERRO] E-mail inválido.")
        return None
    if not password or len(password) < 4:
        print("[ERRO] Senha deve ter pelo menos 4 caracteres.")
        return None
    if role_norm not in VALID_ROLES:
        print(f"[ERRO] Cargo '{role}' inválido. Use: {', '.join(sorted(VALID_ROLES))}")
        return None
    if len(cpf_digits) != 11:
        print("[ERRO] CPF deve conter 11 dígitos (apenas números).")
        return None

    db: Session = SessionLocal()
    try:
        # Checagens de duplicidade (amigáveis)
        if db.query(User).filter(User.email == email_norm).first():
            print(f"[ERRO] E-mail '{email_norm}' já cadastrado.")
            return None
        if db.query(User).filter(User.cpf == cpf_digits).first():
            print(f"[ERRO] CPF '{cpf_digits}' já cadastrado.")
            return None

        user = User(
            name=name_clean,
            email=email_norm,
            password=_hash_password_silently(password),
            role=role_norm,
            cpf=cpf_digits,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[OK] Usuário criado! ID: {user.id} | {user.name} | {user.email} | role={user.role}")
        return user.id

    except IntegrityError as e:
        db.rollback()
        # Plano B: se bateu unique no commit
        msg = str(e.orig).lower()
        if "users.email" in msg or "email" in msg:
            print(f"[ERRO] Conflito de e-mail: '{email_norm}' já existe.")
        elif "users.cpf" in msg or "cpf" in msg:
            print(f"[ERRO] Conflito de CPF: '{cpf_digits}' já existe.")
        else:
            print(f"[ERRO] Falha ao criar usuário (IntegrityError): {e}")
        return None
    except Exception as e:
        db.rollback()
        print(f"[ERRO] Falha inesperada: {e}")
        return None
    finally:
        db.close()


def _interactive_create() -> None:
    print("== Criar usuário SGHSS ==")
    nome = input("Nome: ").strip()
    email = input("Email: ").strip()
    # Esconde a senha ao digitar
    senha = getpass.getpass("Senha: ").strip()
    cpf = input("CPF (somente números ou com máscara): ").strip()
    role = input("Cargo (admin, medico, atendente, user) [atendente]: ").strip() or "atendente"
    create_user(nome, email, senha, cpf, role)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Criar usuário no SGHSS (CLI).")
    parser.add_argument("--name", help="Nome completo")
    parser.add_argument("--email", help="E-mail (único)")
    parser.add_argument("--password", help="Senha (mín. 4 chars)")
    parser.add_argument("--cpf", help="CPF (11 dígitos; pode vir com máscara)")
    parser.add_argument("--role", choices=sorted(VALID_ROLES), default="atendente", help="Papel do usuário")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    if args.name and args.email and args.password and args.cpf:
        # Modo não interativo (útil para script/CI)
        ok = create_user(args.name, args.email, args.password, args.cpf, args.role)
        sys.exit(0 if ok else 1)
    else:
        # Modo interativo (pergunta no terminal)
        _interactive_create()


