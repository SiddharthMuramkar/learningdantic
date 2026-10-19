"""Episode 08 (locked): a refund waits for a person across two requests."""

import pytest
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from sqlalchemy import select

from app import agents
from app.models import Refund

SAM = {"X-Demo-User": "sam"}
ADA = {"X-Demo-User": "ada"}


def refund_order_1042(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """A fake model: ask for the refund once, then answer."""
    asked = any(
        isinstance(part, ToolCallPart) and part.tool_name == "issue_refund"
        for message in messages
        if isinstance(message, ModelResponse)
        for part in message.parts
    )
    if asked:
        answer = {"category": "billing", "message": "Done."}
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, answer)])
    return ModelResponse(parts=[ToolCallPart("issue_refund", {"order_id": 1042})])


@pytest.fixture(autouse=True)
def fake_model(monkeypatch):
    # Agent.override would not reach the thread TestClient runs the app in; setting the model does.
    monkeypatch.setattr(agents.desk, "model", FunctionModel(refund_order_1042))


def ask_for_refund(client):
    """Sam opens a ticket and asks for a refund. Returns (ticket_id, the approval in the reply)."""
    ticket = client.post("/tickets", json={"subject": "Broken mug"}, headers=SAM).json()["id"]
    reply = client.post(f"/tickets/{ticket}/messages", json={"text": "Refund 1042"}, headers=SAM)
    assert reply.status_code == 200, reply.text
    return ticket, reply.json()["approval"]


def decide(client, ticket, approval, decision, headers=SAM):
    url = f"/tickets/{ticket}/approvals/{approval['refund_id']}"
    return client.post(url, json={"decision": decision}, headers=headers)


def statuses(session):
    return sorted(session.scalars(select(Refund.status)).all())


def test_chat_waits_for_a_person(client, session):
    _, approval = ask_for_refund(client)
    assert (approval["order_id"], approval["amount_cents"]) == (1042, 1200)
    assert statuses(session) == ["pending"]  # asked for, not executed


def test_approve_executes_exactly_once(client, session):
    ticket, approval = ask_for_refund(client)
    first = decide(client, ticket, approval, "approve")
    assert first.status_code == 200, first.text
    assert first.json()["message"] == "Done."
    assert statuses(session) == ["executed"]
    assert decide(client, ticket, approval, "approve").status_code == 409  # the double click
    assert statuses(session) == ["executed"]  # and the row did not move


def test_reject_executes_nothing(client, session):
    ticket, approval = ask_for_refund(client)
    assert decide(client, ticket, approval, "reject").status_code == 200
    assert statuses(session) == ["rejected"]


def test_customer_cannot_decide(client, session):
    ticket, approval = ask_for_refund(client)
    assert decide(client, ticket, approval, "approve", ADA).status_code == 403
    assert statuses(session) == ["pending"]


def test_refund_from_another_ticket_is_refused(client, session):
    ticket, approval = ask_for_refund(client)
    other_ticket, _ = ask_for_refund(client)
    assert decide(client, other_ticket, approval, "approve").status_code == 409
    assert statuses(session) == ["pending", "pending"]
    assert ticket != other_ticket
