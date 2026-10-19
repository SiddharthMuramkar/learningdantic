"""Test setup shared by every spec. Needs Postgres: `docker compose up -d --wait`."""

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

# Sessions sharing one Postgres can each set ACME_TEST_DB (say acme_03_test) so they don't clash.
TEST_DB = os.getenv("ACME_TEST_DB", "acme_test")
assert TEST_DB.isidentifier() and TEST_DB.endswith("_test"), (
    "ACME_TEST_DB: letters, digits, _; end in _test"
)

# These lines must run before `app` is imported: importing it reads MODEL and DATABASE_URL.
os.environ["MODEL"] = "test"
dev_url = make_url(os.getenv("DATABASE_URL", "postgresql+psycopg://acme:acme@localhost:5432/acme"))
os.environ["DATABASE_URL"] = dev_url.set(database=TEST_DB).render_as_string(hide_password=False)

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from pydantic_ai import models  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

models.ALLOW_MODEL_REQUESTS = False  # any real model call fails the test

from app.db import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402
from app.seed import seed  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def database():
    """Once per run: a fresh test database, built by the real migrations."""
    admin = create_engine(dev_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB}"))
    admin.dispose()
    command.upgrade(Config(Path(__file__).parents[2] / "alembic.ini"), "head")


@pytest.fixture(autouse=True)
def clean_tables(database):
    """Before every test: empty every table, then put the demo orders back."""
    assert engine.url.database.endswith("_test"), (
        "refusing to wipe a database that is not a test one"
    )
    tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
    with Session(engine) as session:
        session.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
        seed(session)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def session():
    with Session(engine) as session:
        yield session
