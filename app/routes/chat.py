"""The chat route. Stub: spec 04 fills it in (episode 04)."""

from fastapi import APIRouter, HTTPException

from app.identity import UserDep
from app.schemas import MessageIn, ReplyOut

router = APIRouter()


@router.post("/tickets/{ticket_id}/messages")
async def post_message(ticket_id: int, body: MessageIn, user: UserDep) -> ReplyOut:
    raise HTTPException(status_code=501, detail="spec 04")
