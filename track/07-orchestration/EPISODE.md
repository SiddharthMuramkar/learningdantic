# 07: Who holds the wheel
**You'll see:** the same billing question answered three ways, and a count of model requests that shows what each way costs. **Time:** 30-45 min. **With me:** `/episode 07` (tour) or `/episode 07 do` (your piece)

## Run it
Start Postgres first if it is not running: `docker compose up -d --wait`. The test setup needs it.

1. Answer one question three ways. Each line is one pattern and the number of model requests it made.
   ```bash
   uv run --group app python -m app.patterns
   ```
   > ✅ Checkpoint: three lines, `one_agent`, `code_routing` and `delegation`, each with a request count. Cover the numbers and do **Predict** first. Without a key in `.env` the answers are `TestModel` placeholders and the last line says the live part was skipped. Only the counts are real. With a key, the same command makes real requests and adds a line per pattern with tokens and cost.
2. Run the locked test. It scripts every model, so it needs no key.
   ```bash
   uv run --group app pytest app/tests/test_ep07_orchestration.py
   ```
   > ✅ Checkpoint: `2 passed`. The first test asserts all three counts, and that `code_routing` makes fewer requests than `delegation`.

## Read
- `app/patterns.py:54`: `code_routing`. Your code asks a small classifier for a label, then `match` picks who answers. The model never chooses the next step.
- `app/patterns.py:43`: the delegation tool. `usage=ctx.usage` puts the expert's request on the same bill as the front desk's. `usage_limits=ctx.usage_limits` makes the expert obey the same cap.
- `app/agents.py:78`: `ask_billing`. The real desk delegates to the billing expert the same way.

## Predict
- Step 1: how many model requests does `one_agent` make?
- Step 1: how many does `code_routing` make? Count the classifier and the expert.
- Step 1: how many does `delegation` make? Count every model call, including the one inside the tool.

## Break it
In `app/patterns.py:43`, delete `usage=ctx.usage, `. Guess which count changes, then run the test from step 2. The answer is still right, so why is that a bug? Undo with `git restore .`.

## Your piece
`code_routing` in `app/patterns.py:54`. Replace its body with `raise NotImplementedError("your piece")`, run the test and watch it go red, then write the body again until it is green:
```bash
uv run --group app pytest app/tests/test_ep07_orchestration.py
```
1. Your code holds the wheel. Ask a small agent for a label first, then let Python choose who answers.
2. One `RunUsage()` and the shared `BUDGET` go into every run, so the request count includes the expert. Use `match kind:` on the label.
3. Run `classifier` with `usage=bill, usage_limits=BUDGET`. `case "billing":` runs `billing_expert` the same way, and `case _:` sets the answer to `"Passed to a human."`. Save the bill with `BILLS["code_routing"] = bill` (only the live print reads it) and return `answer, bill.requests`.

## Words
- **Delegation**: an agent calls another agent from a tool, then keeps talking. The model holds the wheel.
- **Code routing**: your code picks who answers. The model only gives a label.
- **Workflow**: one word, two meanings. For Anthropic it is fixed steps in code with model calls inside, like `code_routing`. For Temporal it is code that survives a crash. Ask which one is meant.
- **Handoff**: passing the conversation on. In OpenAI's Agents SDK it is one-way, and the first agent does not get it back. Pydantic AI says "programmatic hand-off" when your code calls agents one after another.
- **Swarm**: mostly a marketing word for many agents.

Add agents only when a count shows it helps. Here the second agent cost one extra request in `code_routing` and two in `delegation`.

Parallel: when a model asks for several tools in one reply, Pydantic AI runs them at the same time. You write nothing for it, and this episode does not use it.
