# scrpt/bootstrap_db.py

import os
import sys

# Garante que a raiz do projeto (pasta que contém main.py) esteja no PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base, engine  # usa DATABASE_URL de core.config.settings via database.py
import models  # garante que TODOS os models sejam registrados no Base.metadata

def main() -> None:
    print(">> Criando tabelas com Base.metadata.create_all() ...")
    Base.metadata.create_all(bind=engine)
    print(">> OK! Tabelas criadas.")

if __name__ == "__main__":
    main()



