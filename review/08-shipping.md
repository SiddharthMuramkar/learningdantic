# Review: 08 shipping

PR: branch `08-shipping` (title "08 shipping"). Built from `specs-base`, merged with `origin/main` after 01 (#6), 02, 05 and 04 (#10) landed.

## What I built
- `app/evals.py`: `answer(text)` (opens a ticket for ada in its own short DB session, then `await run_desk(...)`) and `desk_evals` (cases `refund`, `status`, `late_parcel`; shared `IsInstance("str")` + `Contains("Reply HELP")`; `ToolCorrectness` per case; `late_parcel` expects `["lookup_order", "ask_shipping"]`). Ported from notebook 14.
- `app/agents.py`, appended below `# --- spec 08 appends below this line ---` only: `shipping_expert` (policy in its own instructions, on `AGENT_MODEL` like `billing_expert`), `shipping_rule` (an `@desk.instructions` function: one more line for the desk, because `RULES` is 04's and I may only add), and `async ask_shipping` on `desk_tools` (forwards `usage` and `usage_limits`).
- `app/tests/test_ep10_shipping.py` (3 tests): parcel ticket calls `ask_shipping`, the expert's sentence is in the reply, `result.usage.requests == 3`, the audit log holds `lookup_order` + `ask_shipping`, the instructions mention shipping; a customer is offered `ask_shipping` and still not `issue_refund`; `await desk_evals.evaluate(answer)` is 100% keyless with a scripted `FunctionModel` desk (the scripted model lives in the test file).
- `track/10-brief-the-agent/EPISODE.md` (72 lines): brief exercise, template, model-answer brief.
- `specs/08-shipping.md`: Done-when ticked, `Status: done`.

## Commands and results
| Command | Result |
|---|---|
| `git switch -c 08-shipping`, `git branch -D claude/08-shipping-895108` | ok |
| `uv run ruff check . && uv run ruff format --check .` (before 01 landed) | `I001` import order + 2x `E501` in my files; fixed the long lines. The import-order finding was only because `app/__init__.py` did not exist yet (`app` looked third-party); re-checked with `--config "lint.isort.known-first-party=['app']"`: clean |
| Same ruff after merging 01/04 | `All checks passed!`, `80 files already formatted` |
| `uv run --group app pytest app/tests/test_ep10_shipping.py -s` against a throwaway stand-in for 04 (never committed, restored with `git checkout -- app/agents.py`) | 3 passed; eval table 100.0% |
| Same against the real 04 `agents.py` + my additions | `3 passed`; table: refund `requests: 3 ✔✔✔`, status `requests: 2 ✔✔✔`, late_parcel `requests: 3 ✔✔✔`, Averages `100.0% ✔` |
| Red check A: `ask_shipping` without `@desk_tools.tool` | 3 failed (reply lacks the expert's sentence; `ask_shipping` not offered; eval 0.888 != 1.0). Restored: 3 passed |
| Red check B (the episode's Break-it): `shipping_expert.run(question)` with no usage forwarding | `test_parcel_ticket_asks_shipping` fails with `assert 2 == 3`; 2 others pass. Restored: 3 passed |
| `uv run python scripts/check_notebooks.py` | `checked 29 notebooks, 0 problem(s)` |
| `uv run --group app pytest app/tests --ignore=app/tests/e2e` | `20 passed` |
| `/code-review` (medium) | 5 findings, see below |
| `/security-review` | no finding with confidence >= 8. Reasoning: the new code runs fixed ORM inserts, passes a model-written question to a sub-agent that has no tools, and adds static instructions; the tests are excluded |

## Never ran / red
- `uv run pytest` over the notebooks and the e2e tests (09's): not run here; CI runs the keyless notebooks.
- The Break-it was run only for the `-k parcel_ticket` test, with the symptom `assert 2 == 3` as the episode says.
- No live model call, no uvicorn, no Logfire UI. Nothing is red.

## Guesses and decisions
- **Rule line**: spec says "one line in the desk's instructions". 04's `RULES` is a constant I must not edit, so I added an `@desk.instructions` function. In the keyless test `info.instructions` contains it (checked with `"shipping" in shown[0]`). Wording says "late, lost or missing parcel" (as solution 14), so the `status` case ("Has order 1042 arrived yet?") stays a plain lookup.
- `late_parcel` input uses order 1042 (ada's only order, status delivered): "Order 1042 says delivered, but my parcel never arrived." The scripted desk always looks up 1042.
- Tests are `async def` with `@pytest.mark.anyio` (anyio's plugin ships with the env; default backend asyncio), so there is no `asyncio` import (AGENTS.md rule). If someone adds pytest-asyncio with `asyncio_mode=auto`, the two plugins may fight; use one of them.
- `shipping_expert` is built on `AGENT_MODEL` like `billing_expert`. In keyless demo mode (`"test"`) its answer is TestModel's default text; I did not give it a canned sentence there.
- `@desk_tools.tool` after `desk` is built works because the filtered toolset holds `desk_tools` by reference (the red/green checks above prove it).
- Spec path: the contract/spec say `track/10-brief-the-agent/`; used that.

## Notes for the lead
- conftest on main now derives `acme_<8 hex of sha1(repo root)>_test` (4e00962); I used it as is (`acme_97e6e6e3_test`). Before that landed I ran once with the old fixed name via `ACME_TEST_DB=acme_08_test` and dropped that database afterwards.
- `specs/contract.md` fails `ruff format --check` on the base commit (ruff 0.17 formats markdown code blocks). 01 fixed it with `extend-exclude = ["specs"]` in pyproject, so it is fine on main.

## Code-review findings (medium) and what I did
1. EPISODE.md had `LINE_*` placeholders: fixed (lines 159, 170, 175 in agents.py, 44 in evals.py).
2. `fake_desk` repeats its tool calls if the last message is a retry prompt: skipped; the scripted desk never writes a promise word, so no retry happens.
3. `answer()` assumes a `Reply` output (a `DeferredToolRequests` has no `.message`): skipped; customers never see `issue_refund`.
4. Module-level `shown` list: skipped; `scripted()` clears it for each use.
5. The "offered" test relies on TestModel's default output passing 04's validator: skipped; it passes today.

## Sources
- Context7 `/pydantic/pydantic-ai`: evals (`Dataset`, `Case`, `IsInstance`, `Contains`, `ToolCorrectness` / agentic evaluators), agent delegation (`usage=ctx.usage`), `@agent.instructions`.
- Installed signatures (`inspect.signature`, pydantic-ai 2.57 / pydantic-evals): `Dataset.evaluate`, `ToolCorrectness`, `Case`, `FunctionModel`, `Agent.override`, `Agent.instructions`, `AgentInfo`; `dataclasses.fields(EvaluationReport)` (`cases`, `failures`).
- Notebook `notebooks/14_capstone_support_desk.ipynb` and `solutions/14_capstone_extension.ipynb` (ported code); `origin/01-skeleton` stubs and conftest; 04's `review/04-agent.md`.
