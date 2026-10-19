"""How Alembic reaches the database: the same engine the app uses, and the models as the target."""

from logging.config import fileConfig

from alembic import context

from app.db import engine
from app.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# `alembic revision --autogenerate` compares this with the real database.
target_metadata = Base.metadata


def run(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


# The tests pass their own connection (a scratch database) in config.attributes.
connection = config.attributes.get("connection")
if connection is not None:
    run(connection)
else:
    with engine.connect() as connection:
        run(connection)
