"""The desk agent and its billing expert. Stub: spec 04 fills this in (spec 08 adds shipping).

Spec 04 replaces each bare annotation below with a real Agent and writes the body of `run_desk`.
"""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent, AgentRunResult, DeferredToolResults

from app.identity import User


@dataclass
class Deps:
    ticket_id: int
    customer: str
    role: str


class Reply(BaseModel):
    category: Literal["billing", "shipping", "other"]
    message: str


billing_expert: Agent
desk: Agent  # deps_type=Deps, output_type=[Reply, DeferredToolRequests]


async def run_desk(
    ticket_id: int,
    user: User,
    text: str | None,
    deferred_tool_results: DeferredToolResults | None = None,
) -> AgentRunResult:
    raise NotImplementedError("spec 04")
