"""Episode 03, locked: the ticket and order routes. Do not edit; make the code pass it."""

ADA = {"X-Demo-User": "ada"}
BO = {"X-Demo-User": "bo"}
SAM = {"X-Demo-User": "sam"}


def test_ada_creates_and_reads_her_ticket(client):
    created = client.post("/tickets", json={"subject": "Mug arrived cracked"}, headers=ADA)
    assert created.status_code == 201
    ticket = created.json()
    assert ticket["customer"] == "ada"
    assert ticket["subject"] == "Mug arrived cracked"

    read = client.get(f"/tickets/{ticket['id']}", headers=ADA)
    assert read.status_code == 200
    assert read.json() == ticket


def test_bo_gets_404_and_sam_gets_200_for_adas_ticket(client):
    ticket_id = client.post("/tickets", json={"subject": "Refund?"}, headers=ADA).json()["id"]
    assert client.get(f"/tickets/{ticket_id}", headers=BO).status_code == 404
    assert client.get(f"/tickets/{ticket_id}", headers=SAM).status_code == 200


def test_missing_ticket_is_404(client):
    assert client.get("/tickets/9999", headers=ADA).status_code == 404


def test_no_header_is_401(client):
    assert client.post("/tickets", json={"subject": "Hi"}).status_code == 401
    assert client.get("/tickets/1").status_code == 401
    assert client.get("/orders/1042").status_code == 401


def test_empty_subject_is_422(client):
    assert client.post("/tickets", json={"subject": ""}, headers=ADA).status_code == 422


def test_ada_reads_her_order_but_not_bos(client):
    order = client.get("/orders/1042", headers=ADA)
    assert order.status_code == 200
    assert order.json() == {
        "id": 1042,
        "items": "1 blue mug",
        "status": "delivered",
        "amount_cents": 1200,
    }
    assert client.get("/orders/2077", headers=ADA).status_code == 404
    assert client.get("/orders/2077", headers=BO).status_code == 200


def test_sam_reads_any_order(client):
    assert client.get("/orders/1042", headers=SAM).status_code == 200
    assert client.get("/orders/2077", headers=SAM).status_code == 200
    assert client.get("/orders/9999", headers=SAM).status_code == 404


def test_an_id_too_big_for_postgres_is_422_not_500(client):
    assert client.get("/tickets/99999999999", headers=ADA).status_code == 422
    assert client.get("/orders/99999999999", headers=ADA).status_code == 422
