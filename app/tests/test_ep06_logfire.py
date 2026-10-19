"""Episode 06: Logfire. One chat request leaves spans for the agent, model, tool and SQL."""

from pydantic_ai.models.test import TestModel

from app.agents import desk
from app.models import Ticket


def test_one_chat_request_leaves_agent_model_tool_and_sql_spans(client, session, capfire):
    ticket = Ticket(customer="ada", subject="Cracked mug")
    session.add(ticket)
    session.commit()
    capfire.exporter.clear()  # forget the spans from adding the ticket; keep only the chat

    # TestModel calls every tool it is shown: lookup_order and ask_billing.
    with desk.override(model=TestModel()):
        response = client.post(
            f"/tickets/{ticket.id}/messages",
            json={"text": "Where is order 1042?"},
            headers={"X-Demo-User": "ada"},
        )
    assert response.status_code == 200

    spans = capfire.exporter.exported_spans_as_dict()
    names = [span["name"] for span in spans]
    assert any(name.startswith("invoke_agent") for name in names)
    assert any(name.startswith("chat") for name in names)
    assert any(name.startswith("execute_tool") for name in names)
    statements = [span["attributes"].get("db.statement", "") for span in spans]
    assert any(statement.startswith("UPDATE tickets") for statement in statements)
