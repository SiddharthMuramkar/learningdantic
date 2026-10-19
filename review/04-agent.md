# Review: 04 agent

PR: opened from branch `04-agent` (title "04 agent"). Built from `specs-base`, then merged with `origin/main` after 01, 02 and 05 landed.

## What I built
- `app/agents.py`: `Deps`, `Reply`, `billing_expert`, `desk_tools` (a `FunctionToolset`), `desk`, `run_desk`. Blocks are separated by comment lines; the file ends with `# --- spec 08 appends below this line ---`.
  - R1 `RULES` (instructions). R2 `Reply` + `@desk.output_validator no_refund_promise` ("guarantee", "full refund" -> `ModelRetry`). R3 `.filtered` on `ctx.deps.role`. R4 a `Hooks` `before_tool_execute` that inserts an `audit_log` row. R5 `requires_approval=True` on `issue_refund`. R6 `UsageLimits(request_limit=used + 6)` in `run_desk`, with `used` read from the loaded conversation.
  - `lookup_order` is a plain `def` that queries with `ctx.deps.customer` (staff see all) and returns a plain "There is no order N." string. `ask_billing` is `async def` and forwards `usage` and `usage_limits`. `issue_refund` returns `approvals.execute_refund(ctx.deps.ticket_id, ctx.tool_call_id)`.
  - `order_id` on both order tools has `Field(examples=[1042])`, so `TestModel` (the keyless demo) calls them with the seeded order.
- `app/memory.py`: `load` / `save` of the whole `result.conversation` with `ConversationTypeAdapter` (`dump_python(mode="json")` into the JSONB column), `save` is `UPDATE ... WHERE id AND version`, 0 rows -> `VersionConflict`. It also holds the `logfire.instrument_sqlalchemy` call (episode 06's piece).
- `app/routes/chat.py`: `POST /tickets/{ticket_id}/messages`, `async def`, short own `Session` closed before the `await`, 404 for a missing or foreign ticket (staff see all), 409 on `VersionConflict`, 429 on `UsageLimitExceeded`, `approvals.record_pending` on `DeferredToolRequests`.
- Tests: `app/tests/test_ep04_agent.py` (9 tests), `app/tests/test_ep06_logfire.py` (1 test, `capfire`).
- `track/04-agent-joins/EPISODE.md` (88 lines), `track/06-logfire/EPISODE.md` (56 lines).
- `specs/04-agent.md`: Done-when ticked, `Status: done`.

## Commands and results
| Command | Result |
|---|---|
| Context7 `/pydantic/pydantic-ai` (4 queries), `/pydantic/logfire` (3 queries) | see Sources |
| `uv run --frozen python` checks of `Agent.run`, `Conversation`, `UsageLimits`, `RunContext`, `Hooks`, `DeferredToolRequests.build_results`, `FunctionToolset.filtered`, `logfire.instrument_sqlalchemy`, `instrument_pydantic_ai` signatures | read, see Sources |
| Scratch script (no app): conversation JSON round trip, deferred approvals resume, filter, hook | worked; also showed `Field(examples=[1042])` drives `TestModel` args |
| Dry run against a scratch copy of `origin/01-skeleton` (outside the repo, `uv sync --group app` there) before 01 merged | 12 passed, then 15 passed with the 3 ep01/ep02 tests |
| `git merge origin/main` (01, then the per-checkout DB commit, 02, 05) | add/add conflicts on `agents.py`, `memory.py`, `routes/chat.py`: `git checkout --ours`; `specs/01-skeleton.md`: took main's |
| `uv sync --group app` | ok |
| `uv run ruff check . && uv run ruff format --check .` | pass |
| `uv run python scripts/check_notebooks.py` | `checked 29 notebooks, 0 problem(s)` |
| `uv run --group app pytest app/tests` (SPEC.md Check) | 15 passed (before the final merge; see the last row) |
| Blank `memory.save` | 8 of 9 ep04 tests red; restored |
| Remove `logfire.instrument_sqlalchemy` | ep06 test red (`UPDATE tickets` span check); restored |
| Remove the R3 filter | ep04 `test_ada_is_never_offered_issue_refund_but_sam_is` red; restored |
| Remove `usage_limits=` (R6) | first version of the test stayed green (default limit is 50); I made it count desk requests (3 vs 25); now red; restored |
| Drop `conversation=conversation` from `run_desk` (episode 04 Break it) | 2 tests red; restored |
| Comment out `logfire.instrument_pydantic_ai()` in `setup()` (episode 06 Break it) | ep06 test red; restored with `git restore` |
| Keyless `uvicorn` on port 8764/8765 against my own test DB + `curl` | ada reply `{"category":"billing","message":"a","approval":null}`; second message made version 2, 8 messages, 4 requests; sam's refund returned `approval: null` (stub) and stored `deferred_tool_requests`; bo on ada's ticket 404; no header 401 |
| Live check: one chat on the real `MODEL` (`has_key` was true), ada, order 1042, my own test DB | valid `Reply` (billing), `requests: 4`, `cost: 0.004144` (not None), audit `['lookup_order', 'ask_billing']`, conversation saved at version 1 |
| `/code-review` (high) | 5 findings: fixed the unhandled `UsageLimitExceeded` (now 429) and the untyped hook; skipped 3 (below) |
| `/security-review` | no high-confidence findings |
| Final `git merge origin/main`, ruff, format, Check | see the last line of this table once run |

## What failed or went wrong
- First R6 test did not discriminate (see table); fixed.
- `sed -i` on macOS rejected my substitution once; I used Python and the Edit tool.
- Before 01 merged I copied a few files into `/tmp` once by mistake (removed again); all other scratch files are in the scratchpad.
- `docker compose exec db psql` for the episode checkpoints ran only against my own test database, never the shared `acme` one. Dropped my `acme_04_test` at the end.

## Never ran or not verified
- Episode 04 steps 1-3 and 7 (create a ticket through `POST /tickets`) use spec 03's route, which was a 501 stub here. I made the tickets with SQLAlchemy and copied outputs; the `{"id":1,"customer":"ada","subject":"Cracked mug"}` checkpoint is from the contract, not a run.
- Episode 04 runs its curl steps on the dev database `acme`, which I never touched. Outputs were captured on my test database.
- Episode 06 step 3 (Logfire Live view, `logfire auth`) needs a login; the span names and SQL line names come from `capfire` output, not from the web UI. Step 4 (`include_content=False`) was not run.
- `approvals.record_pending` and `execute_refund` are still spec 07's stubs on this branch. Nothing here runs a refund end to end.
- A second `UPDATE` race (two truly concurrent requests) was tested only by a model function that bumps the version mid-run.

## Guesses
- `Deps.customer` is the user who is writing (`user.name`), also for staff; the contract only says `customer`.
- Sync SQLAlchemy calls (`memory.load/save`, the route's ticket check) run directly inside `async def`; they block the event loop for milliseconds. Fine for this demo.
- `logfire.instrument_sqlalchemy` lives in `app/memory.py` because the contract gives the call to spec 04 and `main.py` is 01's. AGENTS.md says `main.py` adds it; if both do, SQL spans could double. Please settle in one place.
- `skip_dep_check=True` is required: OpenTelemetry's SQLAlchemy instrumentor lists support only for `< 2.1` and printed "nothing can be instrumented" on the locked SQLAlchemy 2.1.5. With the flag, SQL spans appear (checked). This can break when SQLAlchemy or the instrumentor changes.
- Spec 08: add the shipping expert and `ask_shipping` below the marker line with `@desk_tools.tool` (the toolset is read at run time, so adding after `desk` is built works) and add the one-line instruction with `@desk.instructions` instead of editing `RULES`.

## Known gaps (skipped code-review findings)
- A new message sent while a refund waits for a person makes the next run store `deferred_tool_requests=None`; spec 07's approve route would then find nothing to resume. Spec 07 should check this, or the chat route should answer 409 while a request is pending.
- The chat route reads the ticket twice (its own check, then `memory.load`).
- Instrumentation runs at import time of `app/memory.py`.

## Sources
- Context7: `/pydantic/pydantic-ai` (`ConversationTypeAdapter`, `conversation=`, `DeferredToolRequests`, `build_results`, `Hooks.on.before_tool_execute`, `.filtered`, `UsageLimits`, `ctx.usage`, `ctx.usage_limits`), `/pydantic/logfire` (`instrument_sqlalchemy` with `engine=`, `capfire`, `instrument_pydantic_ai(include_content=False)`).
- Installed signatures (`inspect.signature`, pydantic-ai 2.57.0): `Agent.run`, `UsageLimits`, `FunctionToolset.tool`, `tool_plain`, `filtered`, `Hooks.__init__`, `DeferredToolRequests.build_results`, `logfire.instrument_sqlalchemy`, `logfire.instrument_pydantic_ai`; `RunContext` fields (`tool_call_id`, `usage`, `usage_limits`, `deps`); `AgentRunResult` attributes (`conversation`, `usage`).
- Versions: pydantic-ai 2.57.0, logfire 5.2.0, sqlalchemy 2.1.5, fastapi 0.146.0, Python 3.14.4.
