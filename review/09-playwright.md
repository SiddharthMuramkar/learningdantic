# Review: 09 playwright

PR: branch `09-playwright` (built from `specs-base`, then merged with `origin/main` twice). `Status: done` since 03, 04, 05 and 07 landed on main and the four e2e tests passed on this branch (see the last two rows of the table).

## What I built
- `app/tests/e2e/conftest.py`: `app_url` (session fixture) starts `python -m uvicorn app.main:app` in a second process on a free `127.0.0.1` port. Its environment gets `MODEL=test` and the test `DATABASE_URL` taken from `app.db.engine` (the same database `clean_tables` empties). It polls `/health` for up to 30 s, writes the server log to a temp file (shown in the failure message) and stops the server at the end. `expect.set_options(timeout=10_000)`, plus an autouse fixture that sets the page's default timeout to 10 s, so a wrong locator fails in 10 s, not 30 s.
- `app/tests/e2e/test_ep09_playwright.py`, four plain `def` tests, sync API, no sleeps, no networkidle: ada's reply; sam approves (row `pending`, no assistant line, click Approve, row `executed`, reply visible); sam rejects (row `rejected`); `<b>x</b>` shown as text. Every approval test starts a fresh ticket. The database is read from the test process with `select(Refund.status)`.
- `.github/workflows/ci.yml`, `fullstack` job only, three steps appended after "App tests": `playwright install --with-deps chromium`, `pytest app/tests/e2e --tracing retain-on-failure`, upload `test-results/` on failure (`actions/upload-artifact@v7`, checked on github.com: v7.0.2 is the latest). The `ci` job is untouched.
- `track/09-playwright/EPISODE.md` (74 lines, contract format).
- `specs/09-playwright.md`: two Done-when lines ticked.

## Commands and results
| Command | Result |
|---|---|
| `git switch -c 09-playwright`, `git branch -D claude/09-playwright-d8dfda` | ok |
| `uv run ruff check . && uv run ruff format --check .` (before 01 landed, and again at the end) | green at the end; E501 and isort found and fixed on the way |
| `uv run --with`-style installs | not used; I waited for `app` instead |
| `git merge origin/main` (01), then (#7, 05, 02) | clean, except `specs/01-skeleton.md` (add/add): took main's |
| `uv sync --group app` | ok; playwright 1.64.0, pytest-playwright 0.10.0, no `pytest-base-url` (so no `base_url` fixture; mine is called `app_url`) |
| `uv run --group app playwright install chromium` (approved) | ok, Chrome Headless Shell 156.0.8078.4 |
| Probe: `Agent(TestModel())` with `Annotated[int, Field(examples=[1042])]` tools | TestModel passes `order_id=1042` and defers `issue_refund`; that is why the card says order 1042 |
| `pytest app/tests/e2e` on the stubs (only 01 on main) | red as expected: the page did nothing (30 s timeouts), later 501 on `POST /tickets` |
| **Scratch merge** of the local branches `03-api`, `04-agent`, `05-page`, `07-approvals` (their committed work at that time) on a throwaway branch, then `pytest app/tests/e2e` | **4 passed in 3.75 s** |
| Same scratch branch: body of the Reject test replaced by `raise NotImplementedError` | 1 failed, 3 passed; restored, `-k rejects` passes |
| Same scratch branch: `approvals.js` label `Approve` -> `OK`, `--tracing retain-on-failure` | red after 10 s: `waiting for get_by_test_id("approval-card").get_by_role("button", name="Approve")`; `test-results/<folder>/trace.zip` exists; restored with `git restore` |
| Same: `--headed --slowmo 300` | 4 passed in 14 s (a window opened) |
| Same: `ACME_KEEP_TEST_DB=1 ... -k approves --tracing on`, then `psql <test-db> -c "select ... from refunds"` | one row: 1, 1042, 1200, `executed`; matches the episode |
| `playwright show-trace` | not run (it opens a GUI window); the folder name and `trace.zip` path in the episode were checked with `ls` |
| On this branch after the final merge: `pytest app/tests --ignore=app/tests/e2e` | 7 passed |
| On this branch after the second merge (03 and 07 not yet on main): `pytest app/tests/e2e` | 4 failed: `assert 501 == 201` (03's tickets route missing) |
| `scripts/check_notebooks.py` | 29 notebooks, 0 problems |
| `/code-review` (high) | 5 low findings, none fixed (see below) |
| `/security-review` | no findings (test-only code, fixed argv, loopback server, no template input in the workflow) |

| After 03 (#12) landed: `git merge origin/main`, `uv sync --group app` | clean merge |
| `pytest app/tests/e2e` | **4 passed in 3.64 s** |
| The Check: ruff, format, `check_notebooks.py`, `pytest app/tests` | all green; 34 passed (e2e included) |
| `gh pr checks 11` on the first push (03 missing) | `ci` pass; `fullstack` fail with the 501 above; this proved the Chromium install, server start and test steps run on GitHub |

## What failed or never ran
- The first push was red in `fullstack` (501, 03 not on main yet). It is fixed by the merge above; the post-merge `fullstack` run is pending at the time of writing.
- The upload-traces step has not run on GitHub (it only runs on failure and the first failure had no trace files worth checking).
- `playwright show-trace` was not opened (GUI).
- My first test run used `ACME_TEST_DB=acme_09_test` (the old conftest); I dropped that database by name afterwards, and my own `acme_4073cf03_test` the same way. I touched no other session's database.
- I changed no app code. I messaged session 05 once: its draft `index.html` loaded `/static/approvals.js`, but `main.py` mounts the folder at `/`. Its merged page uses the relative paths, so that was resolved.

## Review findings I left (all low)
1. `new_ticket` continues on the response event; the page may not have stored `ticketId` yet. Left, 05's page has an in-flight guard and the fill + click take longer than the gap.
2. `expect(assistant).to_have_count(0)` before Approve assumes the approval reply has no assistant line. True for 05's `message: null`; brittle if 04 changes it.
3. The server log lives in a pytest temp dir, so CI's `test-results/` upload does not include it. A failing test shows the trace but not the uvicorn traceback.
4. `free_port()` can race with another process.
5. The approve and reject bodies repeat; kept so the learner's piece is a clean copy-and-change.

## Guesses
- The e2e conftest relies on the parent conftest's autouse `database` and `clean_tables` fixtures (they ran before each e2e test on the scratch merge).
- Order 1042 on the card: the card text contains `1042` (checked on the scratch merge).
- `-k approves` / `-k rejects` select the right tests by name.
- `--with-deps` (the spec's wording) is right for `ubuntu-latest`; I added `--group app` to the `uv run` lines to match the local commands.

## Sources
- Context7: `/websites/playwright_dev_python` (pytest plugin CLI flags `--headed --slowmo --tracing --output`, `expect.set_options`, `get_by_role`, `get_by_test_id`, `to_have_text`).
- Installed signatures (`inspect.signature`): `playwright.sync_api.Page.expect_response`, `expect.set_options`, `pydantic_ai.models.test.TestModel.__init__`; versions via `importlib.metadata`.
- https://github.com/actions/upload-artifact/releases (latest major v7).
- `review/01-skeleton.md` (format and the per-checkout test database), the shared-notes file from session 02.
