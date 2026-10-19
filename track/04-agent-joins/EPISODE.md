# 04: The agent joins
**You'll see:** a customer message go through the desk agent, and the ticket remember the whole chat in Postgres. **Time:** 30-45 min. **With me:** `/episode 04` (tour) or `/episode 04 do` (your piece)

## Run it
You need episodes 01-03: Postgres running, the tables built, and the ticket routes. With no model key the desk runs on a fake model (`TestModel`), so its replies are dummy text like `a`. With a key in `.env` the real model answers. The wiring is the same.

1. Make sure the tables exist, then put the two demo orders in your dev database.
   ```bash
   docker compose up -d --wait
   ```
   ```bash
   uv run --group app alembic upgrade head
   ```
   ```bash
   uv run --group app python -c "from sqlalchemy.orm import Session; from app.db import engine; from app.seed import seed; seed(Session(engine))"
   ```
   > ✅ Checkpoint: no error. The last command prints `✅ ready: MODEL = ...`.
2. Start the app in a second terminal and leave it running.
   ```bash
   uv run --group app uvicorn app.main:app
   ```
   > ✅ Checkpoint: `Uvicorn running on http://127.0.0.1:8000`.
3. As ada, open a ticket. Note its `id` (`1` on a fresh database; use yours below).
   ```bash
   curl -s -X POST localhost:8000/tickets -H 'X-Demo-User: ada' -H 'content-type: application/json' -d '{"subject":"Cracked mug"}'
   ```
   > ✅ Checkpoint: `{"id":1,"customer":"ada","subject":"Cracked mug"}`.
4. Send the first message, then look at what the ticket saved.
   ```bash
   curl -s -X POST localhost:8000/tickets/1/messages -H 'X-Demo-User: ada' -H 'content-type: application/json' -d '{"text":"My mug from order 1042 arrived cracked."}'
   ```
   > ✅ Checkpoint: `{"ticket_id":1,"category":"billing","message":"a","approval":null}` (with a key, a real sentence ending `Need more help? Reply HELP.`).
   ```bash
   docker compose exec db psql -U acme acme -c "select id, version, jsonb_array_length(conversation->'messages') as messages, conversation->'usage'->>'requests' as requests from tickets where id = 1;"
   ```
   > ✅ Checkpoint: `version` 1, `messages` 5, `requests` 3 (two for the desk, one for the billing expert).
5. Send a second message to the same ticket, then run the same `psql` command again.
   ```bash
   curl -s -X POST localhost:8000/tickets/1/messages -H 'X-Demo-User: ada' -H 'content-type: application/json' -d '{"text":"Any news?"}'
   ```
   > ✅ Checkpoint: `version` 2, `messages` 8, `requests` 4. The desk got the old messages back, so the second turn cost only one request.
6. Every tool call was logged by a hook, not by the tools.
   ```bash
   docker compose exec db psql -U acme acme -c "select tool from audit_log where ticket_id = 1 order by id;"
   ```
   > ✅ Checkpoint: `lookup_order` and `ask_billing`, once each (their order can vary).
7. Now the staff side. Sam opens his own ticket (say its id is 2) and asks for a refund.
   ```bash
   curl -s -X POST localhost:8000/tickets -H 'X-Demo-User: sam' -H 'content-type: application/json' -d '{"subject":"Refund test"}'
   ```
   ```bash
   curl -s -X POST localhost:8000/tickets/2/messages -H 'X-Demo-User: sam' -H 'content-type: application/json' -d '{"text":"Refund order 1042"}'
   ```
   > ✅ Checkpoint: `{"ticket_id":2,"category":null,"message":null,"approval":null}`. The desk stopped and asked for a person (the `approval` stays `null` until episode 08). Run step 6 for ticket 2: `lookup_order` and `ask_billing`, but no `issue_refund`, because it has not run.
8. Run the episode's test.
   ```bash
   uv run --group app pytest app/tests/test_ep04_agent.py
   ```
   > ✅ Checkpoint: `9 passed`.

## Read
- `app/agents.py:109`: `desk`. The six rules from notebook 14 sit around it, each in one place: `RULES` (line 91), `Reply`, the `.filtered` line, the `Hooks`, `requires_approval=True` on `issue_refund`, and the limit in `run_desk`.
- `app/agents.py:135`: `run_desk`. Load the conversation, run the desk, save it again. No database session is open while it waits for the model.
- `app/memory.py:30`: `save()`. One `UPDATE` that only works if nobody saved first.

## Predict
- Step 5: will the second message add 1 request or 3?
- Step 6: will `issue_refund` show up in ada's log?
- Step 7: does the refund run when Sam asks?

## Break it
In `app/agents.py`, delete the line `conversation=conversation,` in `run_desk`. Guess which tests turn red, then run step 8. The desk is built fresh every turn, so the second message no longer sees the first. Undo with `git restore .`.

## Your piece
`save()` in `app/memory.py`. Run the locked test until it is green:
```bash
uv run --group app pytest app/tests/test_ep04_agent.py
```
1. `save()` must store the whole conversation in `tickets.conversation` and add 1 to `version`, but only if nobody else saved since you loaded.
2. Send one `UPDATE ... WHERE id = :ticket AND version = :version`. If it changed 0 rows, someone else got there first: raise `VersionConflict`.
3. `stored = ConversationTypeAdapter.dump_python(conversation, mode="json")`, then `session.execute(update(Ticket).where(Ticket.id == ticket_id, Ticket.version == version).values(conversation=stored, version=version + 1)).rowcount`, inside `with Session(engine) as session, session.begin():`.

## Words
- **Conversation**: the messages of a chat, plus the usage so far. Pydantic AI hands it back after every run.
- **Deps**: what one run knows about who is asking (`ticket_id`, `customer`, `role`). Tools read it from `ctx.deps`.
- **Version check**: save only if the row is still at the version you loaded. Otherwise another request won, and you get a 409.
- **Hook**: code that runs on every tool call. Here it writes the audit row.
- **Usage limit**: the most model requests one turn may spend. Here `used + 6`: six new ones on top of what the ticket already used.
