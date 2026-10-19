# Acme Desk: the learningdantic full-stack track

**Goal:** A beginner can read, run and redo, one episode at a time, a working support-desk web app
(Postgres, Alembic, FastAPI, a Pydantic AI desk with human approval, Logfire, Playwright) that coding
agents built.

**Out of scope:**
- MySQL, async SQLAlchemy, streaming replies, a JavaScript framework
- Real login: the `X-Demo-User` header is a labelled fake
- Durable execution (DBOS, Temporal), pydantic-graph, the Harness
- Changing `notebooks/`, `solutions/` or `docs/`

**Check:** `uv run ruff check . && uv run ruff format --check . && uv run python scripts/check_notebooks.py && uv run --group app pytest app/tests`
(start Postgres first: `docker compose up -d --wait`)

Every spec follows [specs/contract.md](specs/contract.md): the shared signatures, file owners and episode format.

## Later
- Streaming replies (POST + a fetch stream reader)
- A durable-execution page (DBOS on the same Postgres)
- Review dojo, flashcards, teach-back
- Logfire browser SDK; Playwright Test Agents and MCP
