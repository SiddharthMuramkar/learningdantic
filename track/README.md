# 00: the map

**You'll see:** how the parts of Acme Desk fit together, and the small things you need before episode 1.
**Time:** 20 min. **Read it once, then keep the start/stop card handy.**

Acme Desk is a small support desk: customers open tickets and chat with an AI agent, and a staff member
must say yes before a refund is paid. Coding agents built it. You read it, run it, break it and rebuild one
piece of it per episode.

## What orchestration is

1. An agent is a model, instructions, tools and an output type, and orchestration is how you connect
   agents, tools and people into one job.
2. The big question is who holds the wheel: the model picks each next step, your code picks it, or a person
   has to say yes first.
3. The more the model holds, the more flexible it is and the more it costs, because every decision is
   another model request.
4. The more your code holds, the cheaper and more predictable it is, so a rule that must never break lives in
   code, not in instructions.
5. Add a second agent only when a count (requests, cost, an eval score) shows that it helps.

Episode 07 shows the first four on one question. Episode 08 puts a person at the wheel.

## The map

```text
                         Playwright drives the page like a person (09)
                                          |
  page (HTML + JS) --HTTP--> FastAPI --> desk agent --> tools --SQL--> Postgres
  app/static/           app/routes/      app/agents.py  (lookup, billing,    (Docker)
                                                        refund)
  Logfire sees every step: the request, the agent run, each tool call, each SQL statement (06)
```

| Box | What it does | Where |
|---|---|---|
| Page | a box to type in, sends your message | `app/static/` |
| FastAPI | takes the HTTP request, checks who you are | `app/main.py`, `app/routes/` |
| Desk agent | reads the message, decides what to do | `app/agents.py` |
| Tools | look up an order, ask billing, issue a refund | `app/agents.py` |
| Postgres | orders, tickets, refunds, audit log | `compose.yaml`, `app/models.py`, `migrations/` |
| Logfire | records the whole trip as a trace | wired once in `app/__init__.py` |
| Playwright | clicks through the page in a real browser | `app/tests/e2e/` |

There is no real login. The page sends a header like `X-Demo-User: ada`. `ada` and `bo` are customers,
`sam` is staff. It is a labelled fake, on purpose.

## Before episode 1

### Two terminal tabs

Tab A runs the long thing (the app). Tab B is for your commands. Open a second tab with Cmd+T.
**Ctrl+C** stops whatever is running in a tab. If a command seems stuck, press it.

### Git, only these

```bash
git status                  # what changed
git branch --show-current   # which branch you are on
git switch main             # go to the finished version
git switch -c try-it        # make your own branch and move to it
git restore .               # throw away edits git has not saved. There is no undo.
```

`main` is the finished, working version. A branch is your own copy to play in, so a mistake never touches
`main`. `git log` and `git diff` open a pager (a scrolling viewer). Press **q** to leave it.

### Docker Desktop

Open Docker Desktop (`open -a Docker`) and wait until the whale stops moving. Or let the terminal wait:

```bash
until docker info >/dev/null 2>&1; do sleep 2; done
```

It returns when Docker is ready. If it runs for more than two minutes, press Ctrl+C and look at the app.

### Install once

```bash
uv sync --group app
```

A bare `uv sync` removes the `app` packages (FastAPI, SQLAlchemy, psycopg). So type `--group app` every time,
also in `uv run --group app …`. Seeing `ModuleNotFoundError: No module named 'fastapi'` means you forgot.

### HTTP codes

| Code | Means | Where you will see it |
|---|---|---|
| 200 | it worked, here is the answer | reading a ticket |
| 201 | it worked and made something new | `POST /tickets` |
| 401 | we do not know who you are | no `X-Demo-User` header |
| 403 | we know you, and you may not | ada calling the approve route |
| 404 | not found, or not yours | bo asking for ada's ticket (404 so ids do not leak) |
| 409 | right request, wrong moment | approving the same refund twice |
| 422 | the body has the wrong shape | a ticket with an empty subject |

### How to read a pytest test

```python
def test_ada_reads_her_order(client):
    r = client.get("/orders/1042", headers={"X-Demo-User": "ada"})
    assert r.status_code == 200
```

`client` is not defined here. pytest sees the argument name, finds a **fixture** with that name (a function
marked `@pytest.fixture`), runs it, and passes the result in. Fixtures shared by many files live in
`conftest.py`; here `app/tests/conftest.py` builds the test database and hands out `client` and `session`.
The `assert` is the check. On a failure, the line starting with `>` is where it stopped and the `E` lines say
why.

```bash
uv run --group app pytest app/tests/test_ep01_postgres.py -x -s
```

`-x` stops at the first failure. `-s` shows your `print` output. Tests named `test_epNN_*` are **locked**:
you never edit them. They are the judge.

### The `?` in notebook 13 is `:name` here

Notebook 13 used `sqlite3` with `?` placeholders. SQLAlchemy writes the placeholder as `:name` and takes a
dict:

```python
session.execute(text("SELECT * FROM orders WHERE id = :id"), {"id": 1042})
```

Same rule as before: never paste user text into the SQL string.

## Start, stop, wipe

Start (two tabs):

```bash
docker compose up -d --wait                  # tab B: Postgres, waits until it is healthy
uv run --group app fastapi dev app/main.py   # tab A: the app at http://127.0.0.1:8000
```

Stop:

```bash
# tab A: Ctrl+C
docker compose down                          # tab B: stops Postgres, keeps your data
```

Wipe (empty the database, start over):

```bash
docker compose down -v                       # -v also deletes the data volume
docker compose up -d --wait
uv run --group app alembic upgrade head      # builds the tables again
```

### Five common errors

| You see | It means | Do |
|---|---|---|
| `failed to connect to the docker API …` (older Docker: `Cannot connect to the Docker daemon`) | Docker Desktop is not running | open it, wait loop above |
| `Bind for 127.0.0.1:5432 failed: port is already allocated` | another Postgres already uses port 5432 | `docker ps` to find it, stop that one, start again |
| `psycopg.OperationalError: … Connection refused` | the database is not up | `docker compose up -d --wait` |
| `ModuleNotFoundError: No module named 'fastapi'` | the `app` group is missing | `uv sync --group app` |
| `[Errno 48] Address already in use` | an old app still runs on port 8000 | find its tab and press Ctrl+C |

## The episodes

| # | Folder | You will |
|---|---|---|
| 01 | [01-postgres](01-postgres/EPISODE.md) | start Postgres in Docker and look inside with `psql` |
| 02 | [02-alembic](02-alembic/EPISODE.md) | read a migration and walk the schema up and down |
| 03 | [03-fastapi](03-fastapi/EPISODE.md) | call the first routes and meet the demo login and status codes |
| 04 | [04-agent-joins](04-agent-joins/EPISODE.md) | chat with the desk agent, which remembers in Postgres |
| 05 | [05-page](05-page/EPISODE.md) | read the page line by line and watch its requests |
| 06 | [06-logfire](06-logfire/EPISODE.md) | see one chat as spans: request, agent, tool, SQL |
| 07 | [07-orchestration](07-orchestration/EPISODE.md) | answer one question three ways and count the requests |
| 08 | [08-approvals](08-approvals/EPISODE.md) | make a refund wait for a person across two requests |
| 09 | [09-playwright](09-playwright/EPISODE.md) | watch a real browser prove the approval rule |
| 10 | [10-brief-the-agent](10-brief-the-agent/EPISODE.md) | write the brief that makes an agent add the shipping expert |
| 11 | [11-bug-hunt](11-bug-hunt/EPISODE.md) | find three planted bugs from their symptoms |

## How an episode works

Each `EPISODE.md` is at most about 120 lines and has the same parts, in this order:

- **Run it**: commands, each followed by a `✅ Checkpoint` that says what you should see.
- **Read**: three places in the code, `path:line` and one sentence each.
- **Predict**: up to three one-line guesses. Guess before you run. A wrong guess teaches more than a right one.
- **Break it**: one deliberate sabotage, the symptom to guess, and `git restore .` to undo it.
- **Your piece**: one function, the locked test that checks it, and three hints from vague to exact.
- **Words**: up to five new terms.

You can read the file alone, or ask the tutor in Claude Code:

- `/episode NN` is the tour. It runs each command, asks for your guess first, and shows guess against result.
- `/episode NN do` is your piece. It blanks the function, shows the locked test go red, waits while you
  write it (or brief the agent), then shows it go green and the diff.

Both work on a throwaway branch called `play-epNN`, made from `main`. Nothing is pushed. When you finish the
tutor switches back to `main`, and your guesses are saved in `data/ledger.md` (it stays on your Mac).
