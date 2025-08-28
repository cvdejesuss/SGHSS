# models/user.py
from sqlalchemy import Column, Integer, String, Index
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False, index=True)
    email = Column(String(160), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="user", index=True)
    cpf = Column(String(14), unique=True, index=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

# Índices compostos úteis (opcional):
Index("ix_users_email_role", User.email, User.role)
