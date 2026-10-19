"""Episode 01: Postgres is running, and seed() puts the demo orders in it."""

from sqlalchemy import func, select, text

from app.models import Order
from app.seed import seed


def test_the_database_is_postgres_18(session):
    assert "PostgreSQL 18" in session.scalar(text("SELECT version()"))


def test_seed_adds_the_two_demo_orders(session):
    orders = {o.id: o for o in session.scalars(select(Order))}
    assert set(orders) == {1042, 2077}
    assert (orders[1042].customer, orders[1042].items) == ("ada", "1 blue mug")
    assert (orders[1042].status, orders[1042].amount_cents) == ("delivered", 1200)
    assert (orders[2077].customer, orders[2077].items) == ("bo", "2 white mugs")
    assert (orders[2077].status, orders[2077].amount_cents) == ("in transit", 2400)


def test_seed_twice_changes_nothing(session):
    seed(session)
    seed(session)
    assert session.scalar(select(func.count()).select_from(Order)) == 2
