# 11: Bug hunt
**You'll see:** three silent bugs, each one a mistake the course warned about, and you find and fix each from a red test alone. **Time:** 30-45 min. **With me:** `/episode 11` (I plant a bug, you hunt it, I give hints when you ask)

Honour system: don't open `track/11-bug-hunt/bugs/` and don't run `git diff` or `git log -p` while a bug is planted. They show the answer, and git can't hide them.

## Run it
You need episodes 01-10 done: Postgres, the tables, the routes, the desk, the approvals. Then:
```bash
docker compose up -d --wait
```
```bash
uv sync --group app
```
`/episode 11` makes the branch `play-ep11` and plants **bug 1** without showing it. Doing it by hand: `git switch -C play-ep11 main`, then `git apply track/11-bug-hunt/bugs/bug-1.patch` (it prints nothing).
```bash
uv run --group app pytest app/tests/test_ep04_agent.py -x
```
> ✅ Checkpoint: one test is red. You can read its name, the line where it stopped and the message. That is your whole symptom.

For each bug the loop is the same:
1. Read the symptom and guess (see **Predict**). Ask for a hint only when you are stuck (see **Your piece**).
2. Say the root cause in **one sentence**. Then fix it.
3. Run the same command until it is green.
4. `git restore .` (it removes the bug and your fix), then plant the next one.

| Bug | Plant it | Locked test |
|---|---|---|
| 1 | `git apply track/11-bug-hunt/bugs/bug-1.patch` | `app/tests/test_ep04_agent.py` |
| 2 | `git apply track/11-bug-hunt/bugs/bug-2.patch` | `app/tests/test_ep08_approvals.py` |
| 3 | `git apply track/11-bug-hunt/bugs/bug-3.patch` | `app/tests/test_ep03_fastapi.py` |

> ✅ Checkpoint: after each `git restore .`, `git status --short` prints nothing and the same test is green again.

## Read
Start from the symptom, not from the code. Three places are fair game before you guess:
- The locked test (`app/tests/test_ep0N_*.py`): which line failed, and what did it expect?
- The pytest traceback: the last frame that is inside `app/` is where the wrong thing happened. It is often not where the mistake is.
- The database. Run the test with `ACME_KEEP_TEST_DB=1 uv run --group app pytest <test file> -x`, then read the line `test database: acme_xxxxxxxx_test` at the top of the output and look inside:
  ```bash
  docker compose exec db psql -U acme acme_xxxxxxxx_test -c 'select * from refunds;'
  ```
  A failed test leaves its rows behind (the tables are only wiped before the next test). Try `tickets` or `refunds`.

## Predict
Write one line before you read each result:
- Bug 1: only one test in the file is red. Which of the two memory tests?
- Bug 2: the red test fails inside the route, or inside the tool?
- Bug 3: will the other order tests in the file go red as well?

> ✅ Checkpoint: a wrong guess is fine. Say it, then compare it with the answers at the end.

## Break it
The whole episode is the break: each patch is a sabotage someone else made. If you are stuck on one bug for 15 minutes, open the next hint. The way back is always `git restore .`.

## Your piece
Find and fix all three. The locked tests are the three commands above. Never edit a test: a bug is fixed when the test goes green with the test untouched. Open one hint at a time.

**Bug 1** (`test_ep04_agent.py`)
1. The first message works and the second one still sees it. Read the assert: what is it counting, and what did the app promise to carry over?
2. Look at the ticket row after the failed run (psql, `select id, version, conversation->'usage' from tickets;`).
3. One function writes `tickets.conversation`. Read what it builds before it writes, and compare it with the docstring above it.

**Bug 2** (`test_ep08_approvals.py`)
1. The error says the refund "is not approved". But the test just approved it. Who changed it, and when?
2. psql: `select id, ticket_id, status from refunds;`. What status did the click leave behind?
3. `grep -n rejected app/routes/approvals.py`. Two places write that word. Read the `WHERE` of the second one.

**Bug 3** (`test_ep03_fastapi.py`)
1. The test expected a 404 and got a 200. Whose order did ada just read?
2. A customer must only see their own rows. Which route returns an order?
3. Compare `get_order` with `get_ticket` just above it in `app/routes/tickets.py`. What does one check that the other does not?

> ✅ Checkpoint: three green runs, each followed by `git restore .`, and a final `git status --short` that prints nothing.

## Words
- **Root cause:** the one line that is wrong, not the place where the error shows up.
- **Symptom:** what you see (a red test). The cause is why it happens.
- **Silent bug:** wrong results with no crash on the happy path, so nothing shouts.
- **Locked test:** a test you run but never edit. It decides when you are done.
- **Play branch:** a throwaway branch (`play-ep11`) that is never pushed.

<details>
<summary>Answers (honour system: only after you said the root cause yourself)</summary>

**Bug 1.** Symptom: `test_usage_carries_over_and_the_version_counts_saves` fails with `assert (0, 2) == (2, 2)`. Root cause: `memory.save` rebuilds a `Conversation` from the messages only, so the usage is never stored and every turn starts at zero (the per-turn request limit resets with it). Fix: store the whole `conversation` you were given, as the docstring says.

**Bug 2.** Symptom: `test_approve_executes_exactly_once` fails with `RuntimeError: refund pyd_ai_... on ticket 1 is not approved`, raised by `execute_refund`, the last lock doing its job. Root cause: in `app/routes/approvals.py`, the UPDATE that rejects the other waiting refunds lost `Refund.status == "pending"`, so it also rejected the refund that had just been approved. Fix: put the condition back. (Dropping `AND status = 'approved'` from `execute_refund` is a different, quieter mistake: every test still passes, because the route's own locks stop a second click first.)

**Bug 3.** Symptom: `test_ada_reads_her_order_but_not_bos` fails with `assert 200 == 404`. Root cause: `get_order` finds the order but no longer checks that it belongs to the caller. Fix: raise the 404 also when the user is not staff and `order.customer != user.name`, as `get_ticket` does.

</details>
