# Contributing

Thanks for helping. This file is the house style for every notebook in the course. Humans and AI agents
both work from it.

## The idea the course teaches

An agent is **a model + instructions + tools + an output type**. Every lesson is about one of two things:

- **Steer**: what the agent tries to do (instructions, output types, validators, evals).
- **Scope**: what it can see, do, spend and remember (tools, toolsets, deps, guardrails, limits, history).

Each notebook's title line carries one tag: **Steer**, **Scope**, **Both**, or **Tooling** (setup, models,
observability, testing).

## Notebook structure

1. `# NN — Title` + a tag line (`**Steer**` / `**Scope**` / `**Both**` / `**Tooling**`) + "When you finish
   you can…" (3–4 bullets).
2. The setup cell: these two lines, with the blank line ruff adds after the import (checked by `scripts/check_notebooks.py`):
   ```python
   from learningdantic import setup

   MODEL = setup()
   ```
3. Repeat: a short markdown idea → **one** runnable cell → `> ✅ **Checkpoint** — what you should see`.
4. Optional `> 🔭 **In Logfire**` notes (Logfire is optional; nothing may depend on it).
5. `## 🏋️ Exercise`, then a link to `../solutions/NN_name.ipynb`, then `## Next →`.

**Budget**, so a notebook fits 30–45 minutes: at most 12 code cells, at most 5 new APIs, and an exercise with
at most 2 required parts plus one optional stretch. Anything else gets one markdown line and a docs link.

## Rules

- **Pydantic AI v2 only** (2.57+). Use `instructions=`, `result.output` and `result.usage` (a property).
  Model strings carry a prefix (`'openai:…'`). Never hardcode a model name in a checkpoint; use `MODEL`.
- **The one async rule.** "In a notebook, put `await` in front of `agent.run(...)`. If that line sits inside a
  function you wrote, make it `async def` and `await` it when you call it. Everything else you write — tools,
  validators, instructions, hooks, filters, evaluators — can be a plain `def`." That means:
  - No `run_sync`, no `evaluate_sync`, no `import asyncio`, no `async with agent:` and no async HTTP clients
    in code cells (checked by the script).
  - Streaming (`async with agent.run_stream(...)` / `async for`) is the one copy-paste pattern.
- **Plain English.** Short sentences. The first time a Python feature appears (decorator, dataclass, type hint,
  `async with`), explain it in one line.
- **Keyless first.** If a concept can be shown with `TestModel` / `FunctionModel`, show it that way so CI can
  run it. Live cells use `MODEL` and short prompts.
- **Re-runnable cells.** Running any cell twice must work. Build the agent in the same cell that adds its tools
  or instructions.
- **Files.** Write only under `data/` (gitignored). Run `Path("../data").mkdir(exist_ok=True)` first, use a file
  named for your notebook (`data/13_chats.sqlite`), and delete it at the top of the cell.
- **Solutions.** Every exercise has `solutions/NN_name.ipynb`, which starts with the same setup cell and ends in
  plain `assert`s that fail loudly.
- **Proving scope.** To show what the model was allowed to see, print
  `test_model.last_model_request_parameters.function_tools` (or read `info.instructions` in a `FunctionModel`).

## Checks before a PR

```bash
uv run ruff check . && uv run ruff format --check .
uv run python scripts/check_notebooks.py
uv run pytest notebooks/00_setup_and_env_check.ipynb      # any keyless notebook; CI runs the full keyless list
```

Notebooks that need a key run locally with your `.env` (`uv run pytest notebooks/01_first_agent.ipynb`).
Outputs are stripped on commit (`uv run pre-commit run --files <changed files>`).
