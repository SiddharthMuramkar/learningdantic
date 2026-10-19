# 08 shipping
Status: done

## What and why
Notebook 14's exercise, for real, as episode 10: you brief the agent. Wave 3, after 04.
In app/agents.py add a `shipping_expert` agent (its policy in its own instructions) and an async `ask_shipping`
tool on the desk that forwards usage and usage_limits; one line in the desk's instructions sends parcel and
delivery questions to shipping. In app/evals.py port notebook 14's `desk_evals` Dataset (refund and status cases,
IsInstance + Contains "Reply HELP", ToolCorrectness per case) against the app's desk, plus a `late_parcel` case
expecting ["lookup_order", "ask_shipping"]. `answer(text)` creates a ticket for ada and runs `run_desk`.
Keyless: a scripted FunctionModel desk follows the rules, so every case passes.
EPISODE.md is written as a brief exercise: "On a play branch, /episode 10 do removes the shipping expert. Write
your brief to Claude (template given), then check it against the locked test." Include a model answer brief.
Your piece: `ask_shipping` plus `shipping_expert` (both removed in do mode).

## Done when
- [x] test_ep10_shipping.py: a parcel ticket calls ask_shipping, the expert's answer reaches the reply,
      result.usage.requests counts the expert, and `await desk_evals.evaluate(answer)` scores 100% keyless
- [x] Removing ask_shipping turns the test red (checked, then restored)
- [x] track/10-brief-the-agent/EPISODE.md
- [x] The Check passes; /code-review and /security-review run, real findings fixed

## Touches
app/agents.py (additions only, below spec 04's code), app/evals.py, app/tests/test_ep10_shipping.py, track/10-brief-the-agent/EPISODE.md

## Out of scope
Changing R1-R6 or run_desk. Live evals (a stretch line in the episode only).
