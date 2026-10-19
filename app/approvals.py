"""Refunds that wait for a person. Stub: spec 07 fills this in (episode 08)."""

from pydantic_ai import DeferredToolRequests

from app.schemas import ApprovalOut


def record_pending(ticket_id: int, requests: DeferredToolRequests) -> ApprovalOut | None:
    """Store one pending refund per approval request. The stub stores nothing."""
    return None


def execute_refund(ticket_id: int, tool_call_id: str) -> str:
    """Guarded UPDATE from approved to executed."""
    raise NotImplementedError("spec 07")
