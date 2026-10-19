"""The four tables, as Python classes. `migrations/` turns them into real tables."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    MetaData,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Every constraint gets a predictable name, so a later migration can drop it by name.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = {datetime: DateTime(timezone=True)}  # Postgres "timestamptz"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str]
    items: Mapped[str]
    status: Mapped[str]
    amount_cents: Mapped[int]


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str]
    subject: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    conversation: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    version: Mapped[int] = mapped_column(server_default=text("0"))


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    tool: Mapped[str]
    at: Mapped[datetime] = mapped_column(server_default=func.now())


class Refund(Base):
    __tablename__ = "refunds"
    __table_args__ = (
        UniqueConstraint("ticket_id", "tool_call_id"),
        CheckConstraint("status IN ('pending', 'approved', 'rejected', 'executed')", name="status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    amount_cents: Mapped[int]
    tool_call_id: Mapped[str]
    status: Mapped[str] = mapped_column(server_default="pending")
