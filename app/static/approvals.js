// The approval card. app.js calls window.showApproval when a reply carries an approval.
window.showApproval = (ticketId, approval) => {
  const log = document.querySelector("#log");
  const addLine = (testid, text) => {
    const div = document.createElement("div");
    div.dataset.testid = testid;
    div.textContent = text; // textContent, never innerHTML: the text is data, not markup
    log.append(div);
    return div;
  };
  const dollars = (approval.amount_cents / 100).toFixed(2);
  const card = addLine("approval-card", `Refund $${dollars} for order ${approval.order_id}? `);
  for (const [label, decision] of [["Approve", "approve"], ["Reject", "reject"]]) {
    const button = document.createElement("button");
    button.textContent = label;
    button.onclick = async () => {
      const buttons = card.querySelectorAll("button");
      buttons.forEach((b) => (b.disabled = true));
      const response = await fetch(`/tickets/${ticketId}/approvals/${approval.refund_id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Demo-User": document.querySelector("#user").value,
        },
        body: JSON.stringify({ decision }),
      });
      const reply = await response.json().catch(() => ({}));
      addLine("assistant-message", response.ok ? reply.message : `Error ${response.status}`);
      if (!response.ok) buttons.forEach((b) => (b.disabled = false));
      if (reply.approval) window.showApproval(ticketId, reply.approval); // the desk asked again
    };
    card.append(button);
  }
};
