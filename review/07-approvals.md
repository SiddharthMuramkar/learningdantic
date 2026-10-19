# Review: 07 approvals

Branch `07-approvals` (PR #13, merged) plus `07-approvals-followup` (this note and the spec ticks). All Done-when
lines are ticked and `Status` is `done`.

Order of events: when I opened PR #13, specs 03 and 04 were not on main, so I first proved the locked test on a
throwaway local branch that merged `origin/04-agent` and `origin/03-api` into mine (rows marked "throwaway" below).
PR #13 then squash-merged before my last commit reached it, and 03 and 04 landed on main. I re-ran the Check on
`origin/main` plus this note: ruff and format clean, `check_notebooks.py` 0 problems, `pytest app/tests
--ignore=app/tests/e2e` **30 passed**, including all 5 tests in `test_ep08_approvals.py`. For a short time `main`
had the 07 tests without 03/04, so the `fullstack` job was red on #13 (not a required check).

## What I built
- `app/approvals.py`
  - `record_pending(ticket_id, requests)`: one `refunds` row per approval, status `pending`. The amount comes from
    the `orders` row, never from the model's arguments. Select-or-insert on (ticket_id, tool_call_id), so calling it
    twice returns the same row. Returns the first `ApprovalOut`. An order that does not exist gets no row and no card.
  - `execute_refund(ticket_id, tool_call_id)`: `UPDATE refunds SET status='executed' WHERE ticket_id AND
    tool_call_id AND status='approved' RETURNING order_id, amount_cents`. No row back raises `RuntimeError`.
- `app/routes/approvals.py`: `POST /tickets/{ticket_id}/approvals/{refund_id}` (async def, `StaffDep`).
  1. Loads the stored conversation and takes the waiting call ids from its `deferred_tool_requests`.
  2. One guarded `UPDATE ... WHERE id, ticket_id, status='pending' RETURNING tool_call_id`. If that call id is not
     among the waiting ones it raises 409 inside the transaction, so the UPDATE rolls back.
  3. Other pending refunds on the ticket are set to `rejected` (see Guesses).
  4. Resumes with `run_desk(ticket_id, user, None, deferred_tool_results=requests.build_results(approvals=answers))`:
     `True` for the approved call, `ToolDenied` for everything else. Nothing from the request body reaches the
     results except `approve` or `reject`.
  5. `VersionConflict` gives 409. A second `DeferredToolRequests` in the reply is stored and returned as `approval`.
- `app/static/approvals.js`: `window.showApproval(ticketId, approval)` draws `div[data-testid=approval-card]` with
  Approve and Reject buttons, all text through `textContent`. A click POSTs `{decision}` with the `#user` value as
  `X-Demo-User`, appends an `assistant-message` line (or `Error <status>`), and draws a new card if the reply has
  another approval.
- `app/tests/test_ep08_approvals.py`: 5 tests (waits, approve once, reject, ada 403, other ticket 409). A
  `FunctionModel` asks for `issue_refund(order_id=1042)` once, then answers; it is set with
  `monkeypatch.setattr(agents.desk, "model", ...)` because `Agent.override` is a ContextVar and does not reach the
  thread TestClient runs the app in.
- `track/08-approvals/EPISODE.md` (64 lines) in the contract format. Your piece: `execute_refund`.

## What I ran
| Command | Result |
|---|---|
| `git fetch origin && git log origin/main` | 01 (`ddfbfae`, then `4e00962` the follow-up) on main; later 05 and 02. Not 03, not 04 |
| `uv run python -c "import inspect ..."` on `DeferredToolRequests`, `DeferredToolResults`, `build_results`, `ToolDenied`, `Agent.run`, `Conversation`, `ToolCallPart` | read; see Sources |
| scratch script on a toy agent (not committed) | partial `build_results` raises `UserError: Tool call results need to be provided for all deferred tool calls`; `ToolDenied` shows as `outcome='denied'` in the tool return; `Agent.model` can be assigned; TestModel gives `order_id=0` unless the field has `Field(examples=[...])` |
| `uv sync --group app` | ok |
| `uv run ruff check . && uv run ruff format --check .` | All checks passed, 75 files formatted |
| `uv run python scripts/check_notebooks.py` | checked 29 notebooks, 0 problems |
| `ACME_TEST_DB=acme_07_test pytest` on a scratch copy of the route tests with stand-ins for 03/04 (own `Agent`, in-memory `memory.load`, `run_desk` patched in the route module, tickets inserted directly) | 7 passed, before and after merging origin/main |
| (throwaway) same, with `execute_refund` body replaced by `raise NotImplementedError` | `test_approve_once` red, 6 passed; restored, file identical |
| (throwaway) same, with both locks removed (the guard and the `if call_id not in answers` check) | 2 red (`AttributeError: 'NoneType' object has no attribute 'build_results'`, and a `ValueError` for call id `None`); restored |
| (throwaway) same, with only the `UPDATE` guard removed | still 7 passed (the `if` refuses and rolls back); the episode says so |
| `uvicorn app.main:app --port 8707` on a database of my own, built-in browser | `showApproval(1, {...})` drew `Refund $12.00 for order 1042?` with Approve and Reject; clicking Approve showed `Error 409` and re-enabled the buttons |
| `pytest app/tests --ignore=app/tests/e2e` with the scratch file copied in, after merging main | 14 passed (ep01, ep02, ep05, 7 scratch), 5 errors: `test_ep08_approvals.py` fails in its fixture with `AttributeError` because `app.agents` has no `desk` yet |
| (throwaway) branch = mine + `origin/04-agent` + `origin/03-api`: `pytest app/tests/test_ep08_approvals.py -v` | 5 passed (real `desk`, real chat and ticket routes) |
| (throwaway) same, `execute_refund` blanked | `test_approve_executes_exactly_once` red (`NotImplementedError`), 4 passed; restored |
| (throwaway) same, both locks removed | 2 red (`AttributeError: 'NoneType' ... 'build_results'`, `ValueError ... tool call IDs not in ... [None]`); restored |
| (throwaway) same, only the `UPDATE` guard removed | 5 passed, as the episode says |
| (throwaway) same, keyless demo flow with no fake model (sam, "Please refund order 1042", then approve) | first reply has `approval {refund_id 1, order_id 1042, amount_cents 1200}`, approve answers 200 with `category billing` |
| (throwaway) same, `ruff check`, `ruff format --check`, `check_notebooks.py`, `pytest app/tests --ignore=app/tests/e2e` | all clean, 30 passed |
| `/code-review` (high) and `/security-review` | code review: 8 findings, 2 fixed, 5 skipped, 1 no change; security review: none |

## What failed or never ran
- The step-by-step run in `EPISODE.md` (page in a browser, psql, curl) was not run end to end. Its pieces were: the card
  drawn and clicked in the built-in browser (409 shown), and the keyless flow through the API.
- The live check (one staff refund chat on the real MODEL) was not run: I did not call a paid model.

## Guesses
- Confirmed on 04's branch: `issue_refund` has `Field(examples=[1042])` (without it TestModel sends order 0 and the
  keyless demo shows no card) and calls `approvals.execute_refund(ctx.deps.ticket_id, ctx.tool_call_id)`.
- Confirmed: 03 lets sam `POST /tickets`, 04 lets him chat on his own ticket, and `run_desk` saves the conversation
  with its `deferred_tool_requests`, so `memory.load` returns them. The 03/04 branches may still change before they merge.
- A resumed run needs an answer for every waiting call, so I reject the other pending refunds on the ticket at the
  same time (they are denied in the run anyway). `ApprovalOut` can only show one card.
- Every missing, wrong-ticket or already-decided refund is 409 (not 404), as the spec says.

## Known shortcuts (all marked in the code)
- If the resumed run fails after the UPDATE (`VersionConflict`, a model error), the refund stays approved/rejected. There is no retry path.
- A concurrent duplicate `record_pending` can hit the unique constraint and answer 500.
- `execute_refund` commits in its own transaction. If `run_desk` fails to save afterwards, the refund is `executed`
  but the stored conversation still lists the call as waiting.
- Sync DB calls sit inside an `async def` route, as the contract asks. Sessions never span an `await`.
- `approvals.js` does not catch a network error from `fetch`.

## Environment note
`conftest.py` first used a fixed `acme_test` (or `ACME_TEST_DB`); I used `ACME_TEST_DB=acme_07_test` until I merged
PR #7, which derives `acme_<sha1>_test` per checkout. I dropped `acme_07_test` at the end.

## Sources
- Context7 `/pydantic/pydantic-ai` (docs/deferred-tools.md: `DeferredToolRequests`, `build_results`, `ToolDenied`, `ConversationTypeAdapter`, resuming with `conversation=` and `deferred_tool_results=`).
- Context7 `/websites/sqlalchemy_en_20_orm` (ORM `update().where().values().returning()`, `Session.begin()` as a context manager).
- Context7 `/websites/fastapi_tiangolo` (`APIRouter`, `HTTPException` in an `async def` route).
- Installed signatures, checked with `inspect.signature` on pydantic_ai 2.57.0: `DeferredToolRequests(calls, approvals, metadata)`,
  `DeferredToolResults`, `DeferredToolRequests.build_results(*, approvals, calls, metadata, approve_all)`, `ToolDenied(message)`,
  `Agent.run(..., conversation=, deferred_tool_results=, deps=, usage_limits=)`, `Conversation(messages, usage, conversation_id, deferred_tool_requests)`.
  I did not run `inspect` on the SQLAlchemy and FastAPI calls; the tests above exercise them.
- specs/contract.md, specs/07-approvals.md, specs/04-agent.md, specs/05-page.md.
