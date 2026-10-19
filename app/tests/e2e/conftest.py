"""Browser tests: a real uvicorn server in a second process, a real Chromium in front of it.

The parent conftest already created and migrated the test database and empties it before every test.
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from playwright.sync_api import Page, expect

from app.db import engine

REPO_ROOT = Path(__file__).parents[3]

# Every expect(...) waits up to 10 s for the page to catch up and stops the moment it matches.
TIMEOUT_MS = 10_000
expect.set_options(timeout=TIMEOUT_MS)


def pytest_collection_modifyitems(items):
    """In `pytest app/tests`, run the browser tests last.

    Once Playwright's sync API has started, it marks its event loop as running until the run ends,
    so an `async def` test after it fails with
    "Cannot run the event loop while another loop is running".
    """
    items.sort(key=lambda item: item.path.is_relative_to(Path(__file__).parent))


@pytest.fixture(autouse=True)
def short_waits(page: Page):
    """Clicks and expect_response wait 10 s too (the default is 30): a wrong locator fails fast."""
    page.set_default_timeout(TIMEOUT_MS)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))  # port 0: the OS picks a free one
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def app_url(tmp_path_factory):
    """Start `uvicorn app.main:app` once for the whole run and yield its base URL."""
    assert engine.url.database.endswith("_test"), "the e2e server must use the test database"
    # The server is another process: Agent.override here cannot reach it, so MODEL=test goes in its
    # environment, and it gets the same database the tests empty and read.
    env = {
        **os.environ,
        "MODEL": "test",
        "DATABASE_URL": engine.url.render_as_string(hide_password=False),
    }
    port = free_port()
    url = f"http://127.0.0.1:{port}"
    log_path = tmp_path_factory.mktemp("server") / "uvicorn.log"
    with log_path.open("w") as log:
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=REPO_ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 30
            while True:
                assert server.poll() is None, f"the server exited early:\n{log_path.read_text()}"
                try:
                    if httpx.get(f"{url}/health").is_success:
                        break
                except httpx.TransportError:
                    pass  # not listening yet
                assert time.monotonic() < deadline, (
                    f"/health never answered:\n{log_path.read_text()}"
                )
                time.sleep(0.2)  # a startup wait in a fixture; the tests themselves never sleep
            yield url
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
