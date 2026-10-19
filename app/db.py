"""The database connection: one engine for the whole app, one Session per request."""

import os
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://acme:acme@localhost:5432/acme")
engine = create_engine(DATABASE_URL)


def get_session() -> Iterator[Session]:
    """FastAPI runs this per request: hand out a Session, close it when the request ends."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
