# 11: Bug hunt
**You'll see:** three silent bugs, each one a mistake the course warned about, and you find and fix them from a red test alone. **Time:** 30-45 min. **With me:** `/episode 11` (I plant a bug, you hunt it) or `/episode 11 do` (same, with hints on request)

Honour system: don't open `track/11-bug-hunt/bugs/` and don't run `git diff`. Those show the answer. Git can't hide them, so you have to.

## Run it
Once: `docker compose up -d --wait` and `uv sync --group app`. Then `/episode 11` makes a play branch and plants **bug 1** without showing it. To do it by hand, run `git switch -C play-ep11 main` and then `git apply track/11-bug-hunt/bugs/bug-1.patch` (it prints nothing).

```bash
uv run --group app pytest app/tests/test_ep04_agent.py -x
```
> ✅ Checkpoint: one test is red. You can read its name, the line where it stopped and its message. That is your whole symptom.

For each bug: say the root cause in **one sentence**, fix it, run the same command until it is green. Then `git restore .` (it removes the bug and your fix) and plant the next one:
- bug 2: `git apply track/11-bug-hunt/bugs/bug-2.patch`, test `app/tests/test_ep08_approvals.py`
- bug 3: `git apply track/11-bug-hunt/bugs/bug-3.patch`, test `app/tests/test_ep03_fastapi.py`

> ✅ Checkpoint: after `git restore .` the same test is green again, and `git status` shows nothing changed.

## Read
Start from the symptom, not from the code. Only these three places are fair game before you guess:
- `app/tests/test_ep04_agent.py`, `test_ep08_approvals.py`, `test_ep03_fastapi.py`: what does the test expect, and which assert fails?
- The pytest traceback: which app function is the last frame in `app/`?
- `docker compose exec db psql -U acme -d acme`: look at what is really stored (`SELECT * FROM refunds;`). Use the `acme` database for looking only. Tests run on their own `*_test` database.

## Predict
Before you open the hint ladder, write one line each:
- Bug 1: "The second message fails because ___ was not saved."
- Bug 2: "Approving twice gives ___ because the guard ___."
- Bug 3: "ada can read bo's order because the query ___."

> ✅ Checkpoint: a wrong guess is fine. Say it, then compare it with the answer at the end.

## Break it
This whole episode is the break. The sabotage is already planted, so the only way back is `git restore .`. If you get stuck for 15 minutes on one bug, go one hint down and keep going.

## Your piece
All three bugs, one at a time. Locked tests: the three commands above. Never edit a test; a bug is fixed only when the test goes green with the test untouched. Each ladder goes from vague to exact. Open one rung at a time.

**Bug 1** (`test_ep04_agent.py`)
1. The first message works. The second message acts as if the first never happened.
2. Look at what is stored in `tickets.conversation` after each message, and at what the second run loaded.
3. The save step keeps less than the whole conversation. The test checks that usage carries over.

**Bug 2** (`test_ep08_approvals.py`)
1. A person clicks Approve twice. Something should say no the second time, and doesn't.
2. Count the `executed` refunds in psql. Then read the UPDATE that marks a refund executed.
3. One condition in that UPDATE is what makes "exactly once" true. Find the missing one.

**Bug 3** (`test_ep03_fastapi.py`)
1. ada asks for an order that is not hers and gets an answer instead of a 404.
2. The customer is known from the demo header. Where does the order query use it?
3. The query looks the order up by id only. A customer's rows must also be filtered by the owner.

> ✅ Checkpoint: three green runs, each followed by `git restore .`, then `git status` is clean.

## Words
- **Root cause:** the one line that is wrong, not the place where the error shows up.
- **Symptom:** what you see (a red test), as opposed to why it happens.
- **Silent bug:** wrong results with no crash, so nothing in the logs shouts.
- **Locked test:** a test you may run but never edit; it decides when you are done.
- **Play branch:** a throwaway branch (`play-ep11`) that is never pushed.

<details>
<summary>Answers (honour system: only after you have said the root cause yourself)</summary>

**Bug 1.** `memory.save` writes only the new messages of the last run instead of the whole conversation, so the next `load` gets a short history and the usage counter starts again. Fix: save the whole `result.conversation`, replacing what is stored.

**Bug 2.** `execute_refund` lost `AND status='approved'` in its UPDATE, so a refund that is already `executed` (or still `pending`) is updated again and the guard that makes it run once is gone. Fix: put the condition back, and keep failing loudly when 0 rows change.

**Bug 3.** The orders query filters by `id` only. Fix: for a customer, also filter by `customer = user.name`; staff see all; a miss is a 404 so ids don't leak.

</details>
