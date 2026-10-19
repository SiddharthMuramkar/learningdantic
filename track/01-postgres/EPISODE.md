# 01: Postgres
**You'll see:** a real database start in Docker, hold the demo orders, and keep or lose its data on purpose. **Time:** 30-45 min. **With me:** `/episode 01` (tour) or `/episode 01 do` (your piece)

## Run it
Open Docker Desktop and wait until it says it is running. Then, in the repo folder:

1. Start Postgres. `--wait` makes the command stop only when the database is ready.
   ```bash
   docker compose up -d --wait
   ```
   > ✅ Checkpoint: the last line says `Container acme-desk-db-1 Healthy`.
2. Open a SQL prompt inside the container. `-U acme` is the user. The last `acme` is the database.
   ```bash
   docker compose exec db psql -U acme acme
   ```
   > ✅ Checkpoint: the prompt reads `acme=#`.
3. At the prompt, type these one at a time. Lines that start with `\` are psql commands. SQL needs a `;` at the end.
   ```text
   \dt
   select 1 + 1
   ;
   \q
   ```
   > ✅ Checkpoint: `\dt` says `Did not find any tables.` After `select 1 + 1` the prompt changes to `acme-#`: it is waiting for more. The `;` makes it answer `2`. `\q` takes you back to your shell.
4. Run the episode's test. It makes a second database just for tests, builds the tables and adds the demo orders. Normally it deletes that database when it finishes. `ACME_KEEP_TEST_DB=1` keeps it, so you can look inside.
   ```bash
   ACME_KEEP_TEST_DB=1 uv run --group app pytest app/tests/test_ep01_postgres.py
   ```
   > ✅ Checkpoint: near the top, a line like `test database: acme_1a2b3c4d_test`. That is your test database, called `<test-db>` below. At the end, `3 passed`.
5. Look inside it, with your own `<test-db>` name.
   ```bash
   docker compose exec db psql -U acme <test-db>
   ```
   Then type `\dt`, then `select * from orders;`, then `\q`.
   > ✅ Checkpoint: five tables, and two orders: 1042 for ada (1 blue mug) and 2077 for bo (2 white mugs).
6. Stop the database, start it again, and count the orders.
   ```bash
   docker compose down
   ```
   ```bash
   docker compose up -d --wait
   ```
   ```bash
   docker compose exec db psql -U acme <test-db> -c "select count(*) from orders;"
   ```
   > ✅ Checkpoint: the count is `2`. The data lives in a volume called `pgdata`, outside the container.
7. Now stop it and delete the volume too, start again, and ask the same question.
   ```bash
   docker compose down -v
   ```
   ```bash
   docker compose up -d --wait
   ```
   ```bash
   docker compose exec db psql -U acme <test-db> -c "select count(*) from orders;"
   ```
   > ✅ Checkpoint: an error that ends in `database "<test-db>" does not exist`. Run step 4 to bring it back.

## Read
- `compose.yaml:15`: the `pgdata` volume. This one line is why step 6 keeps your data and step 7 does not.
- `app/db.py:11`: the address of the database, `localhost:5432`. The app, and every test, reads it from here.
- `app/seed.py:13`: `seed()`, the function that puts the demo orders in the table.

## Predict
- Step 3: after you type `select 1 + 1` and press Enter, what does the prompt do?
- Step 6: is your test database still there after `docker compose down`?
- Step 7: and after `docker compose down -v`?

## Break it
Open `app/seed.py` and delete the line `session.commit()`. Guess what the test says, then run step 4. The orders went to Postgres, but nobody told it to keep them, so the test finds an empty table. Undo with `git restore .`.

## Your piece
`seed()` in `app/seed.py`. Run the locked test until it is green:
```bash
uv run --group app pytest app/tests/test_ep01_postgres.py
```
1. `seed()` must leave the two demo orders in the `orders` table. Calling it twice must not add more or crash.
2. Add each order with `session.merge(order)`. It inserts the row, or updates the one with the same id.
3. Loop over `ORDERS`, call `session.merge(order)` for each, then `session.commit()` once at the end.

## Words
- **Postgres**: a database server. Your app talks to it over the network.
- **Container**: a small, sealed computer that Docker runs. `db` is the one holding Postgres.
- **Volume**: a folder Docker keeps outside the container, so the data outlives it.
- **SQL**: the language you speak to a database, such as `select * from orders;`.
- **Commit**: tell Postgres to keep the changes. Without it they are thrown away.
