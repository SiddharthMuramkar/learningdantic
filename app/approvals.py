"""Approvals: a refund waits in the database between two HTTP requests (episode 08)."""

from pydantic_ai import DeferredToolRequests
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db import engine
from app.models import Order, Refund
from app.schemas import ApprovalOut


def record_pending(ticket_id: int, requests: DeferredToolRequests) -> ApprovalOut | None:
    """Store one 'pending' refunds row per approval the model asked for; return the first."""
    first = None
    with Session(engine) as session, session.begin():
        for call in requests.approvals:
            # The amount comes from the orders row, never from the model's arguments.
            order = session.get(Order, call.args_as_dict()["order_id"])
            # shortcut: no card for an order that does not exist; a real desk should tell the staff
            if order is None:
                continue
            refund = session.scalar(
                select(Refund).where(
                    Refund.ticket_id == ticket_id, Refund.tool_call_id == call.tool_call_id
                )
            ) or Refund(
                ticket_id=ticket_id,
                order_id=order.id,
                amount_cents=order.amount_cents,
                tool_call_id=call.tool_call_id,
                status="pending",
            )
            session.add(refund)
            session.flush()  # gives a new row its id
            first = first or ApprovalOut(
                refund_id=refund.id, order_id=refund.order_id, amount_cents=refund.amount_cents
            )
    return first


def execute_refund(ticket_id: int, tool_call_id: str) -> str:
    """Move one refund from 'approved' to 'executed'. Fails loudly if it was not approved."""
    with Session(engine) as session, session.begin():
        row = session.execute(
            update(Refund)
            .where(
                Refund.ticket_id == ticket_id,
                Refund.tool_call_id == tool_call_id,
                Refund.status == "approved",
            )
            .values(status="executed")
            .returning(Refund.order_id, Refund.amount_cents)
        ).first()
    if row is None:
        raise RuntimeError(f"refund {tool_call_id} on ticket {ticket_id} is not approved")
    return f"Refunded {row.amount_cents / 100:.2f} for order {row.order_id}."
