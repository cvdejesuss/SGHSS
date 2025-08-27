# models/item.py

from sqlalchemy import Column, Integer, String
from database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    category = Column(String, nullable=True)
    unit = Column(String, nullable=False, default="un")  # un, ml, cx, pct...
    min_stock = Column(Integer, nullable=False, default=0)
