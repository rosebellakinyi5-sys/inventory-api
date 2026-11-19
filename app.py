"""Flask REST API for the inventory management system."""
from flask import Flask, jsonify, request

import data
from openfoodfacts import ExternalAPIError, fetch_by_barcode, search_by_name

app = Flask(__name__)

EDITABLE_FIELDS = {"product_name", "brands", "ingredients_text", "barcode", "price", "quantity"}


def find_item(item_id):
    return next((i for i in data.inventory if i["id"] == item_id), None)


def validate_numbers(payload):
    """Return an error message if price/quantity are invalid, else None."""
    if "price" in payload and (not isinstance(payload["price"], (int, float)) or payload["price"] < 0):
        return "price must be a non-negative number"
    if "quantity" in payload and (not isinstance(payload["quantity"], int) or payload["quantity"] < 0):
        return "quantity must be a non-negative integer"
    return None


# ---------- CRUD ----------
@app.route("/inventory", methods=["GET"])
def get_all():
    return jsonify(data.inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_one(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    payload = request.get_json(silent=True)
    if not payload or "product_name" not in payload:
        return jsonify({"error": "product_name is required"}), 400
    error = validate_numbers(payload)
    if error:
        return jsonify({"error": error}), 400
    item = {"id": data.next_id(), "brands": "", "ingredients_text": "", "barcode": "",
            "price": 0.0, "quantity": 0}
    item.update({k: v for k, v in payload.items() if k in EDITABLE_FIELDS})
    data.inventory.append(item)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "JSON body required"}), 400
    error = validate_numbers(payload)
    if error:
        return jsonify({"error": error}), 400
    item.update({k: v for k, v in payload.items() if k in EDITABLE_FIELDS})
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    data.inventory.remove(item)
    return jsonify({"message": "Item deleted"}), 200


# ---------- External API helper routes ----------
def _lookup(barcode, name):
    if barcode:
        return fetch_by_barcode(barcode)
    return search_by_name(name)


@app.route("/external/search", methods=["GET"])
def external_search():
    """Look up a product on OpenFoodFacts without saving it."""
    barcode, name = request.args.get("barcode"), request.args.get("name")
    if not barcode and not name:
        return jsonify({"error": "Provide barcode or name"}), 400
    try:
        product = _lookup(barcode, name)
    except ExternalAPIError as exc:
        return jsonify({"error": str(exc)}), 502
    if product is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404
    return jsonify(product), 200


@app.route("/inventory/import", methods=["POST"])
def import_item():
    """Fetch from OpenFoodFacts and add to the inventory array."""
    payload = request.get_json(silent=True) or {}
    barcode, name = payload.get("barcode"), payload.get("name")
    if not barcode and not name:
        return jsonify({"error": "Provide barcode or name"}), 400
    error = validate_numbers(payload)
    if error:
        return jsonify({"error": error}), 400
    try:
        product = _lookup(barcode, name)
    except ExternalAPIError as exc:
        return jsonify({"error": str(exc)}), 502
    if product is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404
    item = {"id": data.next_id(), **product,
            "price": payload.get("price", 0.0), "quantity": payload.get("quantity", 0)}
    data.inventory.append(item)
    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True)  # Flask debug mode for Task 4
