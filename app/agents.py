"""The Acme desk agent and its billing expert: notebook 14's rules R1-R6, as app code.

Each rule lives in one place. R1 `RULES`, R2 `Reply` + `no_refund_promise`, R3 `.filtered`,
R4 `audit`, R5 `requires_approval=True` on `issue_refund`, R6 `UsageLimits` in `run_desk`.
"""

from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import BaseModel, Field
from pydantic_ai import (
    Agent,
    AgentRunResult,
    DeferredToolRequests,
    DeferredToolResults,
    FunctionToolset,
    ModelRetry,
    RunContext,
    UsageLimits,
)
from pydantic_ai.capabilities import Hooks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import AGENT_MODEL, approvals, memory
from app.db import engine
from app.identity import User
from app.models import AuditLog, Order

# --- Deps and Reply (R2's shape) --------------------------------------------------------------


@dataclass
class Deps:
    ticket_id: int
    customer: str
    role: str  # "customer" or "staff"


class Reply(BaseModel):  # R2
    category: Literal["billing", "shipping", "other"]
    message: str


# --- The billing expert (the refund policy lives here and nowhere else) -----------------------

billing_expert = Agent(
    AGENT_MODEL,
    name="billing_expert",
    instructions=(
        "You are Acme's billing expert. Refund policy: a teammate reviews every refund request "
        "within 5 days, and damaged mugs are replaced or refunded after that review. "
        "Never promise a refund. Answer in one sentence."
    ),
)

# --- The desk's tools -------------------------------------------------------------------------

desk_tools = FunctionToolset()


@desk_tools.tool
def lookup_order(ctx: RunContext[Deps], order_id: Annotated[int, Field(examples=[1042])]) -> str:
    """Look up one order by its number."""
    query = select(Order).where(Order.id == order_id)
    if ctx.deps.role != "staff":  # customers only see their own orders
        query = query.where(Order.customer == ctx.deps.customer)
    with Session(engine) as session:
        order = session.scalar(query)
        if order is None:  # a plain string, not ModelRetry: asking again would not help
            return f"There is no order {order_id}."
        return f"Order {order.id}: {order.items}, {order.status}, {order.amount_cents} cents."


@desk_tools.tool
async def ask_billing(ctx: RunContext[Deps], question: str) -> str:
    """Ask the billing expert about refunds, charges and invoices."""
    answer = await billing_expert.run(question, usage=ctx.usage, usage_limits=ctx.usage_limits)
    return answer.output


@desk_tools.tool(requires_approval=True)  # R5
def issue_refund(ctx: RunContext[Deps], order_id: Annotated[int, Field(examples=[1042])]) -> str:
    """Refund an order. Staff only."""
    # Runs only after a person approved this exact call; the refund row is spec 07's.
    return approvals.execute_refund(ctx.deps.ticket_id, ctx.tool_call_id)


# --- The desk: R1 to R4 -----------------------------------------------------------------------

RULES = (  # R1
    "You are the support desk for Acme, a shop that sells mugs. "
    "Look up the order before you answer about it. "
    "For any refund or charge question, ask billing and pass its answer on. "
    "End every message with: Need more help? Reply HELP."
)
PROMISE_WORDS = ["guarantee", "full refund"]

audit = Hooks()


@audit.on.before_tool_execute  # R4
def log_call(ctx, call, tool_def, args):
    with Session(engine) as session, session.begin():
        session.add(AuditLog(ticket_id=ctx.deps.ticket_id, tool=call.tool_name))
    return args


desk = Agent(
    AGENT_MODEL,
    name="desk",
    deps_type=Deps,
    instructions=RULES,  # R1
    output_type=[Reply, DeferredToolRequests],  # R2 (DeferredToolRequests lets R5 pause a run)
    toolsets=[  # R3
        desk_tools.filtered(lambda ctx, td: td.name != "issue_refund" or ctx.deps.role == "staff")
    ],
    capabilities=[audit],  # R4
)


@desk.output_validator  # R2
def no_refund_promise(output: Reply) -> Reply:
    found = [word for word in PROMISE_WORDS if word in output.message.lower()]
    if found:
        raise ModelRetry(
            f"Never promise a refund (you wrote {found}). Say a teammate reviews it within 5 days."
        )
    return output


# --- The desk's one front door: R6 ------------------------------------------------------------


async def run_desk(
    ticket_id: int,
    user: User,
    text: str | None,
    deferred_tool_results: DeferredToolResults | None = None,
) -> AgentRunResult:
    """One turn: load the ticket's conversation, run the desk, save the conversation again."""
    conversation, version = memory.load(ticket_id)  # no DB session stays open across the await
    used = conversation.usage.requests if conversation else 0  # the conversation carries usage
    result = await desk.run(
        text,
        deps=Deps(ticket_id=ticket_id, customer=user.name, role=user.role),
        conversation=conversation,
        deferred_tool_results=deferred_tool_results,
        usage_limits=UsageLimits(request_limit=used + 6),  # R6: at most 6 requests per turn
    )
    memory.save(ticket_id, result.conversation, version)
    return result


# --- spec 08 appends below this line ---
