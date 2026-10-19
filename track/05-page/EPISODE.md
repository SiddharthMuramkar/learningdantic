# 05: The page

**You'll see:** a plain web page where you open a ticket, chat with the desk, and watch the browser talk to FastAPI.
**Time:** 30-45 min. **With me:** `/episode 05` (tour) or `/episode 05 do` (your piece)

Two files make the whole page: `index.html` (the parts) and `app.js` (what the parts do). No framework, no build step.

## Run it

Use two terminal tabs: one for the server, one for everything else.

1. Start the database, if it is not already up:
   ```bash
   docker compose up -d --wait
   ```
   > ✅ Checkpoint: the last line says `Container acme-desk-db-1 Healthy`.
2. Start the server (tab 1). Leave it running.
   ```bash
   uv run --group app fastapi dev app/main.py
   ```
   > ✅ Checkpoint: a line says `http://127.0.0.1:8000`.
3. Open <http://127.0.0.1:8000/> in your browser.
   > ✅ Checkpoint: a page called Acme Desk with "Signed in as ada", a Subject box, a log and a Message box.
4. Type a subject (`Where is my mug?`) and click **New ticket**. Type `Where is order 1042?` and click **Send**.
   > ✅ Checkpoint: the log shows `Ticket #<number>: Where is my mug?`, then your line, then a reply. No key in `.env`
   > means demo mode: a fake model answers, so the words look odd. That is fine; the round trip is the point.
5. Open the browser's dev tools (`Cmd+Option+I` in Chrome), click the **Network** tab. Type
   another message, click **Send**, then click the row called `messages`.
   > ✅ Checkpoint: **Headers** shows `x-demo-user: ada`, **Payload** shows `{"text": ...}`, **Response** shows
   > JSON with `ticket_id`, `category` and `message`. This is the whole conversation between page and server.
6. Switch **Signed in as** to `bo` and click **Send** on the same ticket.
   > ✅ Checkpoint: a red line, `Error 404`. The ticket is ada's, and the API hides other people's tickets.
7. Run the page's test (tab 2):
   ```bash
   uv run --group app pytest app/tests/test_ep05_page.py
   ```
   > ✅ Checkpoint: `2 passed`.

## Read

- `app/static/index.html:18`: the `<select id="user">`. The six ids on this page are a contract: `app.js`, the
  approval card and the browser tests all find things by them.
- `app/static/app.js:14`: `post()`. One `fetch` with a method, a header that says who you are, and a JSON body.
- `app/static/app.js:9`: `line.textContent = text`. The one way text enters the page.

## Predict

- Step 4: while you wait for the reply, can you still type in the Message box?
- Step 5: which header tells the server who you are?
- Step 6: what does bo see when sending on ada's ticket?

## Break it

In `app/static/app.js`, change line 9 to `line.innerHTML = text;`. Reload the page, make a ticket, and send
`<b>hello</b>`. Guess first: what does the log show for your line?

It shows **hello** in bold. The page ran your text as HTML. If a stranger's text ever lands there, it could
run code in your browser (that attack is called XSS). Run the test from step 7: it goes red too.
Undo with `git restore .`.

## Your piece

`sendMessage` in `app/static/app.js:31`. Blank its body (`/episode 05 do` does this for you), then rebuild it.

Its locked check arrives with episode 09 (`uv run --group app pytest app/tests/e2e`, whose first test sends a
message and waits for a reply). Until then, check by hand: Send must show your line, then a reply.

1. It does three things in order: show what you typed, ask the server, show the answer. `newTicket` just above
   has the same shape.
2. Asking is one line, `const reply = await post(...)`. The path is `/tickets/${ticketId}/messages` and the body
   is `{ text }`. Forget the `await` and `reply` is a promise: nothing shows, and no error appears.
3. Exact:
   ```js
   const reply = await post(`/tickets/${ticketId}/messages`, { text });
   if (reply.message) addLine("assistant", reply.message);
   if (reply.approval) window.showApproval?.(ticketId, reply.approval);
   ```

## Words

- **id**: a name for one element in the page. `$("log")` finds the element by it.
- **fetch**: the browser's built-in way to call a URL. With `method: "POST"` and a body it sends data.
- **await**: the same one rule as in the notebooks. Put it before a call that takes time; the page stays alive meanwhile.
- **header**: a named line of extra information sent with a request. `X-Demo-User` is our fake login.
- **textContent**: sets an element's text as plain text, never as HTML.
