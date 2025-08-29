# routers/patient_router.py

from typing import Optional, Literal
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.patient import Patient
from models.user import User
from auth.auth_utils import get_current_user, require_role
from schemas.patient import PatientCreate, PatientUpdate, PatientOut

router = APIRouter(prefix="/patients", tags=["Patients"])


# ---------------------------
# Helpers
# ---------------------------

def _only_digits(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    return "".join(ch for ch in s if ch.isdigit())

def _get_or_404(db: Session, patient_id: int) -> Patient:
    obj = db.get(Patient, patient_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return obj


# ---------------------------
# CREATE
# ---------------------------

@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),  # qualquer autenticado pode criar
):
    cpf_digits = _only_digits(payload.cpf) if payload.cpf else None

    # unicidade de CPF, se informado
    if cpf_digits:
        exists = db.query(Patient).filter(Patient.cpf == cpf_digits).first()
        if exists:
            raise HTTPException(status_code=409, detail="CPF já cadastrado para outro paciente.")

    p = Patient(
        name=payload.name.strip(),
        cpf=cpf_digits,
        birth_date=payload.birth_date,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# ---------------------------
# LIST (com filtros e paginação)
# ---------------------------

@router.get("/", response_model=list[PatientOut])
def list_patients(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
    name_like: Optional[str] = Query(None, description="Filtro por nome (contém)"),
    cpf_like: Optional[str] = Query(None, min_length=3, description="Filtro por CPF (contém)"),
    birth_from: Optional[date] = Query(None, description="Data de nascimento inicial"),
    birth_to: Optional[date] = Query(None, description="Data de nascimento final"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort: Literal["id_asc", "id_desc", "name_asc", "name_desc", "birth_asc", "birth_desc"] = "id_asc",
):
    q = db.query(Patient)

    if name_like:
        like = f"%{name_like.strip()}%"
        q = q.filter(Patient.name.like(like))

    if cpf_like:
        like = f"%{_only_digits(cpf_like)}%"
        q = q.filter(Patient.cpf.like(like))

    if birth_from:
        q = q.filter(Patient.birth_date >= birth_from)
    if birth_to:
        q = q.filter(Patient.birth_date <= birth_to)

    if sort == "id_desc":
        q = q.order_by(Patient.id.desc())
    elif sort == "name_asc":
        q = q.order_by(Patient.name.asc())
    elif sort == "name_desc":
        q = q.order_by(Patient.name.desc())
    elif sort == "birth_asc":
        q = q.order_by(Patient.birth_date.asc().nulls_last())
    elif sort == "birth_desc":
        q = q.order_by(Patient.birth_date.desc().nulls_last())
    else:
        q = q.order_by(Patient.id.asc())

    return q.offset(offset).limit(limit).all()


# ---------------------------
# RETRIEVE
# ---------------------------

@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return _get_or_404(db, patient_id)


# ---------------------------
# UPDATE (parcial)
# ---------------------------

@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    p = _get_or_404(db, patient_id)

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Nome não pode ser vazio.")
        p.name = name

    if payload.cpf is not None:
        cpf_digits = _only_digits(payload.cpf) or None
        if cpf_digits:
            # checa unicidade se mudou
            if cpf_digits != (p.cpf or ""):
                exists = db.query(Patient).filter(Patient.cpf == cpf_digits).first()
                if exists:
                    raise HTTPException(status_code=409, detail="CPF já cadastrado para outro paciente.")
        p.cpf = cpf_digits

    if payload.birth_date is not None:
        p.birth_date = payload.birth_date

    db.commit()
    db.refresh(p)
    return p


# ---------------------------
# DELETE (admin-only)
# ---------------------------

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role(["admin","medico(a)","enfermeiro(a)"])),
):
    p = _get_or_404(db, patient_id)
    db.delete(p)
    db.commit()
    return None

