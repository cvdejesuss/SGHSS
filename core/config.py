from pathlib import Path
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent  # pasta SGHSS
DB_FILE = BASE_DIR / "db.sqlite3"
DATABASE_URL = f"sqlite:///{DB_FILE}"  # <- ABSOLUTO

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


