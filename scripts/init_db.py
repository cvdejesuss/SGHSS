#init_db.py

from database import Base, engine
import models.patient

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

print("Banco de dados criado com sucesso.")
