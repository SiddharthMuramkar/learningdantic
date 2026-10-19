"""Ticket and order routes (episode 03)."""

from fastapi import APIRouter, HTTPException

from app.db import SessionDep
from app.identity import UserDep
from app.models import Order, Ticket
from app.schemas import OrderOut, TicketIn, TicketOut

router = APIRouter()


@router.post("/tickets", status_code=201)
def create_ticket(body: TicketIn, session: SessionDep, user: UserDep) -> TicketOut:
    ticket = Ticket(customer=user.name, subject=body.subject)
    session.add(ticket)
    session.commit()
    return ticket


@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int, session: SessionDep, user: UserDep) -> TicketOut:
    ticket = session.get(Ticket, ticket_id)
    # 404, not 403: a customer must not learn that someone else's ticket exists.
    if ticket is None or (user.role != "staff" and ticket.customer != user.name):
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/orders/{order_id}")
def get_order(order_id: int, session: SessionDep, user: UserDep) -> OrderOut:
    order = session.get(Order, order_id)
    if order is None or (user.role != "staff" and order.customer != user.name):
        raise HTTPException(status_code=404, detail="Order not found")
    return order
