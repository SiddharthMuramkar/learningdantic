# 03: FastAPI
**You'll see:** a small web API where the status code (201, 401, 404, 422) tells you what went wrong. **Time:** 30-45 min. **With me:** `/episode 03` (tour) or `/episode 03 do` (your piece)

## Run it
You need two terminal tabs. Tab 1 is for setup and `curl`. Tab 2 runs the server.

1. Start Postgres and build the tables (episodes 01 and 02).
   ```bash
   docker compose up -d --wait
   uv run --group app alembic upgrade head
   ```
   > ✅ Checkpoint: no error. If the tables already exist, `alembic` prints nothing new.
2. Put the two demo orders in your dev database. This calls the `seed()` function from episode 01.
   ```bash
   uv run --group app python -c "from app.db import engine; from app.seed import seed; from sqlalchemy.orm import Session; seed(Session(engine))"
   docker compose exec db psql -U acme acme -c "select id, customer from orders;"
   ```
   > ✅ Checkpoint: two rows, `1042 | ada` and `2077 | bo`.
3. In tab 2, start the server. `127.0.0.1` means only your own Mac can reach it.
   ```bash
   uv run --group app fastapi dev app/main.py --host 127.0.0.1
   ```
   > ✅ Checkpoint: a line that says `Uvicorn running on http://127.0.0.1:8000`. Leave this tab running.
4. Open <http://127.0.0.1:8000/docs>. FastAPI wrote this page from your code. Click `POST /tickets`, then **Try it out**. Type `ada` in `x-demo-user`, put `{"subject": "My mug is cracked"}` in the body, press **Execute**.
   > ✅ Checkpoint: `201` and `{"id": 1, "customer": "ada", "subject": "My mug is cracked"}`. Your `id` may differ: remember it.
5. Back in tab 1, make four requests go wrong or right. Use your `id` from step 4 instead of `1`.
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" -X POST 127.0.0.1:8000/tickets -H 'content-type: application/json' -d '{"subject":"Hi"}'
   curl -s -o /dev/null -w "%{http_code}\n" -X POST 127.0.0.1:8000/tickets -H 'content-type: application/json' -H 'X-Demo-User: ada' -d '{"subject":""}'
   curl -s -o /dev/null -w "%{http_code}\n" 127.0.0.1:8000/tickets/1 -H 'X-Demo-User: bo'
   curl -s -o /dev/null -w "%{http_code}\n" 127.0.0.1:8000/tickets/1 -H 'X-Demo-User: sam'
   ```
   > ✅ Checkpoint: `401`, `422`, `404`, `200`, in that order. No login header; an empty subject; someone else's ticket; staff.
6. Orders follow the same rule.
   ```bash
   curl -s 127.0.0.1:8000/orders/1042 -H 'X-Demo-User: ada'
   curl -s 127.0.0.1:8000/orders/2077 -H 'X-Demo-User: ada'
   ```
   > ✅ Checkpoint: the first prints the blue mug order. The second prints `{"detail":"Order not found"}`: order 2077 is bo's.

## Read
- `app/routes/tickets.py:18`: `create_ticket`. The decorator picks the URL, the method and `201`. `body: TicketIn` is a schema: FastAPI checks it before your code runs, which is why step 5 gives `422` without reaching the function.
- `app/routes/tickets.py:27`: `get_ticket`. `user: UserDep` runs the login check first. Lines 29-31 answer `404`, not `403`, so a customer cannot tell whether someone else's ticket exists.
- `app/identity.py:17`: `current_user`. It reads the `X-Demo-User` header and raises `401` for a name it does not know. This is a labelled fake, not real login.

## Predict
- Step 5, first request: no header. Does `create_ticket` start at all?
- Step 5, third request: would `403 Forbidden` be a better answer for bo? What would it tell bo about ada's tickets?
- Step 6, second request: which line of `get_order` makes 2077 vanish for ada but not for sam?

## Break it
In `get_ticket` (`app/routes/tickets.py:30`), change the `if` to just `if ticket is None:`. Guess which test goes red and what bo sees in step 5 now, then run:
```bash
uv run --group app pytest app/tests/test_ep03_fastapi.py
```
The ownership check was the only thing keeping bo out, and bo now gets ada's ticket. Undo with `git restore .`.

## Your piece
`get_order` in `app/routes/tickets.py`. Run the locked test until it is green:
```bash
uv run --group app pytest app/tests/test_ep03_fastapi.py
```
1. An order is visible to its owner and to staff. Everyone else, and any id that does not exist, gets `404`.
2. `get_ticket` just above does the same job for tickets. Look the order up with `session.get(Order, order_id)`.
3. If `order is None or (user.role != "staff" and order.customer != user.name)`, `raise HTTPException(status_code=404, detail="Order not found")`. Otherwise `return order`.

## Words
- **Route**: a function tied to one URL and one HTTP method, such as `POST /tickets`.
- **Schema**: a Pydantic class (`TicketIn`, `TicketOut`) that checks what comes in and shapes what goes out.
- **Dependency**: a function FastAPI runs for you and hands the result to your route (`UserDep`, `SessionDep`).
- **Status code**: the number that says how a request went: 201 created, 401 who are you, 404 not found, 422 bad input.
- **Bound parameter**: a value sent to the database apart from the SQL text, so input can never rewrite the query. `session.get` does this for you.
