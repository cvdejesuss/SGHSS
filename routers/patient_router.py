from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import patient as models
from schemas import PatientCreate, PatientOut
from database import get_db

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/", response_model=list[PatientOut])
def get_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()

@router.post("/", response_model=PatientOut)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = models.Patient(name=patient.name, age=patient.age)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient
@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    db.delete(patient)
    db.commit()
    return