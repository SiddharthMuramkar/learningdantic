"""The approval route. Stub: spec 07 fills it in (episode 08)."""

from fastapi import APIRouter, HTTPException

from app.identity import StaffDep
from app.schemas import DecisionIn, ReplyOut

router = APIRouter()


@router.post("/tickets/{ticket_id}/approvals/{refund_id}")
async def decide(ticket_id: int, refund_id: int, body: DecisionIn, staff: StaffDep) -> ReplyOut:
    raise HTTPException(status_code=501, detail="spec 07")
