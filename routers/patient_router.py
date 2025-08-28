# routers/patient_router.py

from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.patient import Patient
from models.user import User
from auth.auth_utils import get_current_user
from schemas.patient import PatientCreate, PatientUpdate, PatientOut
from schemas.common import Page

router = APIRouter(prefix="/patients", tags=["Patients"])


# ---------- CREATE ----------
@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientOut:
    if payload.cpf:
        exists = db.query(Patient).filter(Patient.cpf == payload.cpf).first()
        if exists:
            raise HTTPException(status_code=409, detail="CPF já cadastrado para outro paciente.")

    patient = Patient(
        name=payload.name.strip(),
        cpf=(payload.cpf.strip() if payload.cpf else None),
        birth_date=payload.birth_date,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


# ---------- LIST (paginação + filtros) ----------
@router.get("/", response_model=Page[PatientOut])
def list_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: Optional[str] = Query(None, description="Busca por nome ou CPF (contém)"),
    birth_from: Optional[str] = None,  # ISO date (YYYY-MM-DD)
    birth_to: Optional[str] = None,    # ISO date
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    order: Literal["name_asc", "name_desc", "id_desc", "id_asc"] = "name_asc",
) -> Page[PatientOut]:
    query = db.query(Patient)

    if q:
        q_like = f"%{q.strip()}%"
        query = query.filter(
            (Patient.name.ilike(q_like)) | (func.replace(func.coalesce(Patient.cpf, ""), ".", "").ilike(q_like))
        )

    if birth_from:
        query = query.filter(Patient.birth_date >= birth_from)
    if birth_to:
        query = query.filter(Patient.birth_date <= birth_to)

    total = query.count()

    if order == "name_asc":
        query = query.order_by(Patient.name.asc())
    elif order == "name_desc":
        query = query.order_by(Patient.name.desc())
    elif order == "id_desc":
        query = query.order_by(Patient.id.desc())
    else:
        query = query.order_by(Patient.id.asc())

    items = query.offset((page - 1) * size).limit(size).all()
    return Page[PatientOut](items=items, page=page, size=size, total=total)


# ---------- READ (detalhe) ----------
@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientOut:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return

