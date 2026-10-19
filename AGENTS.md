# AGENTS.md

A beginner course in Jupyter notebooks on Pydantic AI 2.57 and Logfire 5.2. The learner owns the design, you
write the code, and a `# 🔍 Verify` cell checks it.

The rules below apply to `notebooks/` and `solutions/`, except **Safety**, which applies everywhere. The
Acme Desk app (`app/`, `migrations/`, `track/`) has its own rules in **Full-stack track** at the end.

## Before you write code

- Look up every `pydantic_ai`, `pydantic_evals` and `logfire` API you use in Context7 (`/pydantic/pydantic-ai`,
  `/pydantic/logfire`) or https://pydantic.dev/docs/ai/llms.txt. Your memory predates v2 (June 2026).
- If the brief still has `<…>` blanks, stop and ask. Never invent the design. Otherwise copy the patterns the
  notebook already uses before you reach for anything new.

## Where code goes

- One new cell, directly above the `# 🔍 Verify` cell, unless the brief names other cells.
- Never edit, delete or weaken a Verify cell, a `> ✅ **Checkpoint**` line or anything in `solutions/`. If a
  check looks wrong, say so and stop.
- Add only the objects the brief names: no helpers, classes, factories, modules, files or dependencies.
- Write files only under `data/`. Edit `.ipynb` with a notebook-aware tool (NotebookEdit or `nbformat`).

## Pydantic AI v2 rules

- `await agent.run(...)`. Never `run_sync`, `evaluate_sync`, `asyncio`, `nest_asyncio` or `async with agent:`.
- A function that awaits a run is `async def`; every other tool, validator, hook, filter and evaluator is `def`.
- `result.output`, never `.data`. `result.usage` is a property, not a call. Use `instructions=`.
- Live cells build on `MODEL`. In a keyless notebook (00, 08, 09, 10, 12, 13, 14), build on `TestModel()` or
  `FunctionModel` as the notebook does; only a cell guarded by `LIVE` uses `MODEL`. Never type or invent a
  model-name string. Keyless notebooks stay keyless.
- Per-run things (user, role, log, a sync `httpx.Client` for HTTP) go in deps, read with `ctx.deps`. No globals.
- A tool that runs another agent forwards `usage=ctx.usage, usage_limits=ctx.usage_limits` (and `deps=ctx.deps`).
- To store a conversation, store `result.new_messages()`.
- Hard rules go in code (output type, validator, `.filtered`, `Hooks`, `requires_approval`, `UsageLimits`),
  never only in instructions.
- MCP is `MCPToolset`; trimming history is `capabilities=[ProcessHistory(...)]`. Write `RunContext` the way the
  notebook does (`RunContext[YourDeps]` or plain `RunContext`), never `RunContext[None]`.
- `setup()` already wires Logfire. Never add `logfire.configure()` or `instrument=`. SQL uses `?` placeholders.

## Check your work

Run the three checks in [CONTRIBUTING.md](CONTRIBUTING.md#checks-before-a-pr) (ruff, `scripts/check_notebooks.py`,
`uv run pytest notebooks/NN_name.ipynb`) and report what each printed. Done means pytest passes **and** every
object the Verify cell names exists: a Verify cell prints ⏳ and still passes while one is missing. A live
notebook spends the learner's key: `MODEL=test uv run pytest …` runs it on a free fake (02 still needs a key).

## Safety

- Never read or print `.env`.
- The committed hook `.claude/hooks/guard_git.py` blocks force-pushes, pushes to `main` and admin merges.
  Auto-merge is fine: a ruleset makes `main` wait for green CI. Never edit hooks or settings to get past it; tell the learner. On their own fork, the learner can set
  `{"disableAllHooks": true}` in `.claude/settings.local.json`. That turns off every hook in this project
  (project hooks and their own user hooks, plus a custom status line); managed hooks stay on.

Course authors also follow [CONTRIBUTING.md](CONTRIBUTING.md).

## Full-stack track (`app/`, `migrations/`, `track/`)

Acme Desk: Postgres 18 in Docker, Alembic, sync SQLAlchemy 2 + psycopg 3, FastAPI, a Pydantic AI desk agent
with human approval, Logfire, Playwright. The plan is `SPEC.md` and `specs/`; `specs/contract.md` fixes the
shared signatures, file owners and the episode format.

- Do one spec and touch only the files it lists. Never change a signature in `contract.md`; if one must
  change, stop and say so. The v2 rules above still apply to every Pydantic AI line you write here.
- Look up each FastAPI, SQLAlchemy, Alembic, psycopg, Logfire, Pydantic AI and Playwright API in Context7, then
  confirm the installed signature: `uv run --group app python -c "import inspect, X; print(inspect.signature(X.f))"`.
- `app/__init__.py` is where `setup()` runs, once. Never call `logfire.configure()` yourself.
  Agents run on `AGENT_MODEL`, which is `"test"` without a key. No test makes a live model call.
- Routes that touch the database are plain `def` and take `SessionDep`. A route that runs an agent is
  `async def` and never holds a database session across an `await`. SQL uses bound parameters, never an f-string.
- A schema change is a new Alembic revision (`uv run --group app alembic revision --autogenerate -m "..."`).
  Read it before you run it. Never edit a revision that is already on `main`.
- `X-Demo-User` is a labelled fake login. A customer asking for another customer's row gets 404, not 403.
  Page code sets text with `textContent`, never `innerHTML`.
- Start Postgres with `docker compose up -d --wait`, then `uv run --group app pytest app/tests`. The tests use a
  throwaway `acme_test` database (sessions sharing one Postgres set `ACME_TEST_DB=acme_NN_test`); never point one at `acme`. Never edit a `test_epNN_*.py` that another spec
  owns. Use `uv sync --group app`: a bare `uv sync` removes the app packages.
- The Check is the one line in `SPEC.md`. Run it before you commit.
