# 04 agent
Status: done

## What and why
Notebook 14's desk moves into the app, teaching episode 04 (the agent joins) and 06 (Logfire). Wave 2, after 01.
app/agents.py: `Deps`, `Reply`, `billing_expert`, `desk` and `run_desk` as contract.md says. Rules R1-R6 from
notebook 14 each live in one place: instructions, `Reply` + output validator (no "guarantee", no "full refund"),
`.filtered` toolset (issue_refund for staff only), a `Hooks` before_tool_execute that inserts an audit_log row,
`requires_approval=True` on issue_refund, per-turn `UsageLimits(request_limit=used + 6)`. Tools read customer
and role from ctx.deps and query with them; lookup_order returns a plain "not found" string, never ModelRetry.
ask_billing is `async def` and forwards `usage=ctx.usage, usage_limits=ctx.usage_limits`.
app/memory.py: load/save the whole `result.conversation` with ConversationTypeAdapter into tickets.conversation,
guarded by `version` (VersionConflict -> 409). Never hold a DB session across `await`.
app/routes/chat.py: `POST /tickets/{ticket_id}/messages` (async def), customer sees own tickets only.
Live check: one short chat on the real MODEL only if `has_key(MODEL)`; report `result.usage.cost` (stop if None).
Your pieces: ep04 = `memory.save`; ep06 = the `logfire.instrument_sqlalchemy` call (span test goes red).

## Done when
- [x] test_ep04_agent.py: two messages on one ticket, the second run sees the first (FunctionModel echo);
      usage carries over; a stale version gives 409; ada never sees issue_refund offered, sam does
- [x] test_ep06_logfire.py (capfire): one chat request has spans invoke_agent, chat, execute_tool and a SQL span
- [x] Blanking each piece turns its test red (checked, then restored)
- [x] track/04-agent-joins/EPISODE.md and track/06-logfire/EPISODE.md (06 also: what setup() does, optional
      Live view with your own Logfire login, `include_content=False` before real users)
- [x] The Check passes; /code-review and /security-review run, real findings fixed

## Touches
app/agents.py, app/memory.py, app/routes/chat.py, app/tests/test_ep04_agent.py, test_ep06_logfire.py, two EPISODE.md

## Out of scope
approvals.py (spec 07: keep calling its stubs). The shipping expert (spec 08). Streaming.
