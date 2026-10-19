# Review: 03 api

Branch `03-api`, built from `specs-base`, then merged with `origin/main` after 01 (#6), 01's follow-up (#7), 05 (#8) and 02 (#9) landed.

## What I built
- **`app/routes/tickets.py`** (replaces 01's 501 stub, same three signatures):
  - `POST /tickets` (201): the ticket's `customer` comes from the logged-in user, never from the body.
  - `GET /tickets/{ticket_id}`: `session.get(Ticket, id)`, then 404 unless the user is staff or owns it.
  - `GET /orders/{order_id}`: same rule on `Order`. This is the learner's piece, so it is written out inline and does not share a helper with `get_ticket`.
  - Plain `def` routes with `SessionDep` and `UserDep`; one 404 message per resource for "missing" and "not yours", so ids don't leak.
  - Decision beyond the spec: `Id = Annotated[int, Path(le=2**31 - 1)]` on both path ids. Without it `GET /tickets/99999999999` reached Postgres, failed the `INTEGER` cast and answered 500 (found in `/code-review`, reproduced with `TestClient`). It now answers 422.
- **`app/tests/test_ep03_fastapi.py`** (locked, 8 tests): every case in the spec's Done-when line, plus: missing ticket 404, bo reads his own order 2077, sam reads any order and gets 404 for a missing one, and the too-big id gives 422.
- **`track/03-fastapi/EPISODE.md`** (72 lines, contract format, 01's house style).

## Commands and results
All from the repo root, in this worktree.

| Command | Result |
|---|---|
| `git switch -c 03-api`, `git branch -D claude/03-api-5fe6f1` | ok |
| `uv run ruff check . && uv run ruff format --check .` before 01 landed | `I001` on `tickets.py`: ruff counted `app` as third-party because `app/__init__.py` and `app/routes/__init__.py` did not exist yet. With 01's files present, it passes with the import order I wrote. |
| Early try: scratch branch `03-api-try` = my files + `origin/01-skeleton` (PR #6 still open), `uv sync --group app --locked`, `pytest app/tests/test_ep03_fastapi.py` | 7 passed. Not the official run; the scratch branch is deleted. |
| Blank `get_order` (`raise NotImplementedError`), run test_ep03, then `git restore` | red (2 failed), green again after restore. Done three times, last on the final merged tree. |
| Break-it from the episode (`get_ticket`'s `if` cut to `if ticket is None:`) | `test_bo_gets_404_and_sam_gets_200_for_adas_ticket` red; restored with `git restore .` |
| `fastapi dev app/main.py --host 127.0.0.1 --port <free>` against my own test database, then `curl` | no header 401; create 201 `{"id":1,"customer":"ada",...}`; empty subject 422; bo on ada's ticket 404; sam 200; ada on order 1042 200; ada on 2077 `{"detail":"Order not found"}` 404; `/tickets/abc` 422; `/docs` 200; `x-demo-user` shows as a header field in `openapi.json`. Server stopped afterwards. |
| `git merge origin/main` (first time) | conflicts in `app/routes/tickets.py` (took mine with `--ours`) and `specs/01-skeleton.md` (took main's). Second merge was clean. |
| `uv run ruff check .`, `uv run ruff format --check .`, `uv run python scripts/check_notebooks.py` on the final tree | all clean (75 files formatted; 29 notebooks, 0 problems) |
| `uv run --group app pytest app/tests` on the final tree | **15 passed** (ep01, ep02, ep03, ep05) |
| `/code-review` (xhigh, in this session) | 6 findings. Fixed: ids above Postgres integer range gave 500; tests missed bo's own order. Skipped: whitespace-only subject accepted (`TicketIn` is 01's file), ownership check written twice (on purpose, see above), extra SELECT after commit (`app/db.py` is 01's), ORM rows returned under a schema return type (matches 01's stub). |
| `/security-review` | no finding at confidence 8 or higher. Checked: bound parameters only, ownership check on both reads, `customer` not taken from the body, uniform 404. |

## What failed or went wrong
- **500 on huge ids** (above): found by review, fixed, tested.
- **A test database of mine disappeared.** Before 01's follow-up (#7) made the name per checkout, I used `acme_03_test` (the example name in 01's conftest comment). It vanished between seeding it and the first request to my dev server, so another session probably used the same example name and dropped it. I switched to `acme_<sha1 of repo root>_test`, which is also what conftest now derives. Lesson for the other specs: don't copy the example name.
- **The Check in this tree ran with the per-checkout database after #7**; before #7 I ran with `ACME_TEST_DB` set, and skipped `test_ep02_alembic.py` then because it used the shared `acme_scratch` name. After #7 I ran everything.

## Never ran or not verified
- Episode steps 1 and 2 (`docker compose up`, `alembic upgrade head`, `docker compose exec db psql ...`) were not run against the shared dev database `acme`. The seed one-liner in step 2 was run, against my own test database. Docker commands were outside what this run allowed.
- The `/docs` "Try it out" click-through in step 4 was not done in a browser; I checked that `openapi.json` lists the `x-demo-user` header and that `/docs` answers 200.
- The `Id` alias is a second concept (`Annotated`, `Path`) in an episode about the first routes. The episode doesn't mention it; if it confuses, drop it and accept the 500 on huge ids.

## Guesses
- `session.commit()` in `create_ticket`: `get_session` does not commit, so the route does. After commit the ticket is reloaded by one extra SELECT when FastAPI builds the response.
- `Id` upper bound `2**31 - 1` because `Mapped[int]` becomes Postgres `INTEGER`.
- The 404 for a staff user on a missing row uses the same message as for a customer.
- Episode "Break it" picks `get_ticket`, not `get_order`, so the learner's piece stays separate from the sabotage.

## Sources
- Context7 `/websites/fastapi_tiangolo`: APIRouter / response_model / HTTPException (`session.get` + 404 pattern), TestClient and validation errors, Path numeric validations (`Path(ge=, le=)`).
- Context7 `/websites/sqlalchemy_en_20_orm`: `select`, `Session.scalars`, commit/flush.
- Installed signatures (`uv run --group app python -c "import inspect ..."`): `sqlalchemy.orm.Session.get(entity, ident, *, options, populate_existing, with_for_update, identity_token, execution_options, bind_arguments)`, `fastapi.Path(default, *, ..., gt, ge, lt, le, ...)` (so `le=` exists), `APIRouter.get(..., status_code=None)`. Versions: fastapi 0.146.0, SQLAlchemy 2.1.5.
- Repo files read: `SPEC.md`, `specs/contract.md`, `specs/03-api.md`, `CONTRIBUTING.md`, `app/db.py`, `app/identity.py`, `app/schemas.py`, `app/models.py`, `app/seed.py`, `app/main.py`, `app/tests/conftest.py`, `track/01-postgres/EPISODE.md`, `track/02-alembic/EPISODE.md`, `review/01-skeleton.md`.
