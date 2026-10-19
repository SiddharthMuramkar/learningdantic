# 05 page
Status: todo

## What and why
A page you can click, teaching episode 05. Wave 2, after 01. No framework, no build step, no streaming.
app/static/index.html + app/static/app.js (about 25-40 lines, written to be read line by line): the `#user`
select sets the X-Demo-User header; `#subject` + `#new-ticket` POST /tickets; `#message` + `#send` POST
/tickets/{id}/messages; each line is appended to `#log` as `div[data-testid=user-message]` or
`div[data-testid=assistant-message]` using `textContent` only; an error shows its status code. If a reply has an
`approval`, call `window.showApproval?.(ticketId, approval)` (spec 07 defines it). Keep the ids from contract.md.
Episode 05 teaches: HTML elements and ids, `fetch` with a POST body and a header, `await` in the browser
(the same one rule as in the notebooks), the browser's dev tools Network tab, and why `textContent`.
Your piece: `sendMessage` in app.js (its red/green check arrives with spec 09's Playwright test; until then,
check it by hand in the browser).

## Done when
- [ ] test_ep05_page.py: GET / returns the page with every contract id and loads app.js and approvals.js
- [ ] By hand with the app running: ada creates a ticket, sends a message, sees the reply (keyless TestModel)
- [ ] track/05-page/EPISODE.md in the contract format
- [ ] The Check passes; /code-review and /security-review run, real findings fixed

## Touches
app/static/index.html, app/static/app.js, app/tests/test_ep05_page.py, track/05-page/EPISODE.md

## Out of scope
approvals.js and the approval card (spec 07). CSS beyond a few readable lines. Any JS library.
