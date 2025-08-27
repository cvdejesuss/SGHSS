# scrpt/bootstrap_db.py
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base, engine
import models  # garante que TODOS os models sejam registrados no Base.metadata

print(">> Criando tabelas com Base.metadata.create_all() ...")
Base.metadata.create_all(bind=engine)
print(">> OK! Tabelas criadas.")


