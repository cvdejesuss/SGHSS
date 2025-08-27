# script/peek_metadata.py

import os, sys

# garante que a raiz do projeto (SGHSS) esteja no PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base

print("Tables registradas:", sorted(Base.metadata.tables.keys()))

