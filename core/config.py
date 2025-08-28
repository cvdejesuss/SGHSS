# core/config.py

from pathlib import Path
import os
import secrets
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

# Carrega variáveis do .env (se existir)
load_dotenv()

# Raiz do projeto (pasta que contém main.py)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # === APP ===
    APP_NAME: str = "SGHSS Backend"
    APP_ENV: str = "development"  # development | production | staging
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # === DATABASE ===
    # Em dev: SQLite. Em prod: defina DATABASE_URL no .env (ex.: postgres://user:pass@host:5432/db)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{(BASE_DIR / 'db.sqlite3')}")
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_POOL_PRE_PING: bool = True

    # === SECURITY (JWT) ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # === CORS (opcional – ajuste conforme seu front) ===
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Configuração do Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Instância única de configurações
settings = Settings()


class AppInfo(BaseModel):
    """
    Modelo usado em endpoints de info/health (ex.: response_model no /api/v1/info).
    """
    name: str = settings.APP_NAME
    env: str = settings.APP_ENV
    version: str = settings.APP_VERSION
    docs: str = "/docs"






