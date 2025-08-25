from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.auth_bearer import JWTBearer
from auth.auth_handler import decode_jwt
from database import get_db
from schemas import AppointmentCreate, AppointmentOut
from models.appointment import Appointment
from models.patient import Patient

from datetime import datetime

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentOut, dependencies=[Depends(JWTBearer())])
def create_appointment(data: AppointmentCreate, token_data: dict = Depends(JWTBearer()), db: Session = Depends(get_db)):
    # Verifica se paciente existe
    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # Cria consulta vinculada ao usuário autenticado (profissional)
    appointment = Appointment(
        patient_id=data.patient_id,
        professional_id=token_data["user_id"],
        date=datetime.fromisoformat(data.date),
        status="SCHEDULED"
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
