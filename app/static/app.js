// The page's brain: two helpers, two actions, two click handlers. No library, no build step.
const $ = (id) => document.getElementById(id);
let ticketId = null; // set by newTicket(), used by sendMessage()

// Add one line to the log. textContent shows the text exactly as typed: a "<b>" or "<script>" stays inert.
function addLine(kind, text) {
  const line = document.createElement("div");
  line.dataset.testid = `${kind}-message`; // becomes data-testid="user-message"; tests find lines by it
  line.textContent = text;
  $("log").append(line);
}

// POST a JSON body with the demo-login header. fetch() returns a promise; await waits for it.
async function post(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Demo-User": $("user").value },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`Error ${response.status}`);
  return response.json();
}

async function newTicket() {
  const ticket = await post("/tickets", { subject: $("subject").value });
  ticketId = ticket.id;
  $("log").replaceChildren(); // a new ticket starts a new conversation
  addLine("system", `Ticket #${ticket.id}: ${ticket.subject}`);
}

async function sendMessage() {
  if (ticketId === null) throw new Error("Create a ticket first");
  const text = $("message").value;
  addLine("user", text);
  $("message").value = "";
  const reply = await post(`/tickets/${ticketId}/messages`, { text });
  if (reply.message) addLine("assistant", reply.message); // message is null while a refund waits
  if (reply.approval) window.showApproval?.(ticketId, reply.approval); // approvals.js draws the card
}

// Run an action; a failure becomes a line in the log (with its status code) instead of a silent console error.
const guarded = (action) => () => action().catch((error) => addLine("error", error.message));
$("new-ticket").onclick = guarded(newTicket);
$("send").onclick = guarded(sendMessage);
