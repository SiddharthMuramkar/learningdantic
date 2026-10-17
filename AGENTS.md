# AGENTS.md

A beginner course in Jupyter notebooks on Pydantic AI 2.57 and Logfire 5.2. The learner owns the design, you
write the code, and a `# 🔍 Verify` cell checks it.

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
- The committed hook `.claude/hooks/guard_git.py` blocks force-pushes, pushes to `main` and admin/auto merges.
  Never edit hooks or settings to get past it; tell the learner. On their own fork, the learner can set
  `{"disableAllHooks": true}` in `.claude/settings.local.json`. That turns off every hook in this project
  (project hooks and their own user hooks, plus a custom status line); managed hooks stay on.

Course authors also follow [CONTRIBUTING.md](CONTRIBUTING.md).
