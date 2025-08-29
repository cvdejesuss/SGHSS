# routers/user_admin_router.py
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status, Form
from sqlalchemy.orm import Session
from pydantic import EmailStr

from database import get_db
from models.user import User
from core.config import settings
from auth.auth_utils import require_role
from schemas.user_admin import (
    UserAdminCreate,
    UserAdminUpdate,
    UserAdminOut,
    RoleLiteral,  # admin | doctor | nurse | technician
)

router = APIRouter(
    prefix="/users",
    tags=["Users (Admin)"],
)

# ---------------------------
# Helpers
# ---------------------------

def _only_digits(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    return "".join(ch for ch in s if ch.isdigit())

def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()

def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

def _count_admins(db: Session) -> int:
    return db.query(User).filter(User.role == "admin").count()

# ---------------------------
# LISTA DE PAPÉIS
# ---------------------------

@router.get("/roles", response_model=list[RoleLiteral])
def list_roles(
    _current_admin: User = Depends(require_role(["admin"])),
):
    # Slugs oficiais (para SELECT no front / Swagger)
    return ["admin", "doctor", "nurse", "technician"]

@router.get("/roles/meta")
def list_roles_meta(
    _current_admin: User = Depends(require_role(["admin"])),
):
    # Labels para UI em PT-BR (exibe com "(a)")
    return [
        {"slug": "admin",       "label_pt": "Administrador(a)"},
        {"slug": "doctor",      "label_pt": "Médico(a)"},
        {"slug": "nurse",       "label_pt": "Enfermeiro(a)"},
        {"slug": "technician",  "label_pt": "Técnico(a)"},
    ]

# ---------------------------
# LIST
# ---------------------------

@router.get("", response_model=list[UserAdminOut])
def list_users(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(require_role(["admin"])),
    role: Optional[RoleLiteral] = Query(None),
    email_like: Optional[str] = Query(None),
    name_like: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort: Literal["id_asc", "id_desc", "name_asc", "name_desc"] = "id_asc",
):
    q = db.query(User)

    if role:
        q = q.filter(User.role == role)

    if email_like:
        like = f"%{email_like.strip().lower()}%"
        q = q.filter(User.email.like(like))

    if name_like:
        like = f"%{name_like.strip()}%"
        q = q.filter(User.name.like(like))

    if sort == "id_desc":
        q = q.order_by(User.id.desc())
    elif sort == "name_asc":
        q = q.order_by(User.name.asc())
    elif sort == "name_desc":
        q = q.order_by(User.name.desc())
    else:
        q = q.order_by(User.id.asc())

    return q.offset(offset).limit(limit).all()

# ---------------------------
# RETRIEVE
# ---------------------------

@router.get("/{user_id}", response_model=UserAdminOut)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(require_role(["admin"])),
):
    return _get_user_or_404(db, user_id)

# ---------------------------
# CREATE (JSON)
# ---------------------------

@router.post("", response_model=UserAdminOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserAdminCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(require_role(["admin"])),
):
    email = _normalize_email(payload.email)
    cpf_digits = _only_digits(payload.cpf) or ""

    if len(cpf_digits) != 11:
        raise HTTPException(status_code=400, detail="CPF deve conter 11 dígitos (apenas números).")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
    if db.query(User).filter(User.cpf == cpf_digits).first():
        raise HTTPException(status_code=409, detail="CPF já cadastrado.")

    user = User(
        name=payload.name.strip(),
        email=email,
        password=settings.pwd_context.hash(payload.password),
        role=payload.role,  # admin | doctor | nurse | technician
        cpf=cpf_digits,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ---------------------------
# CREATE (FORM) – Dropdown de role no Swagger
# ---------------------------

@router.post("/form", response_model=UserAdminOut, status_code=status.HTTP_201_CREATED)
def create_user_form(
    name: str = Form(..., min_length=2),
    email: EmailStr = Form(...),
    password: str = Form(..., min_length=4),
    role: RoleLiteral = Form(..., description="Selecione o papel"),
    cpf: str = Form(..., min_length=11, max_length=14, description="Pode vir com máscara"),
    db: Session = Depends(get_db),
    _current_admin: User = Depends(require_role(["admin"])),
):
    email_norm = _normalize_email(str(email))
    cpf_digits = _only_digits(cpf) or ""

    if len(cpf_digits) != 11:
        raise HTTPException(status_code=400, detail="CPF deve conter 11 dígitos (apenas números).")

    if db.query(User).filter(User.email == email_norm).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
    if db.query(User).filter(User.cpf == cpf_digits).first():
        raise HTTPException(status_code=409, detail="CPF já cadastrado.")

    user = User(
        name=name.strip(),
        email=email_norm,
        password=settings.pwd_context.hash(password),
        role=role,
        cpf=cpf_digits,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ---------------------------
# UPDATE (partial)
# ---------------------------

@router.patch("/{user_id}", response_model=UserAdminOut)
def update_user(
    user_id: int,
    payload: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(["admin"])),
):
    user = _get_user_or_404(db, user_id)

    if payload.email is not None:
        new_email = _normalize_email(payload.email)
        if new_email != user.email:
            if db.query(User).filter(User.email == new_email).first():
                raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
            user.email = new_email

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Nome não pode ser vazio.")
        user.name = name

    if payload.cpf is not None:
        cpf_digits = _only_digits(payload.cpf) or ""
        if len(cpf_digits) != 11:
            raise HTTPException(status_code=400, detail="CPF deve conter 11 dígitos (apenas números).")
        if cpf_digits != (user.cpf or ""):
            if db.query(User).filter(User.cpf == cpf_digits).first():
                raise HTTPException(status_code=409, detail="CPF já cadastrado.")
            user.cpf = cpf_digits

    if payload.role is not None:
        new_role = payload.role
        if user.role == "admin" and new_role != "admin":
            admins = _count_admins(db)
            if admins <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="Não é possível remover o último admin do sistema.",
                )
            if user.id == current_admin.id:
                raise HTTPException(
                    status_code=400,
                    detail="Você não pode remover seu próprio papel de admin.",
                )
        user.role = new_role

    if payload.password is not None:
        if len(payload.password) < 4:
            raise HTTPException(status_code=400, detail="Senha deve ter pelo menos 4 caracteres.")
        user.password = settings.pwd_context.hash(payload.password)

    db.commit()
    db.refresh(user)
    return user

# ---------------------------
# DELETE
# ---------------------------

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(["admin"])),
):
    user = _get_user_or_404(db, user_id)

    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Você não pode deletar o próprio usuário.")

    if user.role == "admin":
        admins = _count_admins(db)
        if admins <= 1:
            raise HTTPException(status_code=400, detail="Não é possível deletar o último admin do sistema.")

    db.delete(user)
    db.commit()
    return None



