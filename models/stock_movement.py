# models/stock_movement.py

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    type = Column(String, nullable=False)  # "IN" ou "OUT"
    quantity = Column(Integer, nullable=False)
    reason = Column(String, nullable=True)  # compra, consumo, perda...
    lot = Column(String, nullable=True)
    expiration_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    item = relationship("Item")
    user = relationship("User")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_stock_mov_quantity_positive"),
        CheckConstraint("type in ('IN','OUT')", name="ck_stock_mov_type"),
    )
