# 02: Alembic
**You'll see:** the database tables get built, torn down and rebuilt by a file you can read. **Time:** 30-45 min. **With me:** `/episode 02` (tour) or `/episode 02 do` (your piece)

## Run it
Start Postgres first if it is not running: `docker compose up -d --wait`. If you ran `down -v` in episode 01, the database is empty again, which is what you want here.

1. Build the tables. `upgrade head` means "run every migration up to the newest one".
   ```bash
   uv run --group app alembic upgrade head
   ```
   > ✅ Checkpoint: a line like `Running upgrade  -> 0001, initial schema: orders, tickets, audit_log, refunds`.
2. See what it made.
   ```bash
   docker compose exec db psql -U acme acme -c '\dt'
   ```
   > ✅ Checkpoint: five tables: your four, plus `alembic_version`.
3. Alembic keeps its place in that last table.
   ```bash
   docker compose exec db psql -U acme acme -c 'select * from alembic_version;'
   ```
   > ✅ Checkpoint: one row, `0001`.
4. Ask Alembic where it is, and what it knows.
   ```bash
   uv run --group app alembic current
   ```
   > ✅ Checkpoint: `0001 (head)`.
   ```bash
   uv run --group app alembic history
   ```
   > ✅ Checkpoint: `<base> -> 0001 (head), initial schema: orders, tickets, audit_log, refunds`.
5. Undo everything, look, and build it again.
   ```bash
   uv run --group app alembic downgrade base
   ```
   ```bash
   docker compose exec db psql -U acme acme -c '\dt'
   ```
   > ✅ Checkpoint: only `alembic_version` is left, and it is empty.
   ```bash
   uv run --group app alembic upgrade head
   ```
6. Now ask for a change. Open `app/models.py`, and in `class Ticket` add this line under `subject`:
   ```python
   priority: Mapped[str | None]
   ```
   ```bash
   uv run --group app alembic revision --autogenerate -m "add ticket priority"
   ```
   > ✅ Checkpoint: `Detected added column 'tickets.priority'`, and a new file in `migrations/versions/`. Open it: `upgrade()` has an `op.add_column` line and `downgrade()` has the matching `op.drop_column`.
7. Discard the change. Do not run `upgrade`. Delete the new file in `migrations/versions/` (`git status` shows it as untracked; in a terminal, `rm` plus its name), then undo your edit.
   ```bash
   git restore app/models.py
   ```
   ```bash
   uv run --group app alembic check
   ```
   > ✅ Checkpoint: `No new upgrade operations detected.` The models and the database agree again.

## Read
- `migrations/versions/0001_initial_schema.py:20`: `upgrade()`, one `create_table` for each of the four tables.
- `migrations/versions/0001_initial_schema.py:78`: `downgrade()` drops them in the opposite order. Why do `refunds` and `audit_log` go first?
- `migrations/env.py:15`: `target_metadata`, how Alembic learns what your models look like.

## Predict
- Step 5: after `downgrade base`, which tables are left?
- Step 6: what will `upgrade()` in the new file contain, and how many lines long is it?
- Step 7: why must you delete the file before anyone runs `upgrade head`?

## Break it
In `migrations/versions/0001_initial_schema.py`, change `"amount_cents"` in the `orders` table to `"amount"`. Guess the symptom, then run the episode 01 test:
```bash
uv run --group app pytest app/tests/test_ep01_postgres.py
```
The tests build their database from your migrations, so the code asks for a column the migration never made. Undo with `git restore .`.

## Your piece
`upgrade()` in `migrations/versions/0001_initial_schema.py`. Run the locked test until it is green:
```bash
uv run --group app pytest app/tests/test_ep02_alembic.py
```
1. `upgrade()` must create the four tables that `app/models.py` describes, with the parents before the children.
2. Call `op.create_table` once per table, in the order `orders`, `tickets`, `audit_log`, `refunds`. Copy each column from `models.py`. Foreign keys need `sa.ForeignKeyConstraint`.
3. Name every constraint with `op.f(...)` using the pattern in `NAMING_CONVENTION` (`app/models.py:19`), for example `op.f("pk_orders")`. The second test tells you what still differs from the models.

## Words
- **Migration**: a file that changes the database one step, with a way to undo it.
- **Revision**: one migration's id, such as `0001`. Each one points at the one before it.
- **Head**: the newest revision. `upgrade head` runs everything up to it.
- **Downgrade**: run a migration backwards. `base` means "before the first one".
- **Autogenerate**: Alembic compares your models with the database and writes the migration for you. Always read it.
