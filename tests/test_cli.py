from unittest.mock import MagicMock, patch

import requests

import cli


def resp(status, body):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = body
    return r


@patch("cli.requests.request")
def test_call_api_success(mock_req):
    mock_req.return_value = resp(200, {"ok": True})
    assert cli.call_api("GET", "/inventory") == ({"ok": True}, None)


@patch("cli.requests.request")
def test_call_api_error_message(mock_req):
    mock_req.return_value = resp(404, {"error": "Item not found"})
    assert cli.call_api("GET", "/inventory/9") == (None, "Item not found")


@patch("cli.requests.request", side_effect=requests.ConnectionError)
def test_call_api_server_down(_mock):
    _, err = cli.call_api("GET", "/inventory")
    assert "Could not reach" in err


@patch("builtins.input", return_value="abc")
def test_read_int_invalid(_input, capsys):
    assert cli.read_int("x") is None
    assert "whole number" in capsys.readouterr().out


@patch("cli.call_api", return_value=({"id": 3}, None))
@patch("builtins.input", side_effect=["Rice", "2.5", "10"])
def test_add_item(_input, mock_call, capsys):
    cli.add_item()
    mock_call.assert_called_once_with("POST", "/inventory",
                                      json={"product_name": "Rice", "price": 2.5, "quantity": 10})
    assert "Added item #3" in capsys.readouterr().out


@patch("cli.call_api")
@patch("builtins.input", side_effect=["Rice", "abc", "5"])
def test_add_item_bad_price_skips_api(_input, mock_call):
    cli.add_item()
    mock_call.assert_not_called()


@patch("cli.call_api", return_value=(None, "Item not found"))
@patch("builtins.input", return_value="99")
def test_delete_missing(_input, _call, capsys):
    cli.delete_item()
    assert "Item not found" in capsys.readouterr().out


@patch("cli.call_api")
@patch("builtins.input", side_effect=["2", "Cola", "n"])
def test_find_on_api_by_name(_input, mock_call, capsys):
    mock_call.return_value = ({"product_name": "Cola", "brands": "X", "ingredients_text": "sugar"}, None)
    cli.find_on_api()
    mock_call.assert_called_once_with("GET", "/external/search", params={"name": "Cola"})
    assert "Found: Cola" in capsys.readouterr().out


@patch("builtins.input", return_value="9")
def test_find_on_api_invalid_choice(_input, capsys):
    cli.find_on_api()
    assert "Invalid choice" in capsys.readouterr().out
