from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.record import Record
from models.patient import Patient
from schemas import RecordCreate, RecordOut
from datetime import datetime, timezone
from auth.auth_utils import require_role

router = APIRouter(
    prefix="/patients",
    tags=["Records"]
)


# Somente médicos podem criar prontuários
@router.post("/{patient_id}/records", response_model=RecordOut)
def create_record(
        patient_id: int,
        record: RecordCreate,
        db: Session = Depends(get_db),
        user=Depends(require_role(["medico"]))  # controle de acesso por função
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    db_record = Record(
        patient_id=patient_id,
        notes=record.notes,
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


# Aqui pode ficar acessível para qualquer usuário autenticado
@router.get("/{patient_id}/records", response_model=list[RecordOut])
def get_records(
        patient_id: int,
        db: Session = Depends(get_db),
        user=Depends(require_role(["medico", "admin"]))  # se desejar restringir também
):
    records = db.query(Record).filter(Record.patient_id == patient_id).all()
    return records
