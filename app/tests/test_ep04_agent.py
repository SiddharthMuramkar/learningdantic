"""Episode 04: the agent joins. A ticket remembers its chat, and the desk keeps its rules."""

from pydantic_ai.messages import ModelResponse, ToolCallPart, ToolReturnPart, UserPromptPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import approvals, memory
from app.agents import desk
from app.db import engine
from app.models import AuditLog, Ticket

ADA = {"X-Demo-User": "ada"}
BO = {"X-Demo-User": "bo"}
SAM = {"X-Demo-User": "sam"}


def new_ticket(session, customer="ada") -> int:
    """Add a ticket straight to the table (the ticket routes are another episode)."""
    ticket = Ticket(customer=customer, subject="Cracked mug")
    session.add(ticket)
    session.commit()
    return ticket.id


def say(client, ticket_id, text, who=ADA):
    return client.post(f"/tickets/{ticket_id}/messages", json={"text": text}, headers=who)


def reply(info, message):
    """A scripted model ends its run by calling the output tool, which holds a Reply."""
    return ModelResponse(
        parts=[ToolCallPart(info.output_tools[0].name, {"category": "other", "message": message})]
    )


def echo(messages, info):
    """A scripted model whose reply lists every customer message it can see."""
    seen = [p.content for m in messages for p in m.parts if isinstance(p, UserPromptPart)]
    return reply(info, " | ".join(seen))


def look_up(order_id):
    """A scripted model: look the order up, then reply with what the tool said."""

    def model(messages, info):
        last = messages[-1].parts[-1]
        if isinstance(last, ToolReturnPart):
            return reply(info, last.content)
        return ModelResponse(parts=[ToolCallPart("lookup_order", {"order_id": order_id})])

    return model


def test_the_second_message_sees_the_first(client, session):
    ticket_id = new_ticket(session)
    with desk.override(model=FunctionModel(echo)):
        first = say(client, ticket_id, "My mug is cracked")
        second = say(client, ticket_id, "It is order 1042")
    assert first.json()["message"] == "My mug is cracked"
    assert second.json()["message"] == "My mug is cracked | It is order 1042"


def test_usage_carries_over_and_the_version_counts_saves(client, session):
    ticket_id = new_ticket(session)
    with desk.override(model=FunctionModel(echo)):
        say(client, ticket_id, "one")
        say(client, ticket_id, "two")
    conversation, version = memory.load(ticket_id)
    assert (conversation.usage.requests, version) == (2, 2)


def test_a_stale_version_gives_409(client, session):
    ticket_id = new_ticket(session)

    def rival(messages, info):
        """While this run is in flight, someone else saves the same ticket first."""
        with Session(engine) as other, other.begin():
            other.execute(update(Ticket).where(Ticket.id == ticket_id).values(version=1))
        return echo(messages, info)

    with desk.override(model=FunctionModel(rival)):
        response = say(client, ticket_id, "hello")
    assert response.status_code == 409


def test_ada_is_never_offered_issue_refund_but_sam_is(client, session):
    ticket_id = new_ticket(session)
    model = TestModel(call_tools=[])  # shows its tools to nobody, just reports them
    offered = {}
    with desk.override(model=model):
        for name, who in [("ada", ADA), ("sam", SAM)]:
            say(client, ticket_id, "Refund order 1042", who)
            offered[name] = [t.name for t in model.last_model_request_parameters.function_tools]
    assert "issue_refund" not in offered["ada"]
    assert "issue_refund" in offered["sam"]


def test_a_staff_refund_pauses_for_a_person_instead_of_running(client, session, monkeypatch):
    ticket_id = new_ticket(session)
    waiting = []
    monkeypatch.setattr(approvals, "record_pending", lambda _id, requests: waiting.append(requests))
    with desk.override(model=TestModel()):  # calls every tool it is shown, refund included
        response = say(client, ticket_id, "Refund order 1042", SAM)
    assert response.status_code == 200
    assert [call.tool_name for call in waiting[0].approvals] == ["issue_refund"]


def test_a_customer_only_finds_their_own_orders_and_tickets(client, session):
    ticket_id = new_ticket(session)
    with desk.override(model=FunctionModel(look_up(1042))):
        assert "1 blue mug" in say(client, ticket_id, "Where is it?").json()["message"]
    with desk.override(model=FunctionModel(look_up(2077))):  # bo's order
        assert say(client, ticket_id, "Where is it?").json()["message"] == "There is no order 2077."
        assert "2 white mugs" in say(client, ticket_id, "Where is it?", SAM).json()["message"]
    assert say(client, ticket_id, "Hi", BO).status_code == 404  # bo cannot use ada's ticket


def test_every_tool_call_lands_in_the_audit_log(client, session):
    ticket_id = new_ticket(session)
    with desk.override(model=FunctionModel(look_up(1042))):
        say(client, ticket_id, "Where is it?")
    assert list(session.scalars(select(AuditLog.tool).where(AuditLog.ticket_id == ticket_id))) == [
        "lookup_order"
    ]


def test_a_refund_promise_is_sent_back_once(client, session):
    ticket_id = new_ticket(session)
    promised = []

    def promise_then_fix(messages, info):
        promised.append(1)
        text = "We guarantee a full refund!" if len(promised) == 1 else "A teammate will review it."
        return reply(info, text)

    with desk.override(model=FunctionModel(promise_then_fix)):
        response = say(client, ticket_id, "Refund my mug!")
    assert response.json()["message"] == "A teammate will review it."


def test_a_stuck_desk_is_stopped_by_the_turn_limit(client, session):
    ticket_id = new_ticket(session)
    desk_requests = []

    def stuck(messages, info):
        desk_requests.append(1)
        return ModelResponse(parts=[ToolCallPart("ask_billing", {"question": "Refund?"})])

    with desk.override(model=FunctionModel(stuck)):
        response = say(client, ticket_id, "Refund?")
    assert response.status_code == 429
    assert len(desk_requests) == 3  # 3 desk + 3 billing requests use up the 6 (50 would allow 25)
