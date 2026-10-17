"""Shared setup for the learningdantic notebooks.

Every notebook starts with::

    from learningdantic import setup
    MODEL = setup()

``setup()`` only hides plumbing (``.env`` loading and Logfire wiring). Everything the course teaches
is imported straight from ``pydantic_ai`` and ``logfire`` in the notebooks themselves.
"""

import os
from pathlib import Path

import logfire
from dotenv import find_dotenv, load_dotenv

__version__ = "0.1.0"

# The one place the course's default model is written down. Override it with MODEL=... in .env.
DEFAULT_MODEL = "openai:gpt-6-luna"


def setup() -> str:
    """Load .env, wire up Logfire, and return the model string the notebooks should use."""
    env_file = find_dotenv(usecwd=True)  # walks up from notebooks/ to the repo root
    load_dotenv(env_file)  # no override: a MODEL=... set in your shell wins over .env
    # Notebooks run inside notebooks/, but `logfire projects new` saves credentials next to .env.
    root = Path(env_file).parent if env_file else Path.cwd()
    os.environ.setdefault("LOGFIRE_CREDENTIALS_DIR", str(root / ".logfire"))
    # Traces ship only when a Logfire token exists; without one, this is a silent no-op.
    # distributed_tracing: an in-process MCP server (notebook 09) joins the trace quietly.
    logfire.configure(send_to_logfire="if-token-present", console=False, distributed_tracing=True)
    logfire.instrument_pydantic_ai()

    model = os.getenv("MODEL", DEFAULT_MODEL)
    print(f"✅ ready: MODEL = {model}")
    return model
