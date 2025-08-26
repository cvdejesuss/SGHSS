import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Config JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Config DB
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

