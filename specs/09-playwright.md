# 09 playwright
Status: todo

## What and why
A real browser proves the approval rule, teaching episode 09. Wave 4, after 07.
`uv run --group app playwright install chromium` (approved download). app/tests/e2e/conftest.py starts
`uvicorn app.main:app` in a subprocess on a free 127.0.0.1 port with `DATABASE_URL` = acme_test and `MODEL=test`,
waits for /health, and yields the base URL (no `--base-url`: pytest-base-url is optional in pytest-playwright 0.10).
Sync Playwright API only, plain `def` tests, `expect(...)` with a raised timeout, no sleeps, no networkidle.
test_ep09_playwright.py:
- ada sends a message and sees an assistant reply (also proves spec 05's sendMessage)
- sam asks for a refund on order 1042 in a fresh ticket: the approval card shows; the refunds row is pending
  and NOT executed; click Approve; the row is executed and a reply appears
- the same with Reject: nothing executed
- a message `<b>x</b>` shows as literal text (textContent)
CI: add `uv run playwright install --with-deps chromium` and `uv run pytest app/tests/e2e --tracing retain-on-failure`
to the fullstack job, upload test-results/ on failure.
Episode 09 starts with `--headed --slowmo 300` (watch it), then `--tracing on` and `playwright show-trace`,
break it = rename the Approve button, read the red trace, fix the locator.
Your piece: the Reject test body.

## Done when
- [ ] The four e2e tests pass locally and in CI
- [x] Blanking the Reject test (`raise NotImplementedError`) turns it red (checked, then restored)
- [x] track/09-playwright/EPISODE.md in the contract format
- [ ] The Check passes; /code-review and /security-review run, real findings fixed

## Touches
app/tests/e2e/, .github/workflows/ci.yml (fullstack job only), track/09-playwright/EPISODE.md

## Out of scope
Playwright Test Agents, MCP, codegen as a required step, Node, other browsers, app code changes.
