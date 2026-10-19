"""A ticket's conversation, saved in Postgres. Stub: spec 04 fills this in (episode 04)."""

from pydantic_ai import Conversation


class VersionConflict(Exception):
    """Someone else saved this ticket's conversation first."""


def load(ticket_id: int) -> tuple[Conversation | None, int]:
    """Return (conversation, version)."""
    raise NotImplementedError("spec 04")


def save(ticket_id: int, conversation: Conversation, version: int) -> None:
    """UPDATE ... WHERE version=:v. Zero rows changed means VersionConflict."""
    raise NotImplementedError("spec 04")
