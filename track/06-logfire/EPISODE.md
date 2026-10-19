# 06: Logfire
**You'll see:** one chat message become a tree of timed steps (spans): the request, the agent, the model, the tool and the SQL. **Time:** 30-45 min. **With me:** `/episode 06` (tour) or `/episode 06 do` (your piece)

## Run it
Logfire is optional. Steps 1 and 2 need no account and send nothing anywhere. Step 3 is the part that uses your own Logfire login.

1. Run the episode's test. It sends one chat message and keeps the spans in memory (`capfire`) instead of sending them.
   ```bash
   uv run --group app pytest app/tests/test_ep06_logfire.py
   ```
   > ✅ Checkpoint: `1 passed`.
2. See what `setup()` did, so there was something to capture. Open `src/learningdantic/__init__.py` at line 40. Two lines turn Logfire on: `logfire.configure(send_to_logfire="if-token-present", ...)` and `logfire.instrument_pydantic_ai()`. `app/__init__.py` calls `setup()` once, when the app starts. Nothing is sent until Logfire finds a token or saved credentials.
   > ✅ Checkpoint: you can say why steps 1 and 2 sent nothing: there is no token.
3. Optional, Live view with your own login. In a terminal at the repo root:
   ```bash
   uv run logfire auth
   ```
   ```bash
   uv run logfire projects new
   ```
   Then start the app (`uv run --group app uvicorn app.main:app`), send a message to a ticket as in episode 04, and open your project's Live view at [logfire.pydantic.dev](https://logfire.pydantic.dev).
   > ✅ Checkpoint: one trace for `POST /tickets/{ticket_id}/messages`. Under it: `invoke_agent desk`, some `chat ...` lines, `execute_tool lookup_order`, and SQL lines such as `SELECT acme` and `UPDATE acme`. Click one: you see its arguments, result and time.
4. Before real users: the spans carry the customers' messages and the model's replies. Turn that off by editing the call in `setup()`:
   ```python
   logfire.instrument_pydantic_ai(include_content=False)
   ```
   > ✅ Checkpoint (only if you did step 3): new traces keep their shape and timings, but the prompt and reply text is gone.

## Read
- `src/learningdantic/__init__.py:40`: `setup()` configures Logfire and instruments Pydantic AI. This one line is why the agent, model and tool spans exist.
- `app/memory.py:13`: `logfire.instrument_sqlalchemy(engine=engine, ...)`. This one line is why the SQL spans exist. `skip_dep_check=True` is there because OpenTelemetry's instrumentor does not list SQLAlchemy 2.1 yet and refuses to start without it.
- `app/tests/test_ep06_logfire.py:26`: the four checks. A span's name tells you its kind: `invoke_agent`, `chat`, `execute_tool`; a SQL span has a `db.statement`.

## Predict
- Step 1: the test uses `TestModel()`, which calls every tool it is shown. Which check would fail if the model called no tool?
- Step 3: how many `chat` lines will you see for one message? (Count the `ask_billing` call too.)
- Step 4: will the SQL spans lose their text as well as the agent spans?

## Break it
In `src/learningdantic/__init__.py`, change `logfire.instrument_pydantic_ai()` to `pass`. Guess which of the four checks fail, then run step 1. Without that call nothing records the agent, model or tool steps, so those checks find nothing. (The SQL check still has its own line.) Undo with `git restore .`.

## Your piece
The `logfire.instrument_sqlalchemy(...)` call in `app/memory.py`. Delete it, then write it back until the locked test is green:
```bash
uv run --group app pytest app/tests/test_ep06_logfire.py
```
1. The test wants a span for the `UPDATE tickets` that saves the chat. SQLAlchemy sends no spans on its own: you have to instrument the engine.
2. Logfire has one function for it. It must be given the engine from `app/db.py`, which `memory.py` already imports.
3. `logfire.instrument_sqlalchemy(engine=engine, skip_dep_check=True)`, once, at the top level of the file.

## Words
- **Span**: one timed step with a name and details, such as one model call or one SQL statement.
- **Trace**: all the spans of one request, as a tree.
- **Instrumentation**: the one line that makes a library report spans. No line, no spans.
- **Token**: the secret that lets your app send spans to your Logfire project. No token, nothing leaves your machine.
- **`include_content`**: whether the spans keep prompt and reply text. Turn it off before real users write in.
