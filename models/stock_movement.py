# models/stock_movement.py
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True)
    type = Column(String(8), nullable=False)  # "IN" ou "OUT"
    quantity = Column(Integer, nullable=False)
    reason = Column(String(160), nullable=True)  # compra, consumo, perda...
    lot = Column(String(64), nullable=True)
    expiration_date = Column(Date, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    item = relationship("Item", back_populates="stock_movements")
    user = relationship("User", backref="stock_movements")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_stock_mov_quantity_positive"),
        CheckConstraint("type in ('IN','OUT')", name="ck_stock_mov_type"),
        Index("ix_stock_item_created_at", "item_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<StockMovement id={self.id} item={self.item_id} type={self.type} qty={self.quantity}>"
