# 08: Approvals
**You'll see:** a refund wait in the database until a person clicks Approve, then run exactly once. **Time:** 30-45 min. **With me:** `/episode 08` (tour) or `/episode 08 do` (your piece)

## Run it
Start Postgres and build the tables if you have not: `docker compose up -d --wait`, then `uv run --group app alembic upgrade head`.

1. Run the locked test. It plays the whole story with a fake model.
   ```bash
   uv run --group app pytest app/tests/test_ep08_approvals.py -v
   ```
   > ✅ Checkpoint: 5 passed. One test per rule: waits, executes once, rejects, staff only, right ticket only.
2. Start the app.
   ```bash
   uv run --group app uvicorn app.main:app
   ```
   Open http://127.0.0.1:8000. Pick `sam` (staff), make a ticket, and send `Please refund order 1042`.
   > ✅ Checkpoint: a card appears: `Refund $12.00 for order 1042?` with Approve and Reject buttons. No refund has happened yet.
3. Look in the database while the card is still waiting.
   ```bash
   docker compose exec db psql -U acme acme -c 'select id, ticket_id, order_id, amount_cents, status from refunds;'
   ```
   > ✅ Checkpoint: one row, status `pending`. The amount came from the orders table, not from the model.
4. Click Approve, then run the query from step 3 again.
   > ✅ Checkpoint: the desk answers in the log, and the row says `executed`.
5. Click the same refund a second time, the way a double click would. Use the ids from your row.
   ```bash
   curl -s -i -X POST http://127.0.0.1:8000/tickets/1/approvals/1 -H 'X-Demo-User: sam' -H 'Content-Type: application/json' -d '{"decision":"approve"}'
   ```
   > ✅ Checkpoint: `409` and a detail that says the refund is not waiting. Run step 3's query: still `executed`, once.
6. Try it as a customer: the same command with `-H 'X-Demo-User: ada'`.
   > ✅ Checkpoint: `403 Staff only`. The route checks who you are before it looks at anything else.

## Read
- `app/routes/approvals.py:32`: one `UPDATE ... WHERE status = 'pending' RETURNING`. Two clicks race, and the database lets only one win.
- `app/routes/approvals.py:23`: the desk resumes from the conversation saved in Postgres. The browser sends only `approve` or `reject`.
- `app/approvals.py:41`: `execute_refund`, the last lock. It only moves `approved` to `executed`, and it fails loudly otherwise.

## Predict
- After step 2: is the refund done, or only asked for? Check with step 3.
- After step 4: how many rows are `executed`? Check with the same query.
- Step 5: does the second click get a 200, a 409 or a 500?

## Break it
The route has two locks against a second click: the guarded `UPDATE` (line 35) and the `if call_id not in answers` check under it. Remove both: delete `, Refund.status == "pending"` and the two-line `if` with its `raise HTTPException(...)`. Guess first: what does the second click do now?
```bash
uv run --group app pytest app/tests/test_ep08_approvals.py -v
```
> ✅ Checkpoint: two tests fail. Approving twice crashes with `'NoneType' object has no attribute 'build_results'` (a real server would answer 500), and the first `UPDATE` already moved the refund row. Remove just the `UPDATE` guard and everything still passes, because the `if` refuses the click and rolls the `UPDATE` back. The guard earns its place when two clicks arrive at the same moment. Undo with `git restore .`.

## Your piece
Blank the body of `execute_refund` in `app/approvals.py` and write it again. Locked test:
```bash
uv run --group app pytest app/tests/test_ep08_approvals.py
```
1. It is one SQL `UPDATE` on the `refunds` table. Think about which rows it may touch.
2. Match the row by `ticket_id` and `tool_call_id`, and only if its `status` is `"approved"`. Set it to `"executed"`.
3. `update(Refund).where(...).values(status="executed").returning(Refund.order_id, Refund.amount_cents)`, then `.first()`. If that is `None`, raise `RuntimeError`. Otherwise return a sentence like `Refunded 12.00 for order 1042.`

## Words
- **approval**: a tool call the model may ask for but only a person can allow. Pydantic AI pauses the run and hands you a `DeferredToolRequests`.
- **`tool_call_id`**: the id the model gave that one call. It ties the waiting row to the paused run.
- **guarded UPDATE**: `UPDATE ... WHERE status = 'pending'`. The WHERE is the lock; zero rows changed means someone else got there first.
- **`ToolDenied`**: the answer for a rejected call. The model reads it and carries on.
- **`build_results`**: turns your decisions into the `DeferredToolResults` that resume the run.
