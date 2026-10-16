# learningdantic

**Learn [Pydantic AI v2](https://pydantic.dev/docs/ai/) + [Logfire](https://pydantic.dev/logfire) by building, not by reading.**

A set of hands-on Jupyter notebooks that teach you the *real* framework API — no wrappers, no hidden magic. You run every cell yourself, hit every error yourself, and watch every agent run light up in [Logfire](https://logfire.pydantic.dev)'s observability UI. Later phases extend to agent orchestration, MCP, evals, FastAPI serving, and SQLModel databases.

![CI](https://github.com/siddharth-0044/learningdantic/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![uv](https://img.shields.io/badge/uv-managed-de3e77)

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — fast Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- An LLM API key (default: [OpenAI](https://platform.openai.com/) — or use your ChatGPT/Codex subscription, see [openai-codex](https://pydantic.dev/docs/ai/models/openai-codex/))
- *Optional*: a free [Logfire](https://logfire.pydantic.dev) account — 10M spans/month, no credit card

## Quickstart

```bash
git clone https://github.com/siddharth-0044/learningdantic.git
cd learningdantic

uv sync                      # one command: Python 3.14 + .venv + every dependency
cp .env.example .env         # then edit .env: set OPENAI_API_KEY=...

uv run logfire auth          # OPTIONAL: browser login → traces appear in logfire.pydantic.dev
uv run jupyter lab           # Jupyter runs inside the project venv — no kernel setup
```

Open `notebooks/00_setup_and_env_check.ipynb` and run every cell top to bottom. That's it.

> **Heads-up — version drift.** Pydantic AI hit **v2 in June 2026**. Almost every blog post and YouTube tutorial made before that uses APIs that no longer exist (`result.data`, `system_prompt=`, `Agent(instrument=True)`, bare model names…). These notebooks target **v2 only** and flag the stale patterns along the way, so you learn both the new API and why old snippets break.

## The curriculum

### Phase 1 — Pydantic AI + Logfire core ✅

| # | Notebook | You will learn |
|---|----------|----------------|
| 00 | [Setup & env check](notebooks/00_setup_and_env_check.ipynb) | `.env` loading, token-optional Logfire, the asyncio ground rules, a **keyless** TestModel smoke run |
| 01 | [First agent](notebooks/01_first_agent.ipynb) | `Agent(instructions=...)`, `await run()`, `result.output`, `result.usage` (a *property* in v2), `all_messages()` |
| 02 | [Models & providers](notebooks/02_models_and_providers.ipynb) | v2 model-string grammar (`openai:` = Responses API), per-run model settings, `FallbackModel`, cost comparison |
| 03 | [Structured outputs](notebooks/03_structured_outputs.ipynb) | `output_type=BaseModel`, union outputs, `output_validator` + `ModelRetry` |
| 04 | [Tools](notebooks/04_tools.ipynb) | `@agent.tool` vs `@agent.tool_plain`, `RunContext`, docstring→schema, `ModelRetry` from inside tools |
| 05 | [Dependencies & DI](notebooks/05_dependencies.ipynb) | `deps_type` / `deps=` / `ctx.deps`, dynamic `@agent.instructions`, why DI matters |
| 06 | [Logfire observability](notebooks/06_logfire_observability.ipynb) | reading traces, custom `logfire.span`, agent `name=`, cost badges, finding retries in the UI |
| 07 | [History & streaming](notebooks/07_history_and_streaming.ipynb) | `message_history`, serializing conversations, `run_stream` + `stream_output` |
| 08 | [Offline testing](notebooks/08_offline_testing.ipynb) | `TestModel`, `FunctionModel`, `capture_run_messages`, `ALLOW_MODEL_REQUESTS` — develop with **zero API keys** |

Each notebook ends with an **exercise** — try it yourself first, then compare with the matching notebook in [`solutions/`](solutions/).

### Phase 2 — Orchestration & production 🗓️ (roadmap)

| # | Topic | Highlights |
|---|-------|-----------|
| 09 | Toolsets & MCP | `FunctionToolset`, `MCPToolset` / `MCP` capability, a local FastMCP server |
| 10 | Multi-agent orchestration | agent delegation (`usage=ctx.usage`), programmatic hand-offs, output-function routers, parallelism, `pydantic-graph` |
| 11 | Evals | `pydantic-evals` datasets, `LLMJudge`, experiments in the Logfire UI |
| 12 | Serving with FastAPI | build agent once, lifespan state, SSE streaming, `logfire.instrument_fastapi(app)` |
| 13 | Database-backed agents | SQLModel + SQLite (FastAPI's official SQL stack), the validated text-to-SQL pattern |
| 14 | Capstone | support assistant: FastAPI + SQLite persistence + multi-agent + full Logfire tracing + offline test suite |

## The asyncio ground rules (baked into notebook 00)

Jupyter notebooks run an asyncio event loop, and agents are async. Five rules keep you out of trouble:

1. **Top-level `await` just works** in modern Jupyter: `result = await agent.run('...')`. No `nest_asyncio`, ever (that's for legacy setups/Colab).
2. **`run_sync()` only at the top level** of a notebook cell. Never inside a tool, an output function, or another async function — sync code runs on worker threads and nested `run_sync` **deadlocks silently** (sometimes "works" once first, then hangs forever).
3. **Tools and output functions are always `async def`.** If they delegate to another agent: `await other_agent.run(...)`.
4. **`RuntimeError: Event loop is closed`** → restart the kernel and recreate your agent/model. Don't reuse a model across a dead loop.
5. **Logfire is configured once per kernel** (`logfire.configure()` before any `instrument_*()` call) — re-running the setup cell after a kernel restart is fine and expected.

## Running the notebooks

```bash
uv run jupyter lab          # start Jupyter (uses the project .venv automatically)
uv run pytest               # executes ALL notebooks top-to-bottom (needs your .env keys)
uv run pytest notebooks/00_setup_and_env_check.ipynb notebooks/08_offline_testing.ipynb   # keyless subset (what CI runs)
```

CI (GitHub Actions) runs ruff + the two **keyless** notebooks on every push — no secrets needed, thanks to `TestModel`.

## Troubleshooting

| Symptom | Cause & fix |
|---|---|
| `ModuleNotFoundError: pydantic_ai` | Wrong kernel. In the notebook run `import sys; sys.executable` — it must end in `learningdantic/.venv/bin/python`. Restart Jupyter via `uv run jupyter lab` from the repo root. |
| Cell hangs forever | You called `run_sync()` inside a tool or async function → silent deadlock. Use `async def` + `await agent.run(...)`. Restart the kernel to clear it. |
| `RuntimeError: Event loop is closed` | A previous loop died with your model's connection pool. Restart kernel, recreate the agent. |
| Nothing shows in the Logfire UI | Did you run `uv run logfire auth`? Check `.logfire/` exists; check `LOGFIRE_TOKEN` if you use one. |
| `UserError` on model name | v2 requires prefixed model strings: `'openai:gpt-6.1-sol'`, not `'gpt-6.1-sol'`. |
| `result.data` doesn't exist | You found an old tutorial. v2 is `result.output`; `result.usage` is a property. |

## Why Jupyter and not marimo?

[marimo](https://docs.marimo.io/) (reactive, git-friendly `.py` notebooks) is genuinely interesting — but reactive auto-rerun is the wrong default when *every cell costs LLM tokens*, and the ecosystem for agent dev is still `.ipynb`. Revisit later.

## Further reading (v2-current, verified Oct 2026)

- [Pydantic AI docs](https://pydantic.dev/docs/ai/) — start with [agents](https://pydantic.dev/docs/ai/core-concepts/agent/), [output](https://pydantic.dev/docs/ai/core-concepts/output/), [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/), [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/)
- [Testing guide](https://pydantic.dev/docs/ai/guides/testing/) · [Multi-agent guide](https://pydantic.dev/docs/ai/guides/multi-agent-applications/)
- [Logfire docs](https://pydantic.dev/docs/logfire/) · [Pydantic AI ↔ Logfire integration](https://pydantic.dev/docs/ai/integrations/logfire/)
- Official examples (bank support, chat app with FastAPI, SQL generation, flight booking): [pydantic.dev/docs/ai/examples/](https://pydantic.dev/docs/ai/examples/)

## License

[MIT](LICENSE)
