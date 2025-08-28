# models/item.py
from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False, unique=True, index=True)
    category = Column(String(80), nullable=True, index=True)
    unit = Column(String(8), nullable=False, default="un")  # un, ml, cx, pct...
    min_stock = Column(Integer, nullable=False, default=0)

    stock_movements = relationship("StockMovement", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Item id={self.id} name={self.name}>"

Index("ix_items_category_name", Item.category, Item.name)

