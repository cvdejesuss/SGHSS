# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
from core.config import settings

# Ajustes para SQLite (necessário no ambiente local)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    echo=settings.SQLALCHEMY_ECHO,
    pool_pre_ping=settings.SQLALCHEMY_POOL_PRE_PING,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()

# 🔴 IMPORTANTE: registra as tabelas no Base.metadata
import models  # noqa: F401  # garante que os modelos sejam importados

def get_db() -> Generator[Session, None, None]:
    """
    Dependência de sessão para FastAPI (escopo por request).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()






