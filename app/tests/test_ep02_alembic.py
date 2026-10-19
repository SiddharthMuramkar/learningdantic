"""Episode 02: the migration builds the schema, undoes it, and builds it again."""

from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

from app.db import engine
from app.models import Base

TABLES = {"orders", "tickets", "audit_log", "refunds"}


@pytest.fixture
def scratch():
    """An empty throwaway database, so the real acme_test is left alone."""
    name = (
        engine.url.database.removesuffix("_test") + "_scratch"
    )  # one per checkout, like the test db
    admin = create_engine(engine.url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {name} WITH (FORCE)"))
        conn.execute(text(f"CREATE DATABASE {name}"))
    scratch = create_engine(engine.url.set(database=name))
    yield scratch
    scratch.dispose()
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE {name} WITH (FORCE)"))
    admin.dispose()


def migrate(database, action, revision):
    config = Config(Path(__file__).parents[2] / "alembic.ini")
    with database.begin() as connection:
        config.attributes["connection"] = connection  # tell migrations/env.py which database
        action(config, revision)


def tables(database):
    return set(inspect(database).get_table_names()) - {"alembic_version"}


def test_upgrade_downgrade_upgrade(scratch):
    migrate(scratch, command.upgrade, "head")
    assert tables(scratch) == TABLES
    migrate(scratch, command.downgrade, "base")
    assert tables(scratch) == set()
    migrate(scratch, command.upgrade, "head")
    assert tables(scratch) == TABLES


def test_migration_and_models_agree(scratch):
    migrate(scratch, command.upgrade, "head")
    with scratch.connect() as connection:
        changes = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    assert changes == []
