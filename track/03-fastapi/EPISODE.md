# 03: Your first FastAPI routes

**You'll see:** a web API where the status code (201, 401, 404, 422) tells you exactly what went wrong. **Time:** 30-45 min. **With me:** `/episode 03` (tour) or `/episode 03 do` (your piece)

## Run it

Postgres first (episode 01), then the server in a second terminal. It only listens on 127.0.0.1.

```bash
docker compose up -d --wait
uv run --group app fastapi dev app/main.py --host 127.0.0.1
```

> ✅ Checkpoint: the server prints `Uvicorn running on http://127.0.0.1:8000` and `/docs` opens in your browser.

Open <http://127.0.0.1:8000/docs>. Click `POST /tickets`, then **Try it out**. Type `ada` in `x-demo-user`, set the body to `{"subject": "My mug is cracked"}`, press **Execute**.

> ✅ Checkpoint: the response is `201` with `{"id": ..., "customer": "ada", "subject": "My mug is cracked"}`.

Now the same thing from the terminal, with the ways it can go wrong (use your own ticket id for `1`):

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST 127.0.0.1:8000/tickets -H 'content-type: application/json' -d '{"subject":"Hi"}'
curl -s -o /dev/null -w "%{http_code}\n" -X POST 127.0.0.1:8000/tickets -H 'content-type: application/json' -H 'X-Demo-User: ada' -d '{"subject":""}'
curl -s -o /dev/null -w "%{http_code}\n" 127.0.0.1:8000/tickets/1 -H 'X-Demo-User: bo'
curl -s -o /dev/null -w "%{http_code}\n" 127.0.0.1:8000/tickets/1 -H 'X-Demo-User: sam'
```

> ✅ Checkpoint: `401`, `422`, `404`, `200`, in that order. No login header, an empty subject, someone else's ticket, then staff.

```bash
curl -s 127.0.0.1:8000/orders/1042 -H 'X-Demo-User: ada'
curl -s 127.0.0.1:8000/orders/2077 -H 'X-Demo-User: ada'
```

> ✅ Checkpoint: the first prints the blue mug order; the second prints `{"detail":"Order not found"}`. Order 2077 is bo's.

## Read

- `app/routes/tickets.py:13`: `create_ticket`. A route is a function with a decorator saying which URL and method it answers, and `status_code=201`.
- `app/routes/tickets.py:22`: `get_ticket`. `user: UserDep` runs the login check before your code does; the 404 for other people's tickets is on the line below it.
- `app/identity.py`: `current_user`. It reads the `X-Demo-User` header and raises `401` if the name is not one we know. It is a labelled fake, not real login.

## Predict

- Before the `401` curl: what does a request with no header return, and does `create_ticket` even start?
- Before the `404` curl: would `403 Forbidden` be a better answer for bo? What would it tell bo about ada's tickets?
- Before the order curls: which part of `get_order` makes 2077 vanish for ada but not for sam?

## Break it

In `get_ticket`, delete `or ...` so the `if` only checks `ticket is None`.

```bash
uv run --group app pytest app/tests/test_ep03_fastapi.py
```

Guess first: which test goes red, and what does bo see on the `404` curl now? Undo with `git restore .`

## Your piece

`get_order` in `app/routes/tickets.py`. Replace its body with `raise NotImplementedError`, then ask your agent to write it back.

```bash
uv run --group app pytest app/tests/test_ep03_fastapi.py
```

Hints, from vague to exact:

1. `get_ticket` is the same idea. What changes when the thing you look up is an `Order`?
2. Look up the row by its id, and say "not found" the same way for a missing row and for someone else's row.
3. `session.get(Order, order_id)`, then `raise HTTPException(status_code=404, detail="Order not found")` unless it exists and (`user.role == "staff"` or `order.customer == user.name`).

## Words

- **Route:** a function tied to one URL and one HTTP method.
- **Schema:** a Pydantic class (`TicketIn`, `TicketOut`) that checks what comes in and shapes what goes out.
- **Dependency:** a function FastAPI runs for you and hands the result to your route (`UserDep`, `SessionDep`).
- **Status code:** the number that says how the request went: 201 created, 401 who are you, 404 not found, 422 bad input.
- **Bound parameter:** a value passed to the database separately from the SQL text, so input can never rewrite the query.
