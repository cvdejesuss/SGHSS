# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 🔴 IMPORTANTE: registra as tabelas no Base.metadata
import models  # noqa: F401


# ✅ Dependência para FastAPI
from sqlalchemy.orm import Session
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





