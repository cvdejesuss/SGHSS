from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.record import MedicalRecord
from models.patient import Patient
from schemas import RecordCreate, RecordOut
from datetime import datetime, timezone
from auth.jwt_bearer import get_current_user

router = APIRouter(
    prefix="/patients",
    tags=["Records"]
)

@router.post("/{patient_id}/records", response_model=RecordOut)
def create_record(
    patient_id: int,
    record: RecordCreate,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user)  # 👈 Aqui protegemos a rota
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    db_record = MedicalRecord(
        patient_id=patient_id,
        notes=record.notes,
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/{patient_id}/records", response_model=list[RecordOut])
def get_records(
    patient_id: int,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user)
):
    records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).all()
    return records
