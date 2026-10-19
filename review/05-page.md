# Review: 05 page

Branch `05-page`, PR title "05 page". `Status` in `specs/05-page.md` stays `todo`: the by-hand check
(ada sends a message and sees a reply) needs specs 03 and 04 on main, and neither was there. See "What never ran".

## What I built
- `app/static/index.html`: the six contract ids (`#user` with ada/bo/sam, `#subject`, `#new-ticket`, `#message`,
  `#send`, `#log`), labels, a few lines of CSS, and `approvals.js` then `app.js` as relative `<script src>`.
- `app/static/app.js` (55 lines with comments): `addLine` (the only place text enters the page, `textContent`),
  `post` (one `fetch` with the `X-Demo-User` header and a JSON body, throws `Error <status>`), `newTicket`,
  `sendMessage` (the learner's piece), and `guarded`, which disables the clicked button while a request runs and
  turns a failure into a `div[data-testid=error-message]` line showing the status code. If a reply has an
  `approval` it calls `window.showApproval?.(ticketId, reply.approval)`.
- `app/tests/test_ep05_page.py`: `GET /` has every contract id, the three users, and both scripts, and each script
  URL answers 200; `app.js` has the `.textContent =` assignment and none of `innerHTML`, `outerHTML`,
  `insertAdjacentHTML`.
- `track/05-page/EPISODE.md` (85 lines, contract format).
- Decisions beyond the spec:
  - Two extra line kinds, `system-message` (`Ticket #N: subject`) and `error-message`. The contract names only
    user and assistant lines; keeping errors out of `assistant-message` means a Playwright "sees a reply"
    check cannot pass on an error.
  - No empty assistant line while a refund waits (`message` is null then), so the approval card is the only new line.
  - A new ticket clears the log.
  - `maxlength` 200 and 2000 on the inputs, matching `TicketIn` and `MessageIn`.

## Commands and results
All from the worktree root.

| Command | Result |
|---|---|
| `git switch -c 05-page`, `git branch -D claude/05-page-fd90ef` | ok |
| `uv run ruff check . && uv run ruff format --check .` (before 01 landed) | first run: `SIM300` Yoda comparison in my test, fixed. `ruff format --check` also flagged `specs/contract.md`, which is 01's file; 01 fixed it on main by excluding `specs/`. |
| the same, after merging origin/main | `All checks passed!`, `69 files already formatted` |
| `git merge origin/main` (01) | add/add conflicts in `app/static/app.js` and `index.html` (took mine with `--ours`), `specs/01-skeleton.md` (took main's) |
| `git merge origin/main` (01 follow-up, #7) | clean |
| `uv sync --group app` | ok |
| `uv run python scripts/check_notebooks.py` | `checked 29 notebooks, 0 problem(s)` |
| `uv run --group app pytest app/tests` | `7 passed` (3 ep01, 2 ep02, 2 ep05) on the per-checkout test database |
| `ACME_TEST_DB=acme_05_test uv run --group app pytest app/tests --ignore=app/tests/test_ep02_alembic.py` (before #7, when conftest still used a fixed name) | `5 passed`. I skipped ep02 then because it used the shared `acme_scratch` database. |
| Break it: `line.textContent` -> `line.innerHTML` in app.js, run `test_ep05_page.py` | red (`assert 'innerHTML' not in ...`, 1 failed 1 passed); `git restore` made it green |
| `uv run --group app uvicorn app.main:app` on a free port, `curl` `/`, `/app.js`, `/approvals.js` | 200, 200, 200 (`text/html`, `text/javascript`) |
| same app in the built-in browser: New ticket as ada | log shows `Error 501` (spec 03 stub) in a red line; button re-enabled afterwards; a double click made one request |
| `uv run --group app fastapi dev app/main.py --port <free>` (the episode's step 2 with a free port) | starts, `GET /` 200 |
| `/code-review` (xhigh, local) | 10 findings, 5 fixed, 4 skipped (below), 1 doc fix |
| `/security-review` (local) | no findings at confidence 8 or higher |

A throwaway mock API (stdlib `http.server`, in the session scratchpad, not in the repo) stood in for 03 and 04
before 01 landed. In the built-in browser the page did this against it:
1. `Create a ticket first` shows when Send is clicked with no ticket.
2. An empty subject shows `Error 422`.
3. Ada's ticket shows `Ticket #7: ...`.
4. `<b>hello</b>` shows as literal text in the user line and in the echoed reply, with 0 `<b>` elements in the log.
5. A reply with an `approval` calls `window.showApproval` and adds no empty assistant line.
6. bo on ada's ticket shows `Error 404`.
7. A new ticket clears the log.

## What failed or never ran
- **By hand with the real agent (Done-when line 2)**: never ran. Specs 03 (`POST /tickets`) and 04 (the chat
  route) were not on main, and the stubs answer 501. To do it after both land:
  `docker compose up -d --wait`, `uv run --group app fastapi dev app/main.py`, open `http://127.0.0.1:8000/`,
  ada: New ticket, then Send `Where is order 1042?`; a reply line must appear (keyless TestModel). Then follow
  `track/05-page/EPISODE.md` steps 4 to 6.
- **Not run**: `docker compose up -d --wait` (outside my allowed commands, so the checkpoint wording is copied
  from episode 01); the Chrome DevTools walk-through in step 5 (the tab and pane names `Network`, `Headers`,
  `Payload`, `Response` are from memory); `/episode 05` and `/episode 05 do`.
- **Fixed during the run**: my first guess was that the page's scripts load from `/static/...`; main mounts
  `StaticFiles` at `/`, so they are `app.js` and `approvals.js`. The first CSS had `#log div` beating the
  attribute selectors, so user and error lines were not coloured; found by looking at a screenshot.
- **Review findings I skipped** (all low):
  - A failed send still clears the typed text, which stays visible in the user line above the error.
  - An empty-string `message` shows no line.
  - Changing `#user` keeps the old ticket and log.
  - Enter does not send, since the inputs are not in a form.
- `test_ep05_page.py` needs Postgres only because conftest's autouse fixtures create the test database; the page
  itself does not use it.

## Guesses
- Step 6 of the episode says bo gets `Error 404` on ada's ticket. That follows the AGENTS.md rule (a customer
  asking for another customer's row gets 404) and spec 04's "customer sees own tickets only", but the chat
  route had not landed. If 04 answers differently, change the checkpoint.
- Step 4 of the episode says the reply "looks odd" in demo mode; it describes `TestModel` output, which I did not
  see through the real route.
- Spec 07 (not landed) will draw the approval card and the reply after a decision itself; `app.js` exposes
  nothing for it beyond `window.showApproval` being called. If 07 needs `addLine`, a function declaration in a
  classic script is already global.
- Spec 09's tests: I assumed they find lines by `data-testid` and buttons by id.

## Sources
- Context7: not used. This spec has no `pydantic_ai`, `fastapi`, `sqlalchemy` or `logfire` call; the Python test
  uses only the standard library (`html.parser`, `pathlib`, `urllib.parse`) and the `client` fixture from 01's
  conftest. The browser APIs (`fetch`, `dataset`, `replaceChildren`, `?.()`) are from memory and were exercised
  in the built-in browser pane instead of checked in docs.
- No installed signatures checked, because no library function is called.
- Read in the repo: `SPEC.md`, `specs/contract.md`, `specs/01` to `04`, `07`, `09`, `10`, `AGENTS.md`,
  `CONTRIBUTING.md`, `app/main.py`, `app/tests/conftest.py`, `app/routes/chat.py`, `track/01-postgres/EPISODE.md`,
  `review/01-skeleton.md`.
