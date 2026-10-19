# 11: Bug hunt
**You'll see:** three silent bugs, each one a mistake the course warned about, and you find and fix each from a red test alone. **Time:** 30-45 min. **With me:** `/episode 11 do` (I plant each bug, you hunt it, I give a hint when you ask)

Honour system: don't open `track/11-bug-hunt/bugs/`. While a bug is planted, don't run `git status`, `git diff` or `git log -p`, and don't look at your editor's changed-files list. They name the file, and git can't hide them.

## Run it
You need episodes 01-10 done: Postgres, the tables, the routes, the desk, the approvals.
```bash
docker compose up -d --wait
```
```bash
uv sync --group app
```
Plant bug 1 on a throwaway branch. `git apply` prints nothing, which is the point. Make your guess for bug 1 (see **Predict**) before the next command.
```bash
git switch -C play-ep11 main
```
```bash
git apply track/11-bug-hunt/bugs/bug-1.patch
```
```bash
uv run --group app pytest app/tests/test_ep04_agent.py -x
```
> ✅ Checkpoint: one test is red. You can read its name, the line where it stopped and the message. That is your whole symptom.

Each bug runs the same loop:
1. Read the symptom. Ask for a hint only when you are stuck (see **Your piece**).
2. Say the root cause in **one sentence**. Then fix it.
3. Run that bug's locked test until it is green.
4. `git restore .` (it removes the bug and your fix), then plant the next one.

| Bug | Plant it | Locked test |
|---|---|---|
| 1 | `git apply track/11-bug-hunt/bugs/bug-1.patch` | `uv run --group app pytest app/tests/test_ep04_agent.py -x` |
| 2 | `git apply track/11-bug-hunt/bugs/bug-2.patch` | `uv run --group app pytest app/tests/test_ep08_approvals.py -x` |
| 3 | `git apply track/11-bug-hunt/bugs/bug-3.patch` | `uv run --group app pytest app/tests/test_ep03_fastapi.py -x` |

> ✅ Checkpoint: after each `git restore .`, `git status --short` prints nothing and that bug's test is green again.

## Read
Start from the symptom, not from the code. Three places are fair game before you guess:
- The locked test (`app/tests/test_ep0N_*.py`): which line failed, and what did it expect?
- The traceback: the last line that names a file under `app/` (not `app/tests/`) is where the problem was noticed. That is often not where the mistake is.
- The database. Run the locked test so it keeps its database: `ACME_KEEP_TEST_DB=1 uv run --group app pytest <test file> -x`. Read the line `test database: acme_xxxxxxxx_test` at the top of the output, then look inside:
  ```bash
  docker compose exec db psql -U acme acme_xxxxxxxx_test -c "select * from refunds;"
  ```
  A failed test leaves its rows behind (the tables are only wiped before the next test). Try `tickets` too.

## Predict
Write one line before each run:
- Bug 1: will the red test be about what the desk remembers, or about what it counts?
- Bug 2: will the error come from the route, or from the tool?
- Bug 3: will `test_sam_reads_any_order` go red too? (Run the file once without `-x` to check.)

> ✅ Checkpoint: a wrong guess is fine. Say it, then compare it with the answers at the end.

## Break it
The whole episode is the break: each patch is a sabotage someone else made. If you are stuck on one bug for 15 minutes, open the next hint. The way back is always `git restore .`.

## Your piece
Find and fix all three. Never edit a test, and never loosen a check: deleting a condition from the line that raised hides a bug, it does not fix it. A bug is fixed when its locked test is green and the test is untouched. Open one hint at a time.

**Bug 1** (`test_ep04_agent.py`). Hint 1: the first message works and the second one still sees it. Read the assert. What is it counting, and what did the app promise to carry over?
<details><summary>Hint 2</summary>

Look at the ticket row after the failed run: `docker compose exec db psql -U acme acme_xxxxxxxx_test -c "select id, version, conversation->'usage' from tickets;"`

</details>
<details><summary>Hint 3</summary>

One function writes `tickets.conversation`. Read what it builds before it writes, and compare that with its docstring.

</details>

**Bug 2** (`test_ep08_approvals.py`). Hint 1: the error says the refund "is not approved", but the test just approved it. Who changed it, and when?
<details><summary>Hint 2</summary>

psql: `select id, ticket_id, status from refunds;`. What status did the click leave behind?

</details>
<details><summary>Hint 3</summary>

`grep -n '"rejected"' app/routes/approvals.py`. Two places write that word. Read the `WHERE` just above the second one.

</details>

**Bug 3** (`test_ep03_fastapi.py`). Hint 1: the test expected a 404 and got a 200. Whose order did ada just read?
<details><summary>Hint 2</summary>

A customer must only see their own rows. Which route returns an order, and what does it know about the caller?

</details>
<details><summary>Hint 3</summary>

Compare `get_order` with `get_ticket` just above it in `app/routes/tickets.py`. What does one check that the other does not?

</details>

> ✅ Checkpoint: three green runs, each followed by `git restore .`, and a final `git status --short` that prints nothing.

## Words
- **Root cause:** the one line that is wrong, not the place where the error shows up.
- **Symptom:** what you see (a red test). The cause is why it happens.
- **Silent bug:** a line that looks right and raises no error itself. The damage shows up later and somewhere else: a wrong number, a row the wrong person can read, or another check failing.
- **Locked test:** a test you run but never edit. It decides when you are done.
- **Play branch:** a throwaway branch (`play-ep11`) that is never pushed.

<details>
<summary>Answers (honour system: only after you said the root cause yourself)</summary>

**Bug 1.** Symptom: `test_usage_carries_over_and_the_version_counts_saves` fails with `assert (0, 2) == (2, 2)`. It is about counting: the chat itself is remembered. Root cause: `memory.save` rebuilds the `Conversation` field by field and leaves out `usage`, so the ticket's running count of requests and tokens is lost on every save. Fix: store the whole `conversation` it was given, as the docstring says.

**Bug 2.** Symptom: `test_approve_executes_exactly_once` fails with `RuntimeError: refund pyd_ai_... on ticket 1 is not approved`. It comes from the tool (`issue_refund` calls `execute_refund`, the last lock doing its job), but the mistake is in the route. Root cause: in `app/routes/approvals.py`, the UPDATE that rejects the *other* waiting refunds lost `Refund.status == "pending"`, so it also rejected the refund that had just been approved. Fix: put the condition back. If you made the test green by deleting `Refund.status == "approved"` from `execute_refund` instead, you hid the bug: the refund is rejected and then executed anyway, and every test still passes because the route's own locks stop the second click. Put that condition back and look again.

**Bug 3.** Symptom: `test_ada_reads_her_order_but_not_bos` fails with `assert 200 == 404`. Only that test goes red: sam is staff, so `test_sam_reads_any_order` stays green. Root cause: `get_order` finds the order but no longer checks that it belongs to the caller. Fix: raise the 404 also when the user is not staff and `order.customer != user.name`, as `get_ticket` does.

</details>
