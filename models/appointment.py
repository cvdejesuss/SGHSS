# models/appointment.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    professional_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)  # UTC-naive aqui; trate como UTC no app
    status = Column(String(20), nullable=False, default="SCHEDULED", index=True)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    patient = relationship("Patient", back_populates="appointments")
    professional = relationship("User", backref="appointments")

    __table_args__ = (
        CheckConstraint("status in ('SCHEDULED','DONE','CANCELED','NOSHOW')", name="ck_appointment_status"),
        Index("ix_appointments_professional_date", "professional_id", "date"),
        Index("ix_appointments_patient_date", "patient_id", "date"),
    )

    def __repr__(self) -> str:
        return f"<Appointment id={self.id} patient={self.patient_id} at={self.date}>"



