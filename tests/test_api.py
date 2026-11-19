from unittest.mock import patch

from openfoodfacts import ExternalAPIError


def test_get_all(client):
    resp = client.get("/inventory")
    assert resp.status_code == 200 and len(resp.get_json()) == 2


def test_get_one(client):
    assert client.get("/inventory/1").get_json()["product_name"] == "Organic Almond Milk"


def test_get_one_missing(client):
    assert client.get("/inventory/99").status_code == 404


def test_post_creates_item(client):
    resp = client.post("/inventory", json={"product_name": "Rice", "price": 2.5, "quantity": 10})
    assert resp.status_code == 201 and resp.get_json()["id"] == 3
    assert len(client.get("/inventory").get_json()) == 3


def test_post_requires_name(client):
    assert client.post("/inventory", json={"price": 1}).status_code == 400


def test_post_rejects_negative_price(client):
    assert client.post("/inventory", json={"product_name": "X", "price": -1}).status_code == 400


def test_patch_updates_fields(client):
    resp = client.patch("/inventory/1", json={"price": 5.5, "quantity": 7})
    body = resp.get_json()
    assert resp.status_code == 200 and body["price"] == 5.5 and body["quantity"] == 7


def test_patch_cannot_change_id(client):
    client.patch("/inventory/1", json={"id": 50})
    assert client.get("/inventory/1").status_code == 200


def test_patch_missing(client):
    assert client.patch("/inventory/99", json={"price": 1}).status_code == 404


def test_delete(client):
    assert client.delete("/inventory/1").status_code == 200
    assert client.get("/inventory/1").status_code == 404


def test_delete_missing(client):
    assert client.delete("/inventory/99").status_code == 404


def test_external_search_needs_params(client):
    assert client.get("/external/search").status_code == 400


@patch("app.fetch_by_barcode")
def test_external_search_barcode(mock_fetch, client):
    mock_fetch.return_value = {"product_name": "Cola", "brands": "X", "ingredients_text": "", "barcode": "1"}
    resp = client.get("/external/search?barcode=1")
    assert resp.status_code == 200 and resp.get_json()["product_name"] == "Cola"


@patch("app.search_by_name", return_value=None)
def test_external_search_not_found(_mock, client):
    assert client.get("/external/search?name=zzz").status_code == 404


@patch("app.fetch_by_barcode", side_effect=ExternalAPIError("down"))
def test_external_search_api_failure(_mock, client):
    assert client.get("/external/search?barcode=1").status_code == 502


@patch("app.fetch_by_barcode")
def test_import_adds_to_inventory(mock_fetch, client):
    mock_fetch.return_value = {"product_name": "Cola", "brands": "X", "ingredients_text": "", "barcode": "1"}
    resp = client.post("/inventory/import", json={"barcode": "1", "price": 1.2, "quantity": 5})
    assert resp.status_code == 201 and resp.get_json()["product_name"] == "Cola"
    assert len(client.get("/inventory").get_json()) == 3
