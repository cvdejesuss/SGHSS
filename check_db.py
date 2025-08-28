# check_db.py

from sqlalchemy import create_engine, text, inspect
from core.config import settings

def main() -> None:
    print("DATABASE_URL (settings):", settings.DATABASE_URL)

    # Engine isolada só para inspeção rápida
    engine = create_engine(settings.DATABASE_URL, future=True)

    with engine.begin() as conn:
        # Caminho real do banco aberto (SQLite)
        try:
            dbs = conn.execute(text("PRAGMA database_list;")).all()
            print("PRAGMA database_list ->", dbs)
        except Exception:
            # Em outros SGBDs, PRAGMA não existe
            pass

        insp = inspect(engine)
        tables = insp.get_table_names()
        print("Tables:", tables)

        if "appointments" in tables:
            try:
                cols = conn.execute(text("PRAGMA table_info(appointments)")).all()
                print("Appointments cols:", [c[1] for c in cols])
            except Exception:
                pass

if __name__ == "__main__":
    main()

