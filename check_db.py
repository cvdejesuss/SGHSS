# check_db.py
from sqlalchemy import create_engine, text, inspect
from core.config import DATABASE_URL

print("DATABASE_URL (Python):", DATABASE_URL)

engine = create_engine(DATABASE_URL, future=True)

with engine.begin() as conn:
    # Caminho real do banco aberto
    dbs = conn.execute(text("PRAGMA database_list;")).all()
    print("PRAGMA database_list ->", dbs)

    insp = inspect(engine)
    tables = insp.get_table_names()
    print("Tables:", tables)

    if "appointments" in tables:
        cols = conn.execute(text("PRAGMA table_info(appointments)")).all()
        print("Appointments cols:", [c[1] for c in cols])
