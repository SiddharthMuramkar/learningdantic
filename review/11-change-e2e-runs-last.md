# Review: 11 change e2e runs last

PR: branch `11-change-e2e-runs-last`, cut from `origin/main` at a1ff67c. It changes spec 09, which is done.

## What I built
- `app/tests/e2e/conftest.py`: `pytest_collection_modifyitems` sorts the items so the ones under `app/tests/e2e/`
  run last (a stable sort, so the order within each group stays the same). The pytest docs (Context7) say a
  conftest's hook gets every collected item, not only the ones in its own folder.
- `specs/11-change-e2e-runs-last.md`: the change file, `Status: done`.

## The cause
pytest 9 collects files and folders together in alphabetical order, so `e2e/` runs before `test_ep01..10`.
pytest-playwright's `playwright` fixture is session-scoped (`sync_playwright().start()`). Playwright 1.64 marks its
loop as running in the main thread between sync calls (`asyncio._set_running_loop(loop)` in
`playwright/_impl/_greenlets.py`, "Between sync calls the user code marks the loop as running" in
`sync_api/_context_manager.py`). From then on, anyio's runner for the `pytest.mark.anyio` tests in
`test_ep10_shipping.py` stops in `BaseEventLoop._check_running` with "Cannot run the event loop while another loop
is running". No other test file is async, so only ep10 failed.

## Commands and results
| Command | Result |
|---|---|
| `docker compose up -d --wait` | `acme-desk-db-1` healthy (shared, never taken down) |
| `pytest app/tests` on main a1ff67c | **3 failed, 34 passed**: the three ep10 tests, the error above |
| `pytest app/tests --collect-only -q` after the fix | ep01 ... ep10, then `e2e/test_ep09_playwright.py` last |
| The Check exactly as in SPEC.md (ruff, format, `check_notebooks.py`, `pytest app/tests`) | exit 0: ruff clean, 91 files formatted, 29 notebooks 0 problems, **37 passed** |
| `pytest app/tests/test_ep10_shipping.py` | 3 passed |
| `pytest app/tests/e2e` | 4 passed |
| `pytest app/tests --ignore=app/tests/e2e` (CI's split) | 33 passed |
| `/code-review` (high) | 2 low findings, left as they are (below) |
| `/security-review` | no findings (a test-only hook that sorts tests) |

## Why not the other fixes
- Change SPEC.md's Check to CI's split: the spec rules say never change the Check to get green, and anyone who
  runs `pytest app/tests` would still hit the error. Not done, so Siddharth did not need to approve a SPEC.md edit.
- Async Playwright or pytest-asyncio: a new pattern for the course and a rewrite of 09's tests.
- Clear Playwright's running loop after each e2e test: it relies on Playwright's private `_set_running_loop`.

## Review findings I left (both low)
1. The sort runs after pytest's own reordering, so with `--ff` a failed e2e test still runs last. It only changes
   the order.
2. This fixes the order, not the leak: an `async def` test inside `app/tests/e2e/`, or a plugin that shuffles
   tests (pytest-randomly), would bring the error back. Spec 09 allows sync tests only, and pytest-randomly is not
   a dependency.

## What failed or never ran
- The app's sync-with-main tool refused (the origin it pinned for this repo is an old URL), and the worktree branch
  could not fast-forward to main. I cut a new branch from `origin/main` and deleted the app-made branch (its
  commit 7025bea is on `origin/01-skeleton`).
- CI has not run this branch yet at the time of writing.
