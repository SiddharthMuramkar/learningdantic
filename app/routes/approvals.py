"""POST /tickets/{ticket_id}/approvals/{refund_id}: a person decides, then the desk resumes."""

from fastapi import APIRouter, HTTPException
from pydantic_ai import DeferredToolRequests, ToolDenied
from sqlalchemy import update
from sqlalchemy.orm import Session

from app import memory
from app.agents import run_desk
from app.approvals import record_pending
from app.db import engine
from app.identity import StaffDep
from app.models import Refund
from app.schemas import DecisionIn, ReplyOut

router = APIRouter()


@router.post("/tickets/{ticket_id}/approvals/{refund_id}")
async def decide(ticket_id: int, refund_id: int, body: DecisionIn, user: StaffDep) -> ReplyOut:
    new_status = "approved" if body.decision == "approve" else "rejected"
    # The ids and arguments come from the STORED conversation, never from this request.
    conversation, _ = memory.load(ticket_id)
    requests = conversation.deferred_tool_requests if conversation else None
    answers = (
        {call.tool_call_id: ToolDenied("Not approved.") for call in requests.approvals}
        if requests
        else {}
    )
    with Session(engine) as session, session.begin():
        # One guarded UPDATE is the double-click lock: only the first request finds it 'pending'.
        call_id = session.scalar(
            update(Refund)
            .where(
                Refund.id == refund_id, Refund.ticket_id == ticket_id, Refund.status == "pending"
            )
            .values(status=new_status)
            .returning(Refund.tool_call_id)
        )
        # Raising in here rolls the UPDATE back: a refund nobody can resume stays pending.
        if call_id not in answers:
            raise HTTPException(409, "That refund is not waiting for a decision on this ticket.")
        # The resumed run needs an answer for every waiting call, so any sibling is rejected too.
        session.execute(
            update(Refund)
            .where(Refund.ticket_id == ticket_id, Refund.status == "pending")
            .values(status="rejected")
        )

    if new_status == "approved":
        answers[call_id] = True
    try:
        result = await run_desk(
            ticket_id, user, None, deferred_tool_results=requests.build_results(approvals=answers)
        )
    except memory.VersionConflict:  # shortcut: the refund stays decided, no retry path yet
        raise HTTPException(409, "The ticket changed, try again.") from None

    if isinstance(result.output, DeferredToolRequests):
        return ReplyOut(ticket_id=ticket_id, approval=record_pending(ticket_id, result.output))
    return ReplyOut(
        ticket_id=ticket_id, category=result.output.category, message=result.output.message
    )
