"""Episode 07: one billing question, three ways to answer it. Who holds the wheel?

Each pattern returns (answer, model requests). The count comes from the run's bill, and the bill
includes the specialist. Try it: `uv run --group app python -m app.patterns`.
"""

from typing import Literal

from pydantic_ai import Agent, RunContext, RunUsage, UsageLimits

from app import AGENT_MODEL, MODEL
from app.agents import billing_expert
from learningdantic import has_key

QUESTION = "I was charged twice for order 1042. Can I get my money back?"
BUDGET = UsageLimits(request_limit=4)  # one question may spend at most 4 model requests
BILLS: dict[str, RunUsage] = {}  # each pattern's latest bill, for the live tokens-and-cost print

solo = Agent(
    AGENT_MODEL,
    name="one_agent",
    instructions="You are Acme Desk support. Answer billing questions in at most two sentences.",
)

classifier = Agent(
    AGENT_MODEL,
    name="classifier",
    output_type=Literal["billing", "shipping", "other"],
    instructions="Label the message: billing (money, refunds), shipping (parcels) or other.",
)

front_desk = Agent(
    AGENT_MODEL,
    name="front_desk",
    instructions="For any billing question, call ask_billing first. Then answer in one sentence.",
)


@front_desk.tool
async def ask_billing(ctx: RunContext, question: str) -> str:
    """Ask the billing expert. Use it for every billing question."""
    # usage= puts the expert's requests on this bill; usage_limits= makes it obey the same budget.
    result = await billing_expert.run(question, usage=ctx.usage, usage_limits=ctx.usage_limits)
    return result.output


async def one_agent(text: str) -> tuple[str, int]:
    """One agent holds the wheel and nothing else is involved."""
    result = await solo.run(text, usage_limits=BUDGET)
    BILLS["one_agent"] = result.usage
    return result.output, result.usage.requests


async def code_routing(text: str) -> tuple[str, int]:
    """Your code holds the wheel: a classifier labels the question, `match` picks who answers."""
    bill = RunUsage()  # one bill for both runs
    kind = (await classifier.run(text, usage=bill, usage_limits=BUDGET)).output
    match kind:
        case "billing":
            answer = (await billing_expert.run(text, usage=bill, usage_limits=BUDGET)).output
        case _:
            answer = "Passed to a human."
    BILLS["code_routing"] = bill
    return answer, bill.requests


async def delegation(text: str) -> tuple[str, int]:
    """The model holds the wheel: it decides to call ask_billing, then keeps talking."""
    result = await front_desk.run(text, usage_limits=BUDGET)
    BILLS["delegation"] = result.usage
    return result.output, result.usage.requests


async def main() -> None:
    for pattern in (one_agent, code_routing, delegation):
        answer, requests = await pattern(QUESTION)
        print(f"{pattern.__name__:12} {requests} request(s)  {answer[:50]!r}")
    if not has_key(MODEL):  # keyless demo mode: the counts above came from TestModel
        print("live part skipped: no key for MODEL, so no real tokens or cost")
        return
    for name, bill in BILLS.items():
        if bill.cost is None:
            raise SystemExit(f"stop: no cost for MODEL={MODEL} (no price data, or a fake model)")
        print(f"{name:12} {bill.input_tokens} tokens in, {bill.output_tokens} out, ${bill.cost}")


if __name__ == "__main__":
    import anyio

    anyio.run(main)
