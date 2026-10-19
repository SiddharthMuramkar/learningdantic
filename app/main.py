"""The web app. Run it: uv run --group app uvicorn app.main:app"""

from pathlib import Path

import logfire
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import approvals, chat, tickets

app = FastAPI(title="Acme Desk")
logfire.instrument_fastapi(app)  # a no-op unless Logfire has a token (see setup())

app.include_router(tickets.router)
app.include_router(chat.router)
app.include_router(approvals.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Last, so it only answers what no route above claimed: "/" serves the page.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
