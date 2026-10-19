"""Ticket and order routes. Stub: spec 03 fills these in (episode 03)."""

from fastapi import APIRouter, HTTPException

from app.db import SessionDep
from app.identity import UserDep
from app.schemas import OrderOut, TicketIn, TicketOut

router = APIRouter()


@router.post("/tickets", status_code=201)
def create_ticket(body: TicketIn, session: SessionDep, user: UserDep) -> TicketOut:
    raise HTTPException(status_code=501, detail="spec 03")


@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int, session: SessionDep, user: UserDep) -> TicketOut:
    raise HTTPException(status_code=501, detail="spec 03")


@router.get("/orders/{order_id}")
def get_order(order_id: int, session: SessionDep, user: UserDep) -> OrderOut:
    raise HTTPException(status_code=501, detail="spec 03")
