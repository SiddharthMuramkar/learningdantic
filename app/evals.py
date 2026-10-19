"""The desk's eval (spec 08): notebook 14's `desk_evals`, run against the app's desk.

Each case opens a real ticket for ada, then runs `run_desk` on it. Keyless, a scripted model plays
the desk (see app/tests/test_ep10_shipping.py). To try a real model, run
`desk_evals.evaluate(answer)` inside `desk.override(model=MODEL)`, with the same override on
`billing_expert` and `shipping_expert`.
"""

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Contains, IsInstance, ToolCorrectness
from sqlalchemy.orm import Session

from app import models
from app.agents import run_desk
from app.db import engine
from app.identity import User


async def answer(text: str) -> str:
    """The eval task: one customer ticket in, the desk's message out."""
    with Session(engine) as session:  # closed before the await: no DB session is held across it
        ticket = models.Ticket(customer="ada", subject=text[:200])
        session.add(ticket)
        session.commit()
        ticket_id = ticket.id
    result = await run_desk(ticket_id, User("ada", "customer"), text)
    return result.output.message


desk_evals = Dataset(
    name="desk",
    cases=[
        Case(
            name="refund",
            inputs="My mug from order 1042 arrived cracked. I want my money back.",
            evaluators=[ToolCorrectness(expected_tools=["lookup_order", "ask_billing"])],
        ),
        Case(
            name="status",
            inputs="Has order 1042 arrived yet?",
            evaluators=[ToolCorrectness(expected_tools=["lookup_order"])],
        ),
        Case(
            name="late_parcel",
            inputs="Order 1042 says delivered, but my parcel never arrived.",
            evaluators=[ToolCorrectness(expected_tools=["lookup_order", "ask_shipping"])],
        ),
    ],
    evaluators=[IsInstance("str"), Contains("Reply HELP")],
)
