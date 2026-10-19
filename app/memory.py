"""A ticket's conversation, saved in Postgres (tickets.conversation), guarded by tickets.version."""

import logfire
from pydantic_ai import Conversation, ConversationTypeAdapter
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db import engine
from app.models import Ticket

# ep06: every SQL statement becomes a span. skip_dep_check: OpenTelemetry's SQLAlchemy
# instrumentor lists support for < 2.1 only, and refuses to start on 2.1 without it.
logfire.instrument_sqlalchemy(engine=engine, skip_dep_check=True)


class VersionConflict(Exception):
    """Someone else saved this ticket's conversation first."""


def load(ticket_id: int) -> tuple[Conversation | None, int]:
    """Return (conversation, version). A new ticket has (None, 0)."""
    with Session(engine) as session:
        row = session.execute(
            select(Ticket.conversation, Ticket.version).where(Ticket.id == ticket_id)
        ).one()
    stored, version = row
    return (ConversationTypeAdapter.validate_python(stored) if stored else None), version


def save(ticket_id: int, conversation: Conversation, version: int) -> None:
    """Store the whole conversation. Zero rows changed means VersionConflict."""
    stored = ConversationTypeAdapter.dump_python(conversation, mode="json")
    with Session(engine) as session, session.begin():
        changed = session.execute(
            update(Ticket)
            .where(Ticket.id == ticket_id, Ticket.version == version)
            .values(conversation=stored, version=version + 1)
        ).rowcount
    if changed == 0:
        raise VersionConflict(f"ticket {ticket_id} is no longer at version {version}")
