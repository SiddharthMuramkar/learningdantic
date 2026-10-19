"""Episode 07: three ways to answer one question. Keyless: every model is scripted."""

from contextlib import contextmanager

import anyio
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import FunctionModel

from app import patterns
from app.agents import billing_expert
from app.patterns import QUESTION, code_routing, delegation, one_agent


def say(text):
    """A scripted model that always answers `text`."""
    return FunctionModel(lambda messages, info: ModelResponse(parts=[TextPart(text)]))


def label(kind):
    """A scripted classifier that always picks `kind` from its menu."""

    def model(messages, info):
        call = ToolCallPart(info.output_tools[0].name, {"response": kind})
        return ModelResponse(parts=[call])

    return FunctionModel(model)


def front_desk_model(messages, info):
    """Scripted front desk: first call ask_billing, then repeat what it returned."""
    if len(messages) == 1:
        call = ToolCallPart(info.function_tools[0].name, {"question": QUESTION})
        return ModelResponse(parts=[call])
    return ModelResponse(parts=[TextPart(f"Billing says: {messages[-1].parts[0].content}")])


@contextmanager
def scripted(kind="billing"):
    with (
        patterns.solo.override(model=say("One agent: refunds take 5 days.")),
        patterns.classifier.override(model=label(kind)),
        patterns.front_desk.override(model=FunctionModel(front_desk_model)),
        billing_expert.override(model=say("Refunds take 5 days.")),
    ):
        yield


def test_three_ways_answer_the_same_question():
    with scripted():
        got = {f.__name__: anyio.run(f, QUESTION) for f in (one_agent, code_routing, delegation)}
    assert all("5 days" in answer for answer, _ in got.values())
    requests = {name: count for name, (_, count) in got.items()}
    assert requests == {"one_agent": 1, "code_routing": 2, "delegation": 3}
    assert requests["code_routing"] < requests["delegation"]


def test_code_routing_hands_other_questions_to_a_human():
    with scripted("other"):
        assert anyio.run(code_routing, "Where is my parcel?") == ("Passed to a human.", 1)
