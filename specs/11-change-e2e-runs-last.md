# 11 change e2e runs last
Status: done

## What and why
Changes 09 (done). SPEC.md's Check runs `pytest app/tests` in one process. pytest collects `app/tests/e2e/`
first, and once Playwright's sync API has started (the session-scoped `playwright` fixture), it marks its
event loop as running in the main thread until the run ends. The three `async def` tests in
`test_ep10_shipping.py` then fail with "Cannot run the event loop while another loop is running": 3 failed,
34 passed. CI is green only because it runs the e2e folder in its own step.
Fix: `pytest_collection_modifyitems` in the e2e conftest moves the browser tests to the end. No test, no
Check and no CI step changes.

## Done when
- [x] The Check, as written in SPEC.md, passes: 37 passed in one `pytest app/tests` run
- [x] `pytest app/tests/test_ep10_shipping.py` and `pytest app/tests/e2e` still pass on their own

## Touches
app/tests/e2e/conftest.py

## Out of scope
Changing SPEC.md's Check or CI, async Playwright, pytest-asyncio, changing any test.
