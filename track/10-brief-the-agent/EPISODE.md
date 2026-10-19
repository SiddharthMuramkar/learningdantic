# 10: Brief the agent
**You'll see:** you write the brief, a coding agent adds a shipping expert to the desk, and a test plus an eval prove it worked. **Time:** 30-45 min. **With me:** `/episode 10` (tour) or `/episode 10 do` (your piece)

## Run it
Start Postgres first if it is not running: `docker compose up -d --wait`. You need no API key: a scripted model plays the desk, and both experts answer with a fixed sentence.

1. Run the episode's test. `-s` lets you see the eval table it prints.
   ```bash
   uv run --group app pytest app/tests/test_ep10_shipping.py -s
   ```
   > ✅ Checkpoint: `3 passed`, and a table called `Evaluation Summary: scripted desk` with three rows: `refund`, `status` and `late_parcel`. Each row has all its checks ticked, and the Averages row says `100.0% ✔`.
2. Run only the first test. It opens a parcel ticket for Ada and runs the real desk on it.
   ```bash
   uv run --group app pytest app/tests/test_ep10_shipping.py -k parcel_ticket
   ```
   > ✅ Checkpoint: `1 passed`. The test checked four things: the expert's sentence is in the reply, the run used 3 model requests, the audit log holds `lookup_order` and `ask_shipping`, and the desk was told about shipping.

## Read
- `app/agents.py:159`: `shipping_expert`. The shipping policy (7 days, then a free new parcel) lives here and nowhere else. The one line that sends parcel questions to it is `shipping_rule` (line 170).
- `app/agents.py:175`: `ask_shipping` runs the expert and forwards `usage` and `usage_limits`, so the expert counts toward the desk's six-request budget.
- `app/evals.py:44`: the `late_parcel` case. It lists the two tools that ticket must use.

## Predict
- Step 1: how many model requests does the parcel ticket use? (The desk asks its model twice. The expert is asked once.)
- Step 1: if `ask_shipping` did not exist, which row of the eval table would fail?
- Step 2: which tool would be missing from the audit log if the desk skipped the shipping expert?

## Break it
In `app/agents.py`, in `ask_shipping`, change the expert's run to `await shipping_expert.run(question)`, so it no longer gets `usage=ctx.usage, usage_limits=ctx.usage_limits`. Guess the symptom, then run:
```bash
uv run --group app pytest app/tests/test_ep10_shipping.py -k parcel_ticket
```
The reply is still right, but the test says `assert 2 == 3`. The expert's request is on nobody's bill, and the six-request limit can no longer stop a stuck expert. Undo with `git restore .`.

## Your piece
This time you do not write the function. You write the **brief**. On a play branch, `/episode 10 do` removes `shipping_expert`, `shipping_rule` and `ask_shipping` from `app/agents.py`. You write a brief, give it to Claude, and check what Claude builds with the locked test:
```bash
uv run --group app pytest app/tests/test_ep10_shipping.py
```
Fill every slot of this template. A slot left as `<...>` makes the agent stop and ask, because it must never invent your design.
```text
Goal: <what a customer sees after the change>
Where: <the file, and the names of the objects to add>
Rules: <each rule, and the ONE place it lives: expert instructions, desk instructions or code>
Check: <the command that must pass>
Do not: <what must stay as it is>
```
Hints, from vague to exact:
1. A good brief says where each rule lives. The shipping policy belongs to the expert. "Parcel questions go to shipping" belongs to the desk.
2. Name the tool, say it is `async def`, and say it must pass the usage on. Otherwise the expert's requests are not counted.
3. Say what not to touch: `run_desk`, `billing_expert`, `issue_refund`, and every test.

A model brief, to compare with yours after you have written it:
```text
Goal: A customer who asks about a late, lost or missing parcel gets the shipping expert's answer in the desk's reply.
Where: app/agents.py, below the line "# --- spec 08 appends below this line ---". Add an agent shipping_expert, an async tool ask_shipping(question) on the desk, and one line in the desk's instructions.
Rules:
- The shipping policy (parcels take up to 7 days, then Acme sends a new one for free) lives only in shipping_expert's own instructions.
- "Parcel questions go to shipping" lives only in the desk's instructions.
- ask_shipping forwards usage=ctx.usage and usage_limits=ctx.usage_limits.
Check: uv run --group app pytest app/tests/test_ep10_shipping.py
Do not: change run_desk, billing_expert, issue_refund, anything above that line, or any test.
```
*Stretch (needs your own key, spends a little):* run `desk_evals` on your real `MODEL` instead of the scripted one. Does the real model pick the right expert every time?

## Words
- **Brief**: the written task you give a coding agent: goal, place, rules, check and limits.
- **Specialist**: a second agent the desk calls like a tool. It holds one topic's policy.
- **Eval**: a list of example tickets (a `Dataset` of `Case`s) that you run again after every change.
- **ToolCorrectness**: an eval check that a ticket used exactly the tools you listed.
- **Request budget**: the cap on model requests for one ticket. The specialists draw from the same budget.
