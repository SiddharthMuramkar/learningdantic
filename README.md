# learningdantic

**You know some Python. You've never built an AI agent. Start here.**

This is a set of Jupyter notebooks that teach you [Pydantic AI](https://pydantic.dev/docs/ai/) (the agent framework from the Pydantic team) and [Logfire](https://logfire.pydantic.dev) (their observability tool) the only way that actually sticks: by writing and running real code, cell by cell, with an exercise at the end of every notebook.

No videos to sit through, no walls of theory — you build a real agent in the first five minutes of notebook 01, and every concept after that is another runnable cell.

![CI](https://github.com/siddharth-0044/learningdantic/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![uv](https://img.shields.io/badge/uv-managed-de3e77)

## Who this is for

- You can write basic Python (functions, classes, `pip install`)
- You've **never** built an agent, or you've fumbled with one and want to do it properly
- You want to *understand* the framework — not copy a wrapper someone else wrote

## What you need

| Thing | Details | Cost |
|---|---|---|
| An LLM API key | [OpenAI](https://platform.openai.com/) is the default — **or use your ChatGPT/Codex subscription** ([how](https://pydantic.dev/docs/ai/models/openai-codex/)), or [Anthropic](https://console.anthropic.com/) / [Google AI](https://aistudio.google.com/) keys (one line to switch) | A few **cents** per notebook |
| A Logfire account | **Optional.** Everything works without it — [logfire.pydantic.dev](https://logfire.pydantic.dev), free tier is 10M events/month, no card | Free |
| Time | ~30–45 minutes per notebook, at your own pace | — |

If you have *no* API key at all: notebook 00 and notebook 08 run **completely free** using Pydantic AI's built-in test models — you can verify the whole setup works before paying anyone anything.

## Quickstart

**1. Install [uv](https://docs.astral.sh/uv/)** (Python's modern package manager — it manages Python itself, so you don't need to install or worry about versions):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. Clone and set up** (from any folder you keep projects in):

```bash
git clone https://github.com/siddharth-0044/learningdantic.git
cd learningdantic
uv sync                      # installs Python 3.14 + everything else, into .venv/
```

**3. Add your key:**

```bash
cp .env.example .env         # then open .env in any editor and paste your key
```

**4. Start learning:**

```bash
uv run jupyter lab           # opens Jupyter in your browser, correct environment guaranteed
```

Open `notebooks/00_setup_and_env_check.ipynb` and run it top to bottom. That's the whole setup.

> ⚠️ **One thing to know before you Google anything:** Pydantic AI released **v2 in June 2026**, and most blog posts and YouTube tutorials out there were written for the old API. They will show you code that no longer works (`result.data`, `system_prompt=`, bare model names…). These notebooks target v2 only — and they call out the stale patterns when they matter, so you'll recognize them.

## What you'll learn

Work through them in order — each one builds on the last. Every notebook ends with an **exercise**: try it yourself first, then compare against the matching notebook in [`solutions/`](solutions/). (You only cheat yourself by skipping straight to solutions — the struggle *is* the lesson.)

| # | Notebook | When you finish it, you can… |
|---|---|---|
| 00 | [Setup & env check](notebooks/00_setup_and_env_check.ipynb) | Confirm everything works — with zero API keys, zero cost |
| 01 | [First agent](notebooks/01_first_agent.ipynb) | Build and run an agent, and know exactly what a run *cost* you |
| 02 | [Models & providers](notebooks/02_models_and_providers.ipynb) | Switch models/providers, tune settings, survive outages with fallbacks |
| 03 | [Structured outputs](notebooks/03_structured_outputs.ipynb) | Get validated Python objects out of a model instead of fragile text |
| 04 | [Tools](notebooks/04_tools.ipynb) | Give an agent your own functions to call — and make it use them honestly |
| 05 | [Dependencies & DI](notebooks/05_dependencies.ipynb) | Inject per-run state (users, HTTP clients) like a proper backend engineer |
| 06 | [Logfire observability](notebooks/06_logfire_observability.ipynb) | See every tool call, token, retry and dollar in a live trace |
| 07 | [History & streaming](notebooks/07_history_and_streaming.ipynb) | Give agents memory, and stream output as it's generated |
| 08 | [Offline testing](notebooks/08_offline_testing.ipynb) | Test your whole agent with **zero API keys and zero cost** |

After Phase 1 you have every core skill. The roadmap for what comes next lives in [ROADMAP notes below](#whats-next) — multi-agent orchestration, MCP, evals, FastAPI serving, and SQL databases.

## The five asyncio rules (read once, save hours)

Jupyter runs Python's async loop behind every cell, and agents are async. These rules are baked into notebook 00, but here they are for reference:

1. **Top-level `await` just works**: `result = await agent.run('...')`. Never install `nest_asyncio`.
2. **`run_sync()` only at the top level of a cell** — never inside a tool or async function. Nested `run_sync` *silently deadlocks*: your cell just hangs, no error.
3. **Tools and output functions are always `async def`**.
4. **`RuntimeError: Event loop is closed`** → restart the kernel (Kernel → Restart), re-run the setup cell.
5. **A cell that hangs forever** → you broke rule 2. Restart the kernel, fix the code.

## Troubleshooting (the stuff beginners actually hit)

| Symptom | What it means | Fix |
|---|---|---|
| `ModuleNotFoundError: pydantic_ai` | Notebook is running the wrong Python | Restart Jupyter with `uv run jupyter lab` from the repo root. Check with `import sys; sys.executable` — it must end in `learningdantic/.venv/bin/python` |
| A cell hangs forever, no error | `run_sync()` called inside a tool/async function | Kernel → Restart, make the function `async def` + `await` |
| `UserError` mentioning the model name | Old tutorial syntax | v2 needs a prefix: `'openai:gpt-6.1-sol'`, not `'gpt-6.1-sol'` |
| `result.data` doesn't exist | Same — old tutorial | It's `result.output` now; `result.usage` is a property |
| `UserError: Set the OPENAI_API_KEY...` | No key in `.env` | Add it, then re-run the setup cell (it reloads `.env`) |
| Nothing shows in the Logfire UI | Not authenticated | `uv run logfire auth` once, re-run the notebook |

Stuck on something not listed here? [Open an issue](https://github.com/siddharth-0044/learningdantic/issues) — questions are welcome, and they make the repo better for the next person.

## No OpenAI key?

- **Have a ChatGPT/Codex subscription?** Use it directly — no API key needed: set `MODEL=openai-codex:<model>` in `.env` ([docs](https://pydantic.dev/docs/ai/models/openai-codex/))
- **Have an Anthropic or Google key instead?** Set `MODEL=anthropic:claude-...` or `MODEL=google:gemini-...` in `.env` — all provider support is already installed
- **No key at all?** Notebooks 00 and 08 run free (test models). Everything else needs a key

## Running notebooks from the terminal

```bash
uv run pytest                             # executes ALL notebooks top-to-bottom (uses your .env)
uv run pytest notebooks/00_setup_and_env_check.ipynb notebooks/08_offline_testing.ipynb   # the free pair CI runs
```

## What's next

Phase 1 (notebooks 00–08, this repo) is complete. Planned Phase 2: multi-agent orchestration, MCP servers, evals, serving agents with FastAPI, SQLModel databases, and a capstone project. Watch this repo or open an issue if you'd like to nudge the priorities.

## Contributing

Found a typo, a stale API call, or a confusing explanation? PRs are very welcome — this is a learning project for everyone, including its author. Keep the same tone: verified code, honest checkpoints, no hand-waving.

## License

[MIT](LICENSE) — learn from it, fork it, build on it.
