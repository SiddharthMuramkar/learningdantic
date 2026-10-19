from html.parser import HTMLParser
from pathlib import Path

IDS = {"user", "subject", "new-ticket", "message", "send", "log"}
APP_JS = Path(__file__).parents[1] / "static" / "app.js"


class Page(HTMLParser):
    """Collects the ids and script files that an HTML page declares."""

    def __init__(self):
        super().__init__()
        self.ids, self.scripts = set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "script":
            self.scripts.append(attrs.get("src"))


def test_page_has_every_contract_id_and_loads_both_scripts(client):
    response = client.get("/")
    assert response.status_code == 200
    page = Page()
    page.feed(response.text)
    assert page.ids >= IDS
    for name in ("ada", "bo", "sam"):
        assert f">{name}</option>" in response.text
    assert set(page.scripts) >= {"/static/app.js", "/static/approvals.js"}
    for src in page.scripts:  # a script tag that points nowhere would pass the lines above
        assert client.get(src).status_code == 200, src


def test_app_js_puts_text_in_with_textcontent_only():
    js = APP_JS.read_text()
    assert "textContent" in js
    for unsafe in ("innerHTML", "outerHTML", "insertAdjacentHTML"):
        assert unsafe not in js
