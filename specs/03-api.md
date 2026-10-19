# 03 api
Status: todo

## What and why
The first FastAPI routes, teaching episode 03. Wave 2, after 01.
Implement app/routes/tickets.py exactly as contract.md says: `POST /tickets`, `GET /tickets/{ticket_id}`,
`GET /orders/{order_id}`. Plain `def` routes with `SessionDep` and `UserDep`. Customers see only their own rows
(anything else is 404, so ids don't leak); staff see all. Bound parameters only.
Episode 03 teaches: a route, a Pydantic schema, a dependency (the demo login header), status codes 201/401/404/422,
and `/docs` (try a request there). Second terminal: `uv run --group app fastapi dev app/main.py` (127.0.0.1 only).
Your piece: `get_order` in app/routes/tickets.py.

## Done when
- [ ] app/tests/test_ep03_fastapi.py passes: create a ticket as ada (201), read it back, bo gets 404 for it,
      sam gets 200, no header gets 401, an empty subject gets 422, ada reads order 1042 and gets 404 for 2077
- [ ] Blanking `get_order` turns test_ep03 red (checked, then restored)
- [ ] track/03-fastapi/EPISODE.md in the contract format
- [ ] The Check passes; /code-review and /security-review run, real findings fixed

## Touches
app/routes/tickets.py, app/tests/test_ep03_fastapi.py, track/03-fastapi/EPISODE.md

## Out of scope
The chat route and anything that runs an agent (spec 04). Changing schemas.py or main.py (spec 01's files).
