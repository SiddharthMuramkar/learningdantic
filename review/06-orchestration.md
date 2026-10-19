# Review: 06 orchestration

PR: branch `06-orchestration` (title "06 orchestration"). Built from `specs-base`. I wrote it before 01 landed and proved it on a stand-in package. Then I merged `origin/main` after 01, again after 04, and once more after 03, 07, 08 and 09.

## What I built
- `app/patterns.py`: one billing question (`QUESTION`), three ways to answer it. Each returns `(answer, model requests)`.
  - `one_agent`: one agent (`solo`), no tools and no specialist. 1 request.
  - `code_routing` (episode 07's piece): a `classifier` agent with `output_type=Literal["billing", "shipping", "other"]`. A `match` on its label sends `"billing"` to `billing_expert` from `app/agents.py`; anything else is `"Passed to a human."`. One `RunUsage()` bill and the shared `BUDGET = UsageLimits(request_limit=4)` go to both runs. 2 requests.
  - `delegation`: a `front_desk` agent whose `async def ask_billing` tool runs `billing_expert` with `usage=ctx.usage, usage_limits=ctx.usage_limits`. 3 requests.
  - `main()` (`uv run --group app python -m app.patterns`) prints the three counts. If `has_key(MODEL)`, it also prints tokens and cost for each pattern from a module-level `BILLS` dict, and stops with `SystemExit` if a cost is `None`. Otherwise it says the live part was skipped.
- `app/tests/test_ep07_orchestration.py`: every model scripted with `FunctionModel`, keyless. The first test asserts that all three answers carry the expert's "5 days", that the counts are exactly 1, 2 and 3, and that `code_routing` < `delegation`. The second test asserts that an "other" label gives `("Passed to a human.", 1)`.
- `track/07-orchestration/EPISODE.md`: the contract format. Predict = the three counts. Break it = delete `usage=ctx.usage, ` from the tool. Your piece = `code_routing`. Words: delegation, code routing, workflow, handoff, swarm. Then the "count first" note and a one-line note on Pydantic AI's own parallel tool calls.

## Commands and results
- `git switch -c 06-orchestration`, `git branch -D claude/06-orchestration-887b7f`: ok.
- Before 01: `uv run ruff check .` flagged I001, because `app` was not a package yet. It went away once 01 landed. E501 lines fixed.
- Stand-in proof (scratchpad copy with a fake `app/__init__.py` and `app/agents.py`): `pytest` 2 passed. The demo printed 1, 2 and 3 on `TestModel`. `MODEL=test` gave `stop: no cost for MODEL=test`. Blanking `code_routing` gave 2 failed. Dropping `usage=ctx.usage` gave `delegation': 2 != 3`.
- After 01 and 04 landed, on the real app:
  - `uv run ruff check . && uv run ruff format --check .`: all checks passed, 93 files already formatted.
  - `uv run python scripts/check_notebooks.py`: 29 notebooks, 0 problems.
  - `uv run --group app pytest app/tests/test_ep07_orchestration.py`: 2 passed.
  - `uv run --group app pytest app/tests --ignore=app/tests/e2e` (the CI command): 35 passed.
  - `uv run --group app pytest app/tests` (the SPEC.md Check, e2e included): **5 failed, 34 passed** (see below).
  - Blank `code_routing`: 2 failed with `NotImplementedError: your piece`. Restored: 2 passed.
  - Break it (delete `usage=ctx.usage, `): `delegation': 2` vs `3`, as the episode says. Restored.
  - `uv run --group app python -m app.patterns`: a key was set in this checkout's environment (`.env` was never opened), so the run was live. Counts 1, 2, 3. Cost: one_agent 43 tokens in, 201 out, $0.002096; code_routing 164 in, 58 out, $0.000908; delegation 378 in, 161 out, $0.002366. About half a cent in total.
- `/code-review` (high): 7 findings. Fixed: `code_routing` now records its bill after the runs, not before. The import break went away once 04 landed. The rest are skipped (see Known gaps).
- `/security-review`: no findings.

## What failed or went wrong
- **The full Check is red, and not in my files.** With `app/tests/e2e` collected first, `test_ep07_orchestration.py` (2 tests) and `test_ep10_shipping.py` (3 tests) fail with `RuntimeError: Runner.run() cannot be called from a running event loop`. `pytest app/tests/e2e app/tests/test_ep07_orchestration.py` gives 2 failed. The reverse order gives 6 passed. Playwright's sync API (09's e2e fixtures) leaves an event loop running for the rest of the pytest session. CI is green because its app job uses `--ignore=app/tests/e2e`. A fix belongs in 09's e2e setup or in the Check (run e2e in its own `pytest` call). I left `Status: todo` and the Check line unticked for this reason.
- My first background wait loop detached, because it had an `&` inside a background command. I restarted it properly.

## Never ran or not verified
- I could not check the Words lines about Anthropic's and Temporal's "workflow", OpenAI's one-way "handoff" and "swarm" against their own pages. Those domains are outside this run's allowed list. The wording comes from the spec. "Programmatic hand-off" and the parallel tool calls are checked against the Pydantic AI docs.
- The `/episode 07` skill tour itself (spec 02) was not run.

## Guesses
- I did not use `desk`. The parent brief said the patterns call `desk`, but my spec names only `billing_expert`. `desk` already delegates (its `ask_billing` is at `app/agents.py:78`), and its audit hook writes rows for a real ticket. The episode points at it in **Read** instead.
- `billing_expert` takes no deps and returns `str`. Both held once 04 landed.
- `BILLS` is a module-level dict, so the live print can read tokens and cost without changing the contract signature `(text) -> tuple[str, int]`.
- `main()` and the test use `anyio.run`, because a script needs an event loop and `asyncio` is off limits here. anyio is only a transitive dependency (via httpx and starlette).
- The classifier labels match `Reply.category` (`billing`, `shipping`, `other`). Only `billing` has a specialist here.

## Known gaps (skipped code-review findings)
- `BILLS` is shared module state (AGENTS.md prefers deps for per-run things). It is used only by the demo print.
- With `MODEL=test`, the live part stops at the first `cost is None`, by design ("stop if cost is None").
- EPISODE.md cites `app/patterns.py:43` and `:54`. They drift if the file changes.
- The scripted front desk reads `messages[-1].parts[0].content` (the tool return).

## Sources
- Context7 `/pydantic/pydantic-ai`: "Agent delegation" and "Programmatic agent hand-off" (docs/multi-agent-applications.md), `UsageLimits` (usage.py), "Parallel tool calls & concurrency" (docs/tools-advanced.md).
- `notebooks/11_multi_agent.ipynb`: the delegation, `Literal` classifier + `match`, and `FunctionModel` scripting patterns.
- Installed signatures (`uv run python -c "import inspect ..."`): `Agent.run(..., usage_limits=, usage=, deps=, ...)`; `RunUsage` has `requests`, `input_tokens`, `output_tokens`, `cost`; `AgentRunResult.usage`.
