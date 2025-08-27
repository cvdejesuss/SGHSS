# routers/appointment_router.py

from datetime import datetime
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import get_db
from auth.auth_utils import get_current_user
from models.user import User
from models.patient import Patient
from models.appointment import Appointment
from schemas.appointment import AppointmentCreate, AppointmentOut

router = APIRouter(prefix="/appointments", tags=["Appointments"])

# ---------------------------
# Schemas (complementares)
# ---------------------------

AllowedStatus = Literal["SCHEDULED", "CONFIRMED", "CANCELLED", "COMPLETED", "NO_SHOW"]


class AppointmentUpdate(BaseModel):
    """Atualização parcial."""
    patient_id: Optional[int] = None
    date: Optional[datetime] = None
    status: Optional[AllowedStatus] = None
    reason: Optional[str] = None


class StatusChange(BaseModel):
    """Payload simples para mudar status."""
    status: AllowedStatus


# ---------------------------
# Helpers de permissão
# ---------------------------

def _can_manage(appt: Appointment, current_user: User) -> bool:
    """Regra simples:
       - admin pode tudo
       - o profissional 'owner' da consulta pode editar/deletar
    """
    if current_user.role == "admin":
        return True
    return appt.professional_id == current_user.id


# ---------------------------
# CREATE
# ---------------------------

@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(
        data: AppointmentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    # valida paciente
    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    appt = Appointment(
        patient_id=data.patient_id,
        professional_id=current_user.id,  # profissional autenticado
        date=data.date if isinstance(data.date, datetime) else datetime.fromisoformat(str(data.date)),
        status="SCHEDULED",
        reason=getattr(data, "reason", None),
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


# ---------------------------
# READ (listagem com filtros)
# ---------------------------

@router.get("/", response_model=list[AppointmentOut])
def list_appointments(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        # filtros
        patient_id: Optional[int] = None,
        professional_id: Optional[int] = None,
        status_filter: Optional[AllowedStatus] = Query(None, alias="status"),
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        # paginação/ordenação
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        sort: Literal["date_asc", "date_desc", "created_desc", "created_asc"] = "date_asc",
):
    q = db.query(Appointment)

    if patient_id is not None:
        q = q.filter(Appointment.patient_id == patient_id)

    # Por padrão, se não for admin, lista só as próprias
    if current_user.role != "admin":
        q = q.filter(Appointment.professional_id == current_user.id)
    elif professional_id is not None:
        q = q.filter(Appointment.professional_id == professional_id)

    if status_filter is not None:
        q = q.filter(Appointment.status == status_filter)

    if date_from is not None:
        q = q.filter(Appointment.date >= date_from)
    if date_to is not None:
        q = q.filter(Appointment.date <= date_to)

    if sort == "date_asc":
        q = q.order_by(Appointment.date.asc())
    elif sort == "date_desc":
        q = q.order_by(Appointment.date.desc())
    elif sort == "created_desc":
        q = q.order_by(Appointment.created_at.desc())
    else:
        q = q.order_by(Appointment.created_at.asc())

    return q.offset(offset).limit(limit).all()


# ---------------------------
# READ (detalhe)
# ---------------------------

@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(
        appointment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    if not _can_manage(appt, current_user):
        raise HTTPException(status_code=403, detail="Sem permissão")

    return appt


# ---------------------------
# UPDATE (parcial)
# ---------------------------

@router.patch("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
        appointment_id: int,
        payload: AppointmentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    if not _can_manage(appt, current_user):
        raise HTTPException(status_code=403, detail="Sem permissão")

    # atualizar paciente (se enviado)
    if payload.patient_id is not None:
        patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        appt.patient_id = payload.patient_id

    if payload.date is not None:
        appt.date = payload.date

    if payload.reason is not None:
        appt.reason = payload.reason

    if payload.status is not None:
        appt.status = payload.status

    db.commit()
    db.refresh(appt)
    return appt


# ---------------------------
# STATUS endpoints (atalhos)
# ---------------------------

@router.post("/{appointment_id}/status", response_model=AppointmentOut)
def change_status(
        appointment_id: int,
        body: StatusChange,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    if not _can_manage(appt, current_user):
        raise HTTPException(status_code=403, detail="Sem permissão")

    appt.status = body.status
    db.commit()
    db.refresh(appt)
    return appt


# atalhos sem corpo:
@router.post("/{appointment_id}/confirm", response_model=AppointmentOut)
def confirm(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    if not _can_manage(appt, current_user):
        raise HTTPException(status_code=403, detail="Sem permissão")
    appt.status = "CONFIRMED"
    db.commit();
    db.refresh(appt)
    return appt


@router.post("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    if not _can_manage(appt, current_user):
        raise HTTPException(status_code=403, detail="Sem permissão")
    appt.status = "CANCELLED"
    db.commit();
    db.refresh(appt)
    return appt


@router.post("/{appointment_id}/complete", response_model=AppointmentOut)
def complete(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    if not _can_manage(appt, current_user):
        raise HTTPException(status_code=403, detail="Sem permissão")
    appt.status = "COMPLETED"
    db.commit();
    db.refresh(appt)
    return appt


# ---------------------------
# DELETE
# ---------------------------

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
        appointment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    if not _can_manage(appt, current_user):
        raise HTTPException(status_code=403, detail="Sem permissão")

    db.delete(appt)
    db.commit()
    return None
