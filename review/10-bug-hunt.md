# Review: 10 bug hunt

Branch `10-bug-hunt`, PR title "10 bug hunt". Markdown and patch files only. `Status` in `specs/10-bug-hunt.md`
stays `todo` for two reasons, both explained below. Bug 2 is not the bug the spec names: the spec's version turns
nothing red, and the substitute is loud, not silent. And the Check as written in SPEC.md fails on main for a
reason outside this spec.

## What I built
- `track/11-bug-hunt/EPISODE.md` (118 lines, the contract's section layout): plant a bug on `play-ep11`, read
  the red test, guess, say the root cause in one sentence, fix, `git restore .`, next bug. The honour-system note
  is at the top. Each bug has three hints from vague to exact; hints 2 and 3 are collapsed. The Read section
  names the three places to look (the test, the traceback, psql on the kept test database). The answers, with the
  exact symptoms, are in a collapsed `<details>` at the end. Read has no `path:line` on purpose: a line number
  would point at the planted bug.
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
Everything ran on branch `10-bug-hunt` after merging origin/main at `a1ff67c` (01-09 merged). Patches went on with `git apply`
and came off with `git restore .`, in this worktree only. I checked `git diff --quiet` before and after each one.
Tests used this checkout's database, `acme_772b7a5e_test`.

| Command | Result |
|---|---|
| background poll: `git fetch origin && git log origin/main --oneline` every 60 s | 01 at 10:14, 04 at 10:26, 03 and 07 at 10:27 |
| `git merge origin/main` (twice, main moved during the work) | first: add/add conflicts in `specs/01..05,07, contract.md`, resolved by taking main's version; second: clean |
| `uv sync --group app` | ok |
| `uv run --group app pytest app/tests` on clean main (one process, as SPEC.md's Check says) | before 08 landed: 34 passed. At `a1ff67c`: **3 failed, 34 passed** (see What failed) |
| `uv run --group app pytest app/tests --ignore=app/tests/e2e`, then `pytest app/tests/e2e` (CI's split) on clean main | 33 passed, 4 passed: the baseline I compare against |
| each patch: `git apply --check`, `git apply`, both suites, `git restore .`, both suites again, diff per test vs baseline | see next table |
| `ACME_KEEP_TEST_DB=1 pytest <file> -x` with bug 2, then `docker compose exec -T db psql -U acme acme_772b7a5e_test -c 'select id, ticket_id, order_id, status from refunds;'` | one row, status `rejected` (the hint works) |
| same with bug 1, then the episode's exact zsh command `psql ... -c "select id, version, conversation->'usage' from tickets;"` | version 2, `"requests": 0` (the hint works) |
| bug 2 planted: `grep -n '"rejected"' app/routes/approvals.py` | two lines, 21 and 47 (the hint works) |
| bug-2 **plus** deleting `Refund.status == "approved"` in `execute_refund` (the tempting wrong fix) | **33 + 4 passed**: the wrong fix turns everything green; the episode now warns about it |
| read-only review workflow: 4 reviewers (accuracy, teaching, bug 2 design, patches + note), each followed by a skeptic that tried to refute every finding | 33 findings, 27 confirmed; all confirmed ones fixed in EPISODE.md and this note (list below) |
| `uv run ruff check .` / `uv run ruff format --check .` | All checks passed! / 92 files already formatted |
| `uv run python scripts/check_notebooks.py` | checked 29 notebooks, 0 problem(s) |
| `gh pr create` | failed: this Mac's DNS server stopped answering (`nslookup api.github.com`: "no servers could be reached"); `git push` worked from cache |

| Patch | Applies to main | Red with the patch (vs baseline) | After `git restore .` |
|---|---|---|---|
| bug-1 | yes | `test_ep04_agent.py::test_usage_carries_over_and_the_version_counts_saves` only | identical to baseline |
| bug-2 | yes | `test_ep08_approvals.py::test_approve_executes_exactly_once`, and the browser test of the same click `e2e/test_ep09_playwright.py::test_sam_approves_a_refund[chromium]` | identical to baseline |
| bug-3 | yes | `test_ep03_fastapi.py::test_ada_reads_her_order_but_not_bos` only | identical to baseline |
| the spec's bug 2 (drop `Refund.status == "approved"` in `execute_refund`), scratch only, not shipped | yes | **nothing**: 33 + 4 passed | identical to baseline |

## What the review workflow changed
- `/episode 11 do`, not `/episode 11`: the merged skill (`.claude/skills/episode/SKILL.md`, "3. Do mode") plants
  patches only in do mode. The spec says `/episode 11`. Run it now also has the `git switch` and `git apply` as
  commands, so the tour works too. **Siddharth decides** whether the spec or the skill wording changes.
- The pass rule now says "never loosen a check", and bug 2's answer explains the wrong fix (above).
- "Silent bug" in Words now means "a line that looks right and raises no error itself; the damage shows up later
  and somewhere else". Bug 2 is still loud on the happy path (every Approve returns 500), so "each a silent
  mistake" holds only in that sense.
- The table holds the full locked-test commands, the psql template uses double quotes (the `'usage'` hint broke
  inside single quotes), the honour note adds `git status` and the editor's changed-files list, and hints 2-3 are
  collapsed.
- Answers corrected: bug 1 loses the ticket's running request and token count (the 6-per-turn limit still holds,
  because `run_desk` adds 6 to whatever was stored); bug 2 names the tool; bug 3 says `test_sam_reads_any_order`
  stays green. The Predict lines can now be checked from what the episode runs.

## What failed or never ran
- **The spec's bug 2 can't turn a test red on the merged code.** A second approve never reaches `execute_refund`:
  the route's guarded UPDATE finds no pending row, and its `if call_id not in answers` check returns 409 first.
  Spec 07's episode 08 already uses "remove both" as its Break it. So I tried once to fix it, as rule 3 says. I
  kept the spirit (a state-changing UPDATE drops its `status == ...` condition and the refund lifecycle breaks)
  and moved it to the sibling-reject UPDATE. That one goes red, has one root cause and is a line the learner has
  not broken before. **Siddharth decides** whether to keep this substitute.
- Bug 2 is loud: every Approve click returns 500. It also turns the e2e approve test red, because it breaks the
  approve click itself (the spec's literal patch, in the same flow, leaves all 4 e2e tests green).
- The locked test can't catch the tempting wrong fix for bug 2 (see the table above). The episode warns about it
  in words. Making a test catch it would mean changing spec 07's locked test, which is out of scope.
- **SPEC.md's Check fails on main** at `a1ff67c`, without any patch. In one `pytest app/tests` process the
  Playwright tests run first, and then the three `test_ep10_shipping.py` tests fail with
  `RuntimeError: Cannot run the event loop while another loop is running`. Run alone, `test_ep10_shipping.py` gives
  3 passed. CI runs the two suites separately, so CI is green. The test files belong to 08 and 09; this spec
  doesn't change them. A follow-up session is proposed.
- `/episode 11 do` was not run end to end, because it needs a person. I ran the plant, test and restore loop by hand.
- No live model calls; none are needed.

## Guesses
- Bug 1: the spec says "stores only the new messages". In the merged code `save` gets the whole
  `result.conversation`, and storing a message list would crash `load`. So the bug rebuilds the `Conversation`
  field by field and leaves out `usage`, which the spec names as the symptom. It keeps `deferred_tool_requests`,
  or the approvals tests would go red too. The Pydantic AI docs warn about exactly this loss ("Losing `usage` is
  the one that bites").
- Bug 3: the spec says "the orders query forgets the customer filter". The route has no WHERE clause. It uses
  `session.get` and then an owner check, so the patch drops that check. Dropping the filter in `lookup_order`
  (agents.py) would turn test_ep04 red, not test_ep03.
- The patch names are neutral (`bug-1..3.patch`). Once a bug is planted, `git status` names the changed file, and
  the honour note asks the learner not to look.
- The episode's psql hints use the test database kept with `ACME_KEEP_TEST_DB=1`, not the dev database. conftest
  supports that variable, and the pytest header prints the database's name.

## Sources
- Context7 `/pydantic/pydantic-ai`: docs/persistence.md and docs/message-history.md ("Carrying a conversation
  whole": `result.conversation`, `ConversationTypeAdapter`, and why storing messages without `usage` resets
  `UsageLimits`).
- Installed signature (pydantic_ai 2.57.0): `Conversation(*, messages, usage, conversation_id, deferred_tool_requests)`.
- Merged code I read: `app/memory.py`, `app/approvals.py`, `app/routes/approvals.py`, `app/routes/tickets.py`,
  `app/agents.py`, `app/routes/chat.py`, `app/tests/conftest.py`, the ep03/ep04/ep08 tests,
  `review/07-approvals.md`, `track/08-approvals/EPISODE.md`, `.claude/skills/episode/SKILL.md`, `.github/workflows/ci.yml`.
- specs/contract.md, specs/10-bug-hunt.md, SPEC.md.
