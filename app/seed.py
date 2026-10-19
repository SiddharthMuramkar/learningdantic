"""The demo data: two orders, so there is something to ask the desk about."""

from sqlalchemy.orm import Session

from app.models import Order

ORDERS = [
    Order(id=1042, customer="ada", items="1 blue mug", status="delivered", amount_cents=1200),
    Order(id=2077, customer="bo", items="2 white mugs", status="in transit", amount_cents=2400),
]


def seed(session: Session) -> None:
    """Put the demo orders in the table. Safe to run twice."""
    for order in ORDERS:
        session.merge(order)  # insert, or update the row with the same id
    session.commit()
