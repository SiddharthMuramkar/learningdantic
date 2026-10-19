# Review: 10 bug hunt

Branch `10-bug-hunt`, PR title "10 bug hunt". Markdown and patch files only. `Status` in `specs/10-bug-hunt.md`
stays `todo`, for two reasons explained below: bug 2 is not the bug the spec names (the spec's version turns
nothing red), and the Check as written in SPEC.md fails on main for a reason outside this spec.

## What I built
- `track/11-bug-hunt/EPISODE.md` (91 lines, contract format): plant a bug on `play-ep11`, read the red test,
  guess, say the root cause in one sentence, fix, `git restore .`, next bug. The honour-system note is at the top.
  Each bug has a hint ladder (the test, the traceback, psql on the kept test database). The answers, with the exact
  symptoms, are in a collapsed `<details>` at the end.
- `track/11-bug-hunt/bugs/bug-1.patch` (`app/memory.py`): `save` rebuilds a `Conversation` from `messages`,
  `conversation_id` and `deferred_tool_requests`, and leaves out `usage`. The docstring still says "Store the
  whole conversation". Red: `test_ep04_agent.py::test_usage_carries_over_and_the_version_counts_saves`,
  `assert (0, 2) == (2, 2)`.
- `track/11-bug-hunt/bugs/bug-2.patch` (`app/routes/approvals.py`): the UPDATE that rejects the *other* pending
  refunds loses `Refund.status == "pending"`, so approving a refund also rejects it. `execute_refund` then
  finds no approved row and fails loudly. Red: `test_ep08_approvals.py::test_approve_executes_exactly_once`,
  `RuntimeError: refund pyd_ai_... on ticket 1 is not approved`.
- `track/11-bug-hunt/bugs/bug-3.patch` (`app/routes/tickets.py`): `get_order` keeps `if order is None` and drops
  the owner check. Red: `test_ep03_fastapi.py::test_ada_reads_her_order_but_not_bos`, `assert 200 == 404`.

None of the three files is touched by spec 09.

## What I ran
All on branch `10-bug-hunt` after merging origin/main at `a1ff67c` (01-09 merged). Patches were applied with
`git apply` and removed with `git restore .` in this worktree only; `git diff --quiet` was checked before and
after each one. Tests used this checkout's database `acme_772b7a5e_test`.

| Command | Result |
|---|---|
| background poll: `git fetch origin && git log origin/main --oneline` every 60 s | 01 at 10:14, 04 at 10:26, 03 and 07 at 10:27 |
| `git merge origin/main` (twice, main moved during the work) | first: add/add conflicts in `specs/01..05,07, contract.md`, resolved by taking main's version; second: clean |
| `uv sync --group app` | ok |
| `uv run --group app pytest app/tests` on clean main (one process, as SPEC.md's Check says) | before 08 landed: 34 passed. At `a1ff67c`: **3 failed, 34 passed** (see What failed) |
| `uv run --group app pytest app/tests --ignore=app/tests/e2e`, then `pytest app/tests/e2e` (CI's split) on clean main | 33 passed, 4 passed: the baseline I compare against |
| each patch: `git apply --check`, `git apply`, both suites, `git restore .`, both suites again, diff per test vs baseline | see next table |
| `ACME_KEEP_TEST_DB=1 pytest <file> -x` with bug 2, then `docker compose exec -T db psql -U acme acme_772b7a5e_test -c 'select id, ticket_id, order_id, status from refunds;'` | one row, status `rejected` (the hint works) |
| same with bug 1, `select id, version, conversation->'usage', jsonb_array_length(conversation->'messages') from tickets;` | version 2, `"requests": 0`, 6 messages (the hint works) |
| `uv run ruff check .` / `uv run ruff format --check .` | All checks passed! / 92 files already formatted |
| `uv run python scripts/check_notebooks.py` | checked 29 notebooks, 0 problem(s) |

| Patch | Applies to main | Red with the patch (vs baseline) | After `git restore .` |
|---|---|---|---|
| bug-1 | yes | `test_ep04_agent.py::test_usage_carries_over_and_the_version_counts_saves` only | identical to baseline |
| bug-2 | yes | `test_ep08_approvals.py::test_approve_executes_exactly_once`, and the browser test of the same flow `e2e/test_ep09_playwright.py::test_sam_approves_a_refund[chromium]` | identical to baseline |
| bug-3 | yes | `test_ep03_fastapi.py::test_ada_reads_her_order_but_not_bos` only | identical to baseline |
| the spec's bug 2 (drop `Refund.status == "approved"` in `execute_refund`), scratch only, not shipped | yes | **nothing**: 33 + 4 passed | identical to baseline |

## What failed or never ran
- **The spec's bug 2 can't turn a test red on the merged code.** A second approve never reaches `execute_refund`.
  The route's guarded UPDATE (`status == 'pending'`) and its `if call_id not in answers` check each return 409
  first, and spec 07's episode 08 already uses "remove both" as its Break it. So I tried once to fix, as rule 3
  says: I kept the spirit (a state-changing UPDATE drops its `AND status = ...`, and the refund lifecycle breaks)
  and moved it to the sibling-reject UPDATE, which is red, has one root cause and is new to the learner. The
  answers section mentions the spec's version and why it stays green. **Siddharth decides** whether to keep this
  substitute.
- Bug 2 also turns the e2e approve test red. Any bug in the approve flow does that; "exactly the named test" holds
  for the unit suite only.
- **SPEC.md's Check fails on main** at `a1ff67c`, without any patch: in one `pytest app/tests` process the
  Playwright tests run first and then the three `test_ep10_shipping.py` tests fail with
  `RuntimeError: Cannot run the event loop while another loop is running`. Alone, `test_ep10_shipping.py` gives
  3 passed, and CI runs the two suites separately, so CI is green. Owners: 08 (tests) and 09 (e2e). Not changed here.
- `/episode 11` itself was not run end to end (it needs a person). I ran the plant, test, restore loop by hand.
- No live model calls; none are needed.

## Guesses
- Bug 1: the spec says "stores only the new messages". In the merged code `save` gets the whole
  `result.conversation`, and storing a message list would crash `load`. So the bug rebuilds the `Conversation`
  from its messages (keeping `deferred_tool_requests`, or the approvals tests would go red too) and loses `usage`,
  the symptom the spec names and the one the Pydantic AI docs warn about ("Losing `usage` is the one that bites").
- Bug 3: the spec says "the orders query forgets the customer filter". The route has no WHERE clause. It uses
  `session.get` and then an owner check, so the patch drops that check. Dropping the filter in `lookup_order`
  (agents.py) would turn test_ep04 red, not test_ep03.
- Patch names are neutral (`bug-1..3.patch`) so a file listing gives nothing away. The skill from 02 only says
  "a patch from `track/11-bug-hunt/bugs/`".
- The episode's psql hint uses the test database kept with `ACME_KEEP_TEST_DB=1` (conftest supports it, and the
  pytest header prints its name), not the dev database.

## Sources
- Context7 `/pydantic/pydantic-ai`: docs/persistence.md and docs/message-history.md ("Carrying a conversation
  whole": `result.conversation`, `ConversationTypeAdapter`, and why storing messages without `usage` resets
  `UsageLimits`).
- Installed signature (pydantic_ai 2.57.0): `Conversation(*, messages, usage, conversation_id, deferred_tool_requests)`.
- Merged code read: `app/memory.py`, `app/approvals.py`, `app/routes/approvals.py`, `app/routes/tickets.py`,
  `app/agents.py`, `app/routes/chat.py`, `app/tests/conftest.py`, the ep03/ep04/ep08 tests,
  `review/07-approvals.md`, `track/08-approvals/EPISODE.md`, `.claude/skills/episode/SKILL.md`, `.github/workflows/ci.yml`.
- specs/contract.md, specs/10-bug-hunt.md, SPEC.md.
