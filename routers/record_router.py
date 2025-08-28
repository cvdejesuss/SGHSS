# routers/record_router.py

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.record import Record
from models.patient import Patient
from models.user import User
from schemas.record import RecordCreate, RecordUpdate, RecordOut
from schemas.common import Page
from auth.auth_utils import require_role, get_current_user

router = APIRouter(prefix="/patients", tags=["Records"])


# Somente médicos podem criar prontuários
@router.post("/{patient_id}/records", response_model=RecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    patient_id: int,
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["medico"])),
):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    record = Record(
        patient_id=patient_id,
        professional_id=current_user.id,   # <-- profissional autenticado
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# Lista (paginada). Acesso restrito a médicos e admins (ajuste se quiser).
@router.get("/{patient_id}/records", response_model=Page[RecordOut])
def list_records(
    patient_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(["medico", "admin"])),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
) -> Page[RecordOut]:
    if not db.get(Patient, patient_id):
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    q = db.query(Record).filter(Record.patient_id == patient_id).order_by(Record.id.desc())
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return Page[RecordOut](items=items, page=page, size=size, total=total)


# (Opcional) Update de notas do prontuário
@router.patch("/{patient_id}/records/{record_id}", response_model=RecordOut)
def update_record(
    patient_id: int,
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["medico"])),
):
    rec = db.get(Record, record_id)
    if not rec or rec.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    # Regra simples: médico autor (owner) ou admin pode editar
    if current_user.role != "admin" and rec.professional_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para editar este registro")

    data = payload.model_dump(exclude_unset=True)
    if "notes" in data and data["notes"]:
        rec.notes = data["notes"]

    db.commit()
    db.refresh(rec)
    return rec


