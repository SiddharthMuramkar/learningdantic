"""The shapes of what goes in and out of the API. FastAPI checks every one of them."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # build it straight from a database row

    id: int
    items: str
    status: str
    amount_cents: int


class TicketIn(BaseModel):
    subject: str = Field(min_length=1, max_length=200)


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer: str
    subject: str


class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class ApprovalOut(BaseModel):
    refund_id: int
    order_id: int
    amount_cents: int


class ReplyOut(BaseModel):
    ticket_id: int
    category: str | None = None
    message: str | None = None
    approval: ApprovalOut | None = None


class DecisionIn(BaseModel):
    decision: Literal["approve", "reject"]
