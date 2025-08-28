# models/record.py
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    professional_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True)
    notes = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    patient = relationship("Patient", back_populates="records")
    professional = relationship("User", backref="records")

    def __repr__(self) -> str:
        return f"<Record id={self.id} patient={self.patient_id}>"


