"""The chat route: one message in, the desk's reply (or a refund waiting for a person) out."""

from fastapi import APIRouter, HTTPException
from pydantic_ai import DeferredToolRequests
from sqlalchemy.orm import Session

from app import approvals
from app.agents import run_desk
from app.db import engine
from app.identity import UserDep
from app.memory import VersionConflict
from app.models import Ticket
from app.schemas import MessageIn, ReplyOut

router = APIRouter()


@router.post("/tickets/{ticket_id}/messages")
async def post_message(ticket_id: int, body: MessageIn, user: UserDep) -> ReplyOut:
    # Its own short Session, closed before the await below (SessionDep would stay open across it).
    with Session(engine) as session:
        ticket = session.get(Ticket, ticket_id)
    if ticket is None or (user.role != "staff" and ticket.customer != user.name):
        raise HTTPException(status_code=404, detail="No such ticket")  # same 404: no peeking
    try:
        result = await run_desk(ticket_id, user, body.text)
    except VersionConflict:
        raise HTTPException(status_code=409, detail="Ticket changed, send it again") from None
    if isinstance(result.output, DeferredToolRequests):
        return ReplyOut(
            ticket_id=ticket_id, approval=approvals.record_pending(ticket_id, result.output)
        )
    return ReplyOut(
        ticket_id=ticket_id, category=result.output.category, message=result.output.message
    )
