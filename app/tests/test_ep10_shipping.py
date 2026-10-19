"""Episode 10, the locked test for your piece: `ask_shipping` and `shipping_expert`."""

from contextlib import contextmanager

import pytest
from pydantic_ai.messages import ModelResponse, ToolCallPart, ToolReturnPart, UserPromptPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.models.test import TestModel
from sqlalchemy import select

from app import models
from app.agents import billing_expert, desk, run_desk, shipping_expert
from app.evals import answer, desk_evals
from app.identity import User

pytestmark = pytest.mark.anyio  # lets the tests below be `async def` and `await` the desk

ADA = User("ada", "customer")
PARCEL = "Order 1042 says delivered, but my parcel never arrived."
SHIPPING_ANSWER = "Parcels take up to 7 days; after that we send a new one."
shown = []  # the instructions the scripted desk was shown, one entry per request


def fake_desk(messages, info):
    """A scripted desk: look up order 1042, ask billing or shipping, then reply."""
    shown.append(info.instructions)
    text = next(
        part.content
        for message in reversed(messages)
        for part in message.parts
        if isinstance(part, UserPromptPart)
    ).lower()
    money = "money" in text or "refund" in text
    parcel = "parcel" in text
    returns = [part for part in messages[-1].parts if isinstance(part, ToolReturnPart)]
    if not returns:  # the first request: call the tools
        calls = [ToolCallPart("lookup_order", {"order_id": 1042})]
        if money:
            calls.append(ToolCallPart("ask_billing", {"question": text}))
        if parcel:
            calls.append(ToolCallPart("ask_shipping", {"question": text}))
        return ModelResponse(parts=calls)
    experts = [part.content for part in returns if part.tool_name.startswith("ask_")]
    category = "billing" if money else "shipping" if parcel else "other"
    reply = {"category": category, "message": " ".join([*experts, "Need more help? Reply HELP."])}
    return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, reply)])


@contextmanager
def scripted():
    """The desk plays by the rules and both experts answer with fixed sentences. No key needed."""
    shown.clear()
    with (
        desk.override(model=FunctionModel(fake_desk)),
        billing_expert.override(model=TestModel(custom_output_text="A teammate reviews it.")),
        shipping_expert.override(model=TestModel(custom_output_text=SHIPPING_ANSWER)),
    ):
        yield


def new_ticket(session) -> int:
    ticket = models.Ticket(customer="ada", subject="parcel")
    session.add(ticket)
    session.commit()
    return ticket.id


async def test_parcel_ticket_asks_shipping(session):
    ticket_id = new_ticket(session)
    with scripted():
        result = await run_desk(ticket_id, ADA, PARCEL)
    assert result.output.category == "shipping"
    assert SHIPPING_ANSWER in result.output.message  # the expert's answer reached the reply
    assert result.usage.requests == 3  # the desk's 2 plus the shipping expert's 1, on one bill
    tools = session.scalars(
        select(models.AuditLog.tool).where(models.AuditLog.ticket_id == ticket_id)
    ).all()
    assert sorted(tools) == ["ask_shipping", "lookup_order"]  # R4 logs the new tool too
    assert "shipping" in shown[0].lower()  # R1: the rule reached the model


async def test_customer_is_offered_ask_shipping(session):
    model = TestModel(call_tools=[])
    with desk.override(model=model):
        await run_desk(new_ticket(session), ADA, "Where is my parcel?")
    offered = [tool.name for tool in model.last_model_request_parameters.function_tools]
    assert "ask_shipping" in offered
    assert "issue_refund" not in offered  # R3 still holds


async def test_desk_evals_pass_keyless():
    with scripted():
        report = await desk_evals.evaluate(answer, name="scripted desk", progress=False)
    report.print(include_durations=False)
    assert {case.name for case in report.cases} == {"refund", "status", "late_parcel"}
    assert not report.failures
    assert report.averages().assertions == 1.0
