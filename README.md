# learningdantic

**Learn to steer and scope AI agents with [Pydantic AI](https://pydantic.dev/docs/ai/), by running real code.**

This is a course in Jupyter notebooks. You build a real agent in the first five minutes. After that, each idea is
one runnable cell, a checkpoint that tells you what you should see, and an exercise at the end. Logfire, the
Pydantic team's observability tool, is optional.

[![CI](https://github.com/SiddharthMuramkar/learningdantic/actions/workflows/ci.yml/badge.svg)](https://github.com/SiddharthMuramkar/learningdantic/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![uv](https://img.shields.io/badge/uv-managed-de3e77)
![Pydantic AI](https://img.shields.io/badge/pydantic--ai-2.57-e92063)

## The one idea

An agent is **a model + instructions + tools + an output type**. Everything in this course is about two questions:

- **Steer**: *what is it trying to do?* You use instructions, output types, validators and evals.
- **Scope**: *what can it see, do, spend and remember?* You use tools, toolsets, dependencies, guardrails,
  budgets and history.

Every notebook is tagged **Steer**, **Scope**, **Both**, or **Tooling** (setup, models, observability, testing).

## Who this is for

- You can write basic Python: functions, classes, `pip install`. Decorators and dataclasses get a one-line
  explanation the first time they appear.
- You've **never** built an agent, or you have and want to design them properly.
- You don't want to learn asyncio. You won't need to (see [the one async rule](#the-one-async-rule)).

## What you need

| Thing | Details | Cost |
|---|---|---|
| An LLM API key | An [OpenAI](https://platform.openai.com/) key is the default. [Anthropic](https://platform.claude.com/) or [Google AI](https://aistudio.google.com/) keys work too (one line to switch). | **Less than a cent** per notebook on the default model |
| A Logfire account | **Optional.** Everything works without it. The free tier at [logfire.pydantic.dev](https://logfire.pydantic.dev) is 10M spans, logs or metrics a month, no card. | Free |
| Time | ~30–45 minutes per notebook | — |

**No key yet?** Notebooks **00, 08, 09, 10, 12, 13 and 14** run completely free, on Pydantic AI's built-in fake
models (`TestModel`, `FunctionModel`). CI runs exactly that set on every push.

## Quickstart

**1. Install [uv](https://docs.astral.sh/uv/)**, Python's modern package manager. It installs Python itself too:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. Clone and set up:**

```bash
git clone https://github.com/SiddharthMuramkar/learningdantic.git
cd learningdantic
uv sync                      # installs Python 3.14 + everything else into .venv/
```

**3. Add your key:**

```bash
cp .env.example .env         # then open .env and paste your key after OPENAI_API_KEY=
```

**4. Start learning:**

```bash
uv run jupyter lab           # opens Jupyter in your browser, with the right environment
```

Open `notebooks/00_setup_and_env_check.ipynb` and run it top to bottom. Every notebook starts with the same two
lines:

```python
from learningdantic import setup

MODEL = setup()  # loads .env, wires up Logfire (optional), returns your model string
```

## The one async rule

Agents talk to the network, so Pydantic AI is async. In a notebook you only need this:

> **Put `await` in front of `agent.run(...)`.** If that line sits inside a function you wrote, make the function
> `async def` and `await` it when you call it. Everything else you write (tools, validators, instructions, hooks,
> filters, evaluators) can be a plain `def`.

That's it. There's no `asyncio`, no `nest_asyncio` and no `run_sync()` in any notebook. (`run_sync()` is for plain
`.py` scripts; in Jupyter it fails with `This event loop is already running`.)

## What you'll learn

Work through them in order. Notebooks 01–14 end with an **exercise**: try it first, then compare with the matching
notebook in [`solutions/`](solutions/). Every solution ends in `assert`s, so you know it really works.

| # | Notebook | Tag | When you finish it, you can… |
|---|---|---|---|
| 00 | [Setup & env check](notebooks/00_setup_and_env_check.ipynb) | Tooling | Confirm everything works, with zero keys and zero cost |
| 01 | [First agent](notebooks/01_first_agent.ipynb) | Steer | Build and run an agent, and know exactly what a run cost you |
| 02 | [Models & providers](notebooks/02_models_and_providers.ipynb) | Tooling | Switch models and providers, tune reasoning, survive outages with fallbacks |
| 03 | [Structured outputs](notebooks/03_structured_outputs.ipynb) | Steer | Get validated Python objects back, and reject answers that break your rules |
| 04 | [Tools](notebooks/04_tools.ipynb) | Scope | Decide what an agent can *do*, and prove which tools really ran |
| 05 | [Dependencies](notebooks/05_dependencies.ipynb) | Scope | Decide what an agent can *see*, per run, per user |
| 06 | [Logfire observability](notebooks/06_logfire_observability.ipynb) *(optional)* | Tooling | See every tool call, token, retry and dollar in a live trace |
| 07 | [History & streaming](notebooks/07_history_and_streaming.ipynb) | Scope | Decide what an agent *remembers*, and stream answers as they're written |
| 08 | [Offline testing](notebooks/08_offline_testing.ipynb) | Tooling | Test steering and scope with **zero keys and zero cost** |
| 09 | [Toolsets & MCP](notebooks/09_toolsets_and_mcp.ipynb) | Scope | Bundle tools, hide the dangerous ones, and plug in an MCP server |
| 10 | [Capabilities & guardrails](notebooks/10_capabilities_and_guardrails.ipynb) | Both | Package behaviour as capabilities; add hooks, human approval and budgets |
| 11 | [Multi-agent](notebooks/11_multi_agent.ipynb) | Both | Give each agent one job: delegate, route and hand off, on one shared budget |
| 12 | [Evals](notebooks/12_evals.ipynb) | Steer | Prove your steering works with datasets and evaluators, not by feel |
| 13 | [Ship it](notebooks/13_ship_it.ipynb) | Scope | Put an agent behind a chat UI and control what it remembers in a database |
| 14 | [Capstone: support desk](notebooks/14_capstone_support_desk.ipynb) | Both | Design an agent by deciding which knob each rule belongs to, then prove it |

## Coming from an old tutorial?

Pydantic AI hit **v1 in September 2025** and **v2 in June 2026**, and most blog posts and videos predate that.
These notebooks target v2 (2.57) only. Here's what changed:

| Old tutorials say | v2 |
|---|---|
| `result.data` | `result.output` |
| `result.usage()` | `result.usage` (a property) |
| `Agent('gpt-4o')` | needs a provider prefix: `Agent('openai:…')` |
| `system_prompt=` | still works, but `instructions=` is preferred |
| `Agent(instrument=True)` | removed; use `logfire.instrument_pydantic_ai()` (`setup()` does it) |
| `history_processors=[...]` | `capabilities=[ProcessHistory(...)]` (notebook 13) |
| `MCPServerStdio`, `FastMCPToolset` | `MCPToolset` (notebook 09) |
| `nest_asyncio`, `run_sync()` in notebooks | `await agent.run(...)` |

## What it costs

The default model is `openai:gpt-6-luna` ($0.10 per million input tokens, $0.50 per million output tokens). It's set
in one place, `DEFAULT_MODEL` in `src/learningdantic/__init__.py`; put `MODEL=...` in `.env` to override it. A live notebook makes a handful of short calls, so
it costs well under a cent. Every run prints its own bill in `result.usage.cost` (it shows `None` if the
model isn't in the price table yet). Want stronger answers? Put `MODEL=openai:gpt-6.1-sol` in `.env`. It costs about 15× more per call, which is still only a cent or two per notebook.

## Troubleshooting

| Symptom | What it means | Fix |
|---|---|---|
| `ModuleNotFoundError: learningdantic` or `pydantic_ai` | The notebook is running the wrong Python | Start Jupyter with `uv run jupyter lab` from the repo root, or pick the *Python 3 (learningdantic)* kernel |
| `RuntimeError: This event loop is already running` | `run_sync()` was used in a notebook | Use `await agent.run(...)` |
| `UserError: … run_sync() … cannot be used inside a synchronous tool` | A plain `def` function calls another agent | Make that function `async def` and `await other_agent.run(...)` |
| `UserError` mentioning the model name | Old tutorial syntax | Add the prefix: `'openai:…'`, not a bare model name |
| `UserError: Set the OPENAI_API_KEY…` or `OpenAIError: Missing credentials` | No key, or an empty one, in `.env` | Paste the key into `.env`, then **Kernel → Restart** and run the setup cell again |
| `UnexpectedModelBehavior: Exceeded maximum retries` | The model kept failing your validator or tool | Raise the budget, e.g. `Agent(..., retries=3)`, or make the rule clearer |
| Nothing shows in the Logfire UI | No project token | Put a write token in `.env` (`LOGFIRE_TOKEN=…`), or run `uv run logfire auth` then `uv run logfire projects new` from the repo root |

Stuck on something not listed here? [Open an issue](https://github.com/SiddharthMuramkar/learningdantic/issues).
Questions are welcome.

## Other ways to run a model

- **An Anthropic or Google key?** Set `MODEL=anthropic:claude-…` or `MODEL=google:gemini-…` in `.env`, plus that
  provider's key. Support is already installed. (`xai:` needs `uv add "pydantic-ai-slim[xai]"`.)
- **A ChatGPT/Codex subscription instead of an API key?** Install the Codex CLI, run `codex login` once, then set
  `MODEL=openai-codex:<model>` ([docs](https://pydantic.dev/docs/ai/models/openai-codex/)).
- **No key at all?** The free notebooks above still teach most of the course.

## Running notebooks from the terminal

```bash
uv run pytest notebooks/01_first_agent.ipynb          # run one notebook top to bottom (uses your .env)
uv run pytest                                          # run every notebook in notebooks/
```

## Contributing

Found a typo, a stale API call or a confusing explanation? PRs are very welcome. The house style, and the checks a
PR must pass, are in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). Learn from it, fork it, build on it.
