# models/patient.py
from sqlalchemy import Column, Integer, String, Date, Index
from sqlalchemy.orm import relationship
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False, index=True)
    cpf = Column(String(14), unique=True, index=True, nullable=True)
    birth_date = Column(Date, nullable=True)

    # Relacionamentos inversos
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    records = relationship("Record", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Patient id={self.id} name={self.name}>"

# Índice auxiliar para buscas por nome:
Index("ix_patients_name", Patient.name)


