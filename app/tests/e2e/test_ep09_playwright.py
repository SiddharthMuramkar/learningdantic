"""Episode 09: a real browser proves a refund waits for a person.

`page` is Playwright's browser tab and `app_url` is the running server (see conftest.py).
`expect(...)` waits and retries until the page matches, so these tests never sleep.
"""

from app.db import engine
from app.models import Refund
from playwright.sync_api import Page, expect
from sqlalchemy import select
from sqlalchemy.orm import Session


def new_ticket(page: Page, app_url: str, user: str) -> None:
    """Open the page as `user` and start a fresh ticket.

    Fresh matters: TestModel calls tools only on a conversation's first request.
    """
    page.goto(app_url)
    page.locator("#user").select_option(user)
    page.locator("#subject").fill("Where is my order?")
    # Wait for the server's answer, so the next click already has a ticket to talk to.
    with page.expect_response(
        lambda r: r.request.method == "POST" and r.url.endswith("/tickets")
    ) as created:
        page.locator("#new-ticket").click()
    assert created.value.status == 201


def send(page: Page, text: str) -> None:
    page.locator("#message").fill(text)
    with page.expect_response(lambda r: r.url.endswith("/messages")) as sent:
        page.locator("#send").click()
    assert sent.value.ok


def ask_for_refund(page: Page, app_url: str):
    """Sam asks for a refund in a fresh ticket. Returns the approval card that appears."""
    new_ticket(page, app_url, "sam")
    send(page, "Please refund order 1042")
    card = page.get_by_test_id("approval-card")
    expect(card).to_contain_text("1042")
    return card


def refund_statuses() -> list[str]:
    """What the database says, read from this process: the page cannot be trusted to tell us."""
    with Session(engine) as db:
        return list(db.scalars(select(Refund.status).order_by(Refund.id)))


def test_ada_sends_a_message_and_sees_a_reply(page: Page, app_url: str):
    new_ticket(page, app_url, "ada")
    send(page, "Where is order 1042?")
    expect(page.get_by_test_id("user-message")).to_have_text("Where is order 1042?")
    expect(page.get_by_test_id("assistant-message").first).to_be_visible()


def test_sam_approves_a_refund(page: Page, app_url: str):
    card = ask_for_refund(page, app_url)
    assistant = page.get_by_test_id("assistant-message")
    assert refund_statuses() == ["pending"]  # the card is up, so nothing has been executed
    expect(assistant).to_have_count(0)  # and the desk has said nothing yet

    with page.expect_response(lambda r: "/approvals/" in r.url) as decided:
        card.get_by_role("button", name="Approve").click()
    assert decided.value.ok
    assert refund_statuses() == ["executed"]
    expect(assistant.first).to_be_visible()


def test_sam_rejects_a_refund(page: Page, app_url: str):
    card = ask_for_refund(page, app_url)
    assistant = page.get_by_test_id("assistant-message")
    assert refund_statuses() == ["pending"]

    with page.expect_response(lambda r: "/approvals/" in r.url) as decided:
        card.get_by_role("button", name="Reject").click()
    assert decided.value.ok
    assert refund_statuses() == ["rejected"]  # a "no" is recorded, and nothing was executed
    expect(assistant.first).to_be_visible()


def test_html_in_a_message_is_shown_as_text(page: Page, app_url: str):
    new_ticket(page, app_url, "ada")
    send(page, "<b>x</b>")
    # textContent keeps the tags as plain text
    expect(page.get_by_test_id("user-message")).to_have_text("<b>x</b>")
    expect(page.locator("#log b")).to_have_count(0)  # no <b> element was ever created
