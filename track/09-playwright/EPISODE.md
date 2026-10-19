# 09: Playwright
**You'll see:** a real browser click through the desk and prove that a refund waits for a person. **Time:** 30-45 min. **With me:** `/episode 09` (tour) or `/episode 09 do` (your piece)

## Run it
Docker Desktop must be running. Then, in the repo folder:

1. Start Postgres.
   ```bash
   docker compose up -d --wait
   ```
   > ✅ Checkpoint: the last line says `Container acme-desk-db-1 Healthy`.
2. Download the browser once. Playwright keeps its own Chromium, separate from your Chrome.
   ```bash
   uv run --group app playwright install chromium
   ```
   > ✅ Checkpoint: a progress bar ends at `100%` and the command exits without an error.
3. Run the four browser tests. They start the real server themselves, on a free port, with the fake model.
   ```bash
   uv run --group app pytest app/tests/e2e
   ```
   > ✅ Checkpoint: `4 passed`. No window opened: this is "headless".
4. Run them again and watch. `--headed` shows the window. `--slowmo 300` waits 300 ms between steps.
   ```bash
   uv run --group app pytest app/tests/e2e --headed --slowmo 300
   ```
   > ✅ Checkpoint: a Chromium window opens by itself. You see a ticket appear, a message typed, an approval card with two buttons, and a click. Then `4 passed`.
5. Record a trace of the approve test. A trace is a recording you can scrub through afterwards.
   ```bash
   uv run --group app pytest app/tests/e2e -k approves --tracing on
   ls test-results
   ```
   Copy the folder name `ls` prints, then open its recording:
   ```bash
   uv run --group app playwright show-trace test-results/<that-folder>/trace.zip
   ```
   > ✅ Checkpoint: the Trace Viewer opens. The left list holds every step. Click the step that clicks "Approve": the page before and after is on screen, and the Network tab shows a `POST` to `/approvals/...`.
6. The test also reads the database. See what it saw (the run in step 5 left the rows there).
   ```bash
   docker compose exec db psql -U acme acme_test -c "select id, order_id, amount_cents, status from refunds;"
   ```
   > ✅ Checkpoint: one row for order 1042, status `executed`.

## Read
- `app/tests/e2e/conftest.py:39`: `app_url` starts the real server in a second process. `MODEL=test` goes in that process's environment, because a patch in the test process cannot reach it.
- `app/tests/e2e/test_ep09_playwright.py:38`: `ask_for_refund` makes a fresh ticket every time (the fake model calls tools only on a conversation's first request) and finds things the way a person would: by role and name.
- `app/tests/e2e/test_ep09_playwright.py:60`: the approve test. The page shows a card, but only the database knows the truth: `pending` while the card waits, `executed` after the click.

## Predict
- Step 4: while the approval card is on screen, does the `refunds` row say `pending` or `executed`?
- Step 4: does the desk write its reply before you press Approve, or after?
- Step 5: what does the Network tab show for the Approve click?

## Break it
Open `app/static/approvals.js` and change the button label `Approve` to `OK`. Guess what the test says, then run:
```bash
uv run --group app pytest app/tests/e2e -k approves --tracing retain-on-failure
```
It waits 10 seconds, then fails: there is no button named "Approve". Open the trace from `test-results` and look at the last step. The snapshot shows a card with an "OK" button, so the locator is wrong, not the app. Fix the locator in the test (`name="OK"`) and watch it go green, or undo with `git restore .`.

## Your piece
`test_sam_rejects_a_refund` in `app/tests/e2e/test_ep09_playwright.py`. Blank its body (keep the `def` line), write it again, and run the locked test until it is green:
```bash
uv run --group app pytest app/tests/e2e -k rejects
```
1. It is the approve test with a different button and a different row status.
2. Start with `ask_for_refund`. Click "Reject" inside the card, wait for the page's `POST` to `/approvals/...`, then read the row with `refund_statuses()`.
3. `card = ask_for_refund(page, app_url)`, then `with page.expect_response(lambda r: "/approvals/" in r.url) as decided:` around `card.get_by_role("button", name="Reject").click()`. Then `assert decided.value.ok`, `assert refund_statuses() == ["rejected"]` and `expect(page.get_by_test_id("assistant-message").first).to_be_visible()`.

## Words
- **Playwright**: a library that drives a real browser from Python: open pages, click, read.
- **Headless**: the browser runs with no window. `--headed` gives it one.
- **Locator**: how a test finds an element, such as `get_by_role("button", name="Approve")`.
- **`expect`**: a check that keeps retrying until the page matches or 10 seconds pass. This is why the tests never sleep.
- **Trace**: a recording of a test run: every step, a snapshot of the page, and the network calls.
