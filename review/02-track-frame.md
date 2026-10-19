# Review note: 02 track frame

Status: the spec stays `todo`. The second Done-when line ("every command runs as written") is not fully true,
see "Never ran".

## What I built

- `track/README.md` (episode 00): the orchestration idea in 5 sentences, the map of the app (diagram plus a
  table of where each box lives), "Before episode 1" (tabs and Ctrl+C, git, Docker wait loop, `uv sync --group app`,
  HTTP codes, reading a pytest test, `?` vs `:name`), a start/stop/wipe card with 5 common errors, the episode
  list 01-11 and how an episode works.
- `.claude/skills/episode/SKILL.md`: `/episode NN` (tour) and `/episode NN do` (your piece), with preflight, the
  ledger in `data/ledger.md`, and the finish. `disable-model-invocation: true`, so only the learner starts it.
- Nothing else. No app code, no tests, no `contract.md` change. I did not run `/code-review` or `/security-review`
  (Markdown only, as the spec says).

## Commands I ran, and what they printed

Two passes. Pass 1 ran on main at `ddfbfae` (PR 6), whose conftest used the fixed test database `acme_test` unless
`ACME_TEST_DB` was set, so I set `ACME_TEST_DB=acme_02_test` (the commands below show it). Then main moved to `4e00962`
(PR 7: a per-checkout test database `acme_<hash>_test`, dropped at the end). I merged that and ran the Check and the
README's pytest line again, with no env prefix: the "Pass 2" rows at the end of the table.

| Command | Result |
|---|---|
| `git fetch origin && git log origin/main` | `ddfbfae 01 skeleton (#6)` on top |
| `git merge origin/main` | one add/add conflict in `specs/01-skeleton.md`; took main's (`--theirs`). After the merge my branch differs from `origin/main` by my two files only |
| `uv run ruff check .` | All checks passed |
| `uv run ruff format --check .` | 68 files already formatted (see "Failed" for the earlier red run) |
| `uv run python scripts/check_notebooks.py` | checked 29 notebooks, 0 problem(s) |
| `uv sync --group app` | ok, app packages import |
| bare `uv sync` (scratch worktree of the 01 branch) | `Uninstalled 31 packages`, then `ModuleNotFoundError: No module named 'fastapi'`. `uv run --group app` installs them back. README claim holds |
| `docker compose up -d --wait` | `Container acme-desk-db-1 Healthy`, container uptime unbroken (config hash matched the running container first, so no recreate) |
| `ACME_TEST_DB=acme_02_test uv run --group app pytest app/tests/test_ep01_postgres.py -x -s` | 3 passed |
| `ACME_TEST_DB=acme_02_test uv run --group app pytest app/tests` (the SPEC.md Check's last part) | 5 passed |
| `DATABASE_URL=…/acme_02_test uv run --group app alembic upgrade head` and `alembic current` | `0001 (head)` |
| README's `text("… WHERE id = :id")` snippet on `acme_02_test` | `(1042, 'ada', '1 blue mug', 'delivered', 1200)` |
| `uv run --group app fastapi dev app/main.py` (default port) | `Server started at http://127.0.0.1:8000`, then `ERROR: [Errno 48] Address already in use` (see Findings) |
| same with `--port 61458` | `/health` gives `{"status":"ok"}`, `/` gives 200 with the page, `POST /tickets` gives 501 (stub) |
| second `fastapi dev` on the same port | `[Errno 48] Address already in use` (the README row, verbatim) |
| `docker run --rm --pull never -p 127.0.0.1:5432:5432 postgres:18 true` (throwaway, never started) | `Bind for 127.0.0.1:5432 failed: port is already allocated` (the README row, verbatim). No container was left behind |
| `psycopg.connect(…:5999…)` | `psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 5999 failed: … Connection refused` |
| `docker -H unix:///tmp/nope.sock ps` | `failed to connect to the docker API at unix:///…` (the first README row) |
| `until docker info >/dev/null 2>&1; do sleep 2; done` and the skill's bounded `for i in $(seq 60)` loop | both returned at once (Docker was up) |
| `docker compose -f <scratch file> --dry-run up -d --wait`, `… down`, `… down -v` | flags accepted; a dry run on a scratch project, nothing created or removed |
| `git branch --show-current`, `status`, `switch -c`, `restore .`, `switch main`, `switch -C play-ep03 main`, `diff main -- file`, `--no-pager log` (scratch clone) | all behave as the README and the skill say |
| Tutor loop by hand on episode 01 (scratch worktree of `origin/main`, branch `play-ep01`): blank `seed()` body with `raise NotImplementedError("TODO(human)")` → test | `E NotImplementedError: TODO(human)` (3 errors, because the autouse fixture calls `seed`) |
| restore → test | 3 passed |
| episode 01's Break it (delete `session.commit()`) → test, then `git restore .` | `assert set() == {1042, 2077}`, then `git status --short` printed nothing |
| ledger header plus one row, `git check-ignore -v data/ledger.md` | table renders; `.gitignore:27:data/` ignores it |
| **Pass 2**, merged with `4e00962`: `uv run ruff check .`, `ruff format --check .`, `scripts/check_notebooks.py` | All checks passed; 70 files already formatted; 29 notebooks, 0 problems |
| Pass 2: `uv run --group app pytest app/tests/test_ep01_postgres.py -x -s` (the README line, as written) | header `test database: acme_c6630af5_test`, 3 passed |
| Pass 2: `uv run --group app pytest app/tests` (the SPEC.md Check's last part) | 5 passed; the test database was dropped at the end |
| `inspect.signature(sqlalchemy.text)`, `Session.execute` | `text(text: 'str') -> 'TextClause'`; `execute(self, statement, params=None, *, …)` |

## Failed, or never ran

- **Never ran for real: `docker compose down` and `docker compose down -v`.** Ten sessions share one Postgres and the
  run rules forbid both. I only checked that the flags parse (dry run on a scratch project). The wipe card and the
  second Done-when line depend on them, so that line stays unticked. Siddharth's own episode 01 will run them.
- **Not run: `open -a Docker`.** `/Applications/Docker.app` exists. Docker was already up, and I did not want to
  raise its window.
- **Not run: the sample test in "How to read a pytest test"** (`test_ada_reads_her_order`). It is an illustration,
  and `/orders/{id}` is a stub (501) until spec 03.
- **Not checkable yet: the HTTP code table** (403, 404, 409, 422 rows). The routes are stubs on main. The rows follow
  `specs/contract.md` and specs 03 and 07. Spec 03's and 07's tests will prove them.
- **Not run end to end: `/episode` itself.** The skill is not in this session's skill list, so I could not invoke it.
  I ran each mechanism by hand (the table above). Whether Claude Code expands `$ARGUMENTS` the way I assume is from
  Context7 (`/websites/code_claude`), not from a run.
- **Dead links until the other PRs merge:** `track/README.md` links 03-11. Folder names match the specs, and the
  ones already on sibling branches (03-fastapi, 05-page, 07-orchestration, 10-brief-the-agent) match exactly.
  04-agent-joins, 06-logfire, 08-approvals, 09-playwright and 11-bug-hunt are from the specs only.
- **Failed first, then fixed (mine):** my first Docker check printed "not reachable" because macOS has no `timeout`
  command; a re-run without it showed Docker up. A dry-run loop failed once because zsh does not split a quoted
  variable. Neither touched anything.
- **Failed before the merge, fixed by 01:** `ruff format --check .` flagged `specs/contract.md`, because ruff
  formats Python blocks inside Markdown. 01 added `extend-exclude = ["specs"]` to `pyproject.toml`, so after the
  merge it passes. I did not touch `contract.md`.

## Guesses I made

- **The "approved plan's 5 sentences" were not available to me.** They are not in the repo or in the notes folder. I
  wrote the five sentences myself from CONTRIBUTING.md, `docs/agentic-coding.md` and spec 06's vocabulary. Siddharth
  should read them and swap in the approved wording if it differs.
- README "Time: 20 min" and the title "00: the map".
- The tutor skill goes beyond the spec in two small places: it runs `psql` as `-c "…"` itself and starts servers in the
  background (a shell cannot type at a prompt), and it deletes only a file that a Break it created (`git restore .`
  leaves new files behind; episode 02's Break it makes one).
- Episodes 10 and 11 are handled as "follow the episode's own text" in the skill, since spec 08 (removes
  `shipping_expert` and `ask_shipping`) and spec 10 (applies a patch) do not blank one function body.
- I listed no "your piece" per episode in the README, so it cannot go stale if a spec changes its piece.
- The README sample uses `/orders/1042` and the `client` fixture from `contract.md`.

## Findings for the other specs (nothing here is changed by this PR)

1. **The dev database `acme` is never seeded** (confirmed by accident, see "Shared state": order 1042 is not in `acme`). `alembic upgrade head` builds the tables; `seed()` is only called
   by the test fixtures (`app/tests/conftest.py`). `app/main.py` does not call it. Anyone who starts the app by hand
   (episodes 03-08) has no orders 1042 and 2077: `GET /orders/1042` is 404 and the desk's `lookup_order` finds nothing.
   Suggest a `seed` call at startup (`lifespan`) or a one-line command in the README wipe card. Spec 01 or 05 owns this.
2. **Port 8000 is taken on this Mac** by a Docker process (a Dify stack). So the first `fastapi dev app/main.py`
   may fail with `[Errno 48]` on Siddharth's machine too. The README's error table says to use `--port 8001`.
   If you prefer, change the default in every episode instead.
3. Resolved by PR 7 while I worked: conftest used the fixed name `acme_test` at `ddfbfae`; main now derives
   `acme_<hash>_test` per checkout. The README's pytest line needs no env prefix and runs as written.
4. `ruff format` formats code blocks in all Markdown. A bad Python block in any EPISODE.md fails `ci`. Run
   `uv run ruff format --check .` before pushing.

## Shared state I touched

**My mistake: `alembic upgrade head` ran against the dev database `acme`.** In pass 2 I set `DATABASE_URL` from a shell
variable that came back empty (`-q` hides the pytest header), so the URL ended in `/` and Postgres used the default
database, `acme`. I noticed from the output (`0001 (head)`, and order 1042 not found). A read-only look afterwards:
`acme` has `alembic_version` (`0001`), `orders`, `tickets`, `audit_log`, `refunds`, the tables are newer (by object id)
than every other database, and `orders` is empty. So the command most likely built the schema in an empty `acme`; it
adds tables and drops nothing. I did not undo it (a downgrade would be a second unasked change to a shared
database). If someone expected `acme` to be empty, run `uv run --group app alembic downgrade base` against it.
I created and dropped my own database `acme_02_test` on the shared Postgres (pass 1); in pass 2 conftest created and
dropped `acme_c6630af5_test` itself. Ran `docker compose up -d --wait` once
(a no-op on the running container). A scratch worktree of `origin/01-skeleton` and a local branch `play-ep01` were
created and removed. One scratch clone read the main checkout's git objects (read-only). Nothing else was touched.

## Sources

- Context7: `/websites/sqlalchemy_en_20` (`text()`, `:name` bind parameters, `Session.execute` with a dict),
  `/astral-sh/uv` (exact vs inexact sync, `--group`), `/websites/pytest_en_stable` (fixtures as arguments, conftest.py,
  `-x`, `-s`), `/docker/compose` (`up --wait`, `down`, `down --volumes`, `--dry-run`),
  `/websites/code_claude` (skill frontmatter: `name`, `description`, `argument-hint`, `disable-model-invocation`;
  `$ARGUMENTS`).
- Installed, checked by running: `sqlalchemy.text` and `Session.execute` signatures, `fastapi dev` host and port,
  `alembic upgrade head` and `current`, `psycopg.connect` error text, Docker CLI error texts.
- Read in the repo: `SPEC.md`, `specs/contract.md`, `specs/01-10`, `CONTRIBUTING.md`, `AGENTS.md`,
  `docs/agentic-coding.md`, `.claude/hooks/guard_git.py`, `compose.yaml`, `app/main.py`, `app/seed.py`,
  `app/tests/conftest.py`, `track/01-postgres/EPISODE.md`, `track/02-alembic/EPISODE.md`.
