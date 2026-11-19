from unittest.mock import MagicMock, patch

import pytest
import requests

from openfoodfacts import ExternalAPIError, fetch_by_barcode, search_by_name

MILK = {"status": 1, "product": {"product_name": "Organic Almond Milk", "brands": "Silk",
                                 "ingredients_text": "Filtered water, almonds"}}


def fake_response(payload):
    resp = MagicMock()
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


@patch("openfoodfacts.requests.get")
def test_fetch_by_barcode_success(mock_get):
    mock_get.return_value = fake_response(MILK)
    product = fetch_by_barcode("123")
    assert product["product_name"] == "Organic Almond Milk" and product["barcode"] == "123"


@patch("openfoodfacts.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_get.return_value = fake_response({"status": 0})
    assert fetch_by_barcode("000") is None


@patch("openfoodfacts.requests.get", side_effect=requests.ConnectionError("boom"))
def test_fetch_by_barcode_network_error(_mock):
    with pytest.raises(ExternalAPIError):
        fetch_by_barcode("123")


@patch("openfoodfacts.requests.get")
def test_search_by_name_success(mock_get):
    mock_get.return_value = fake_response({"products": [MILK["product"]]})
    assert search_by_name("almond milk")["brands"] == "Silk"


@patch("openfoodfacts.requests.get")
def test_search_by_name_empty(mock_get):
    mock_get.return_value = fake_response({"products": []})
    assert search_by_name("nothing") is None
