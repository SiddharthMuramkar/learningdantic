# 06 orchestration
Status: todo

## What and why
The lesson Siddharth asked for most, episode 07: who holds the wheel. Wave 3, after 04.
app/patterns.py: one billing question handled three ways, each returning (answer, model requests):
- `one_agent`: one agent with the tools, it decides everything.
- `code_routing`: a tiny classifier agent (output type a Literal) picks a lane, then your code uses `match` to
  call the specialist (`billing_expert` from agents.py). The code holds the wheel.
- `delegation`: an agent with an async tool that runs billing_expert, forwarding usage and usage_limits.
  The model holds the wheel.
Requests come from `result.usage.requests`, which counts the specialist too. No asyncio: "parallel" is shown only
as Pydantic AI's own parallel tool calls in one step, as a note. If `has_key(MODEL)`, a guarded part prints real
token counts and cost for the three (stop if cost is None); otherwise it says it skipped.
Episode 07 ends with a short note naming the words: workflow (Anthropic vs Temporal), handoff (one-way in
OpenAI, "programmatic hand-off" in Pydantic AI), swarm (mostly a marketing word), and "add agents only when a
count shows it helps".
Your piece: `code_routing`.

## Done when
- [ ] test_ep07_orchestration.py (FunctionModel, keyless): all three answer the same question, and the test
      asserts each one's request count and that code_routing makes fewer requests than delegation
- [ ] Blanking `code_routing` turns the test red (checked, then restored)
- [ ] track/07-orchestration/EPISODE.md in the contract format, Predict = guess the three request counts
- [ ] The Check passes; /code-review and /security-review run, real findings fixed

## Touches
app/patterns.py, app/tests/test_ep07_orchestration.py, track/07-orchestration/EPISODE.md

## Out of scope
A scoreboard table, evaluator loops, pydantic-graph, asyncio.gather, changes to agents.py.
