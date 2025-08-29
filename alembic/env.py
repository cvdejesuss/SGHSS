# alembic/env.py
"""
Ambiente Alembic configurado para ler a URL do banco a partir de core.config.settings.
- Suporta SQLite (com render_as_batch=True) e outros SGBDs.
- Carrega models para popular o Base.metadata e permitir autogenerate.
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Garante que o diretório raiz do projeto esteja no sys.path
# (pasta que contém 'core', 'database.py', etc.)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Importa settings e metadata
from core.config import settings  # noqa: E402
from database import Base          # noqa: E402
import models                      # noqa: F401,E402  - importante para registrar todos os models

# Interpret the config file for Python logging.
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# Define a URL centralmente a partir do settings
DATABASE_URL = settings.DATABASE_URL
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Alvo de metadados para autogenerate
target_metadata = Base.metadata


def is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def run_migrations_offline() -> None:
    """
    Executa migrações no modo 'offline'.
    Gera o scripts de SQL sem precisar de DB conectado.
    """
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=is_sqlite(url),  # essencial para ALTER TABLE no SQLite
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Executa migrações no modo 'online'.
    Abre conexão real no banco e aplica as mudanças.
    """
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=is_sqlite(DATABASE_URL),  # essencial para SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

