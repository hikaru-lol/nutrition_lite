from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.infra.db.base import Base
from app.settings import settings

import app.infra.db.models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic の自動マイグレーションで見る metadata を指定
target_metadata = Base.metadata

# env や .ini から DB の URL を設定


def get_url() -> str:
    # settings.DATABASE_URL を使う
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """'オフライン'モードでマイグレーションを実行。"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # 型変更も検出したければ True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """'オンライン'モードでマイグレーションを実行。"""
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        raise RuntimeError("No configuration section in alembic.ini")

    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
