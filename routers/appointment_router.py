from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import AppointmentCreate, AppointmentOut
from models.appointment import Appointment
from models.patient import Patient
from datetime import datetime
from auth.auth_utils import get_current_user
from models.user import User

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentOut)
def create_appointment(data: AppointmentCreate,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    appt = Appointment(
        patient_id=data.patient_id,
        professional_id=current_user.id,
        date=data.date if isinstance(data.date, datetime) else datetime.fromisoformat(str(data.date)),
        status="SCHEDULED",
        reason=getattr(data, "reason", None)
    )
    db.add(appt);
    db.commit();
    db.refresh(appt)
    return appt
