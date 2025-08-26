from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    professional_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    status = Column(String, default="SCHEDULED")
    reason = Column(String, nullable=True)  # <-- NEW
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient")
    professional = relationship("User")

