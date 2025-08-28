# script/peek_metadata.py

import os
import sys

# garante que a raiz do projeto (SGHSS) esteja no PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base
import models  # importa para registrar todos os mapeamentos no Base.metadata

def main() -> None:
    print("Tables registradas:", sorted(Base.metadata.tables.keys()))

if __name__ == "__main__":
    main()


