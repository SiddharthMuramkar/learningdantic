# 10 bug hunt
Status: todo

## What and why
The exam, episode 11: three planted bugs, symptoms only. Wave 4, after 07. Markdown and patch files only.
track/11-bug-hunt/bugs/ holds three `git apply`-able patches against main, each a silent mistake the course
warned about, each in a file that spec 09 does not touch:
1. memory.save stores only the new messages, so the second turn forgets usage (test_ep04 goes red)
2. execute_refund drops `AND status='approved'`, so a double approve executes twice (test_ep08 goes red)
3. the orders query forgets the customer filter, so ada can read bo's order (test_ep03 goes red)
track/11-bug-hunt/EPISODE.md: `/episode 11` applies one patch on a play branch without showing it; he gets the
symptom (the red test name and its message) and a hint ladder (where to look: the test, the trace, psql); he says
the root cause in one sentence, fixes it, the test goes green; `git restore .` and the next bug. An honour-system
note: don't open bugs/ first. Answers in a collapsed section at the end.

## Done when
- [ ] Each patch applies cleanly to main and turns exactly the named test red; reverting makes it green (checked)
- [ ] track/11-bug-hunt/EPISODE.md exists
- [ ] The Check passes on main (patches are never applied there); Markdown and patches only, so no code reviews

## Touches
track/11-bug-hunt/

## Out of scope
Changing app code or tests. Hiding the answers (git can't hide them; this is an honour system).
