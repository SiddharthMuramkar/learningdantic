# 07 approvals
Status: todo

## What and why
A refund waits for a person, across two HTTP requests. Episode 08. Wave 3, after 04 and 05.
app/approvals.py: `record_pending` stores one `refunds` row per approval in the stored DeferredToolRequests
(amount from the orders row, unique per ticket + tool_call_id) and returns its ApprovalOut. `execute_refund`
runs `UPDATE refunds SET status='executed' WHERE ticket_id=:t AND tool_call_id=:c AND status='approved'` and
fails loudly if 0 rows changed.
app/routes/approvals.py: `POST /tickets/{ticket_id}/approvals/{refund_id}` (async def, StaffDep). The body is
only `{decision}`. Check the refund belongs to the ticket and is pending (else 409: that is the double click),
set it approved or rejected, then build the results from the STORED conversation's deferred_tool_requests
(`build_results(approvals={call_id: True})`, or a ToolDenied on reject) and resume with
`run_desk(ticket_id, user, None, deferred_tool_results=...)`. Never pass client data into override_args.
app/static/approvals.js: defines `window.showApproval(ticketId, approval)`, which draws the approval card
(order and amount from the API, textContent only) with Approve and Reject buttons that POST the decision.
Live check: one staff refund chat on the real MODEL only if `has_key(MODEL)`; report cost (stop if None).
Your piece: `execute_refund`.

## Done when
- [ ] test_ep08_approvals.py: sam's refund chat returns an approval; the refund row is pending and NOT executed;
      approve -> executed exactly once; a second approve -> 409; reject -> status rejected, nothing executed;
      ada calling the approve route -> 403; a refund from another ticket -> 409
- [ ] Blanking `execute_refund` turns the test red (checked, then restored)
- [ ] track/08-approvals/EPISODE.md in the contract format (break it: approve twice)
- [ ] The Check passes; /code-review and /security-review run, real findings fixed

## Touches
app/approvals.py, app/routes/approvals.py, app/static/approvals.js, app/tests/test_ep08_approvals.py, track/08-approvals/EPISODE.md

## Out of scope
Expiry, args hashes, the Vercel/AG-UI adapters, real login, changes to agents.py or app.js.
