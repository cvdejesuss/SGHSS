# core/config.py
from pathlib import Path
import os
import secrets
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()


class Settings(BaseSettings):
    # === APP ===
    APP_NAME: str = "SGHSS Backend"
    APP_ENV: str = "development"  # development | production
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # === DATABASE ===
    DATABASE_URL: str = f"sqlite:///{(BASE_DIR / 'db.sqlite3')}"

    # === SECURITY ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()





