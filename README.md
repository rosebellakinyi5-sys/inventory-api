# Inventory Management System (Flask REST API + CLI)

A small admin tool for a retail shop. A Flask REST API manages inventory stored in an in-memory array, products can be looked up on the [OpenFoodFacts API](https://world.openfoodfacts.org/), and a menu-driven CLI talks to the API.

## Installation
```bash
git clone https://github.com/rosebellakinyi5-sys/inventory-api.git && cd inventory-api
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running
Terminal 1 (API, debug mode on):
```bash
python app.py
```
Terminal 2 (CLI):
```bash
python cli.py
```

## API Endpoints
| Method | Route | Description | Success |
|---|---|---|---|
| GET | `/inventory` | Fetch all items | 200 |
| GET | `/inventory/<id>` | Fetch one item | 200 / 404 |
| POST | `/inventory` | Add item (`product_name` required; optional `brands`, `ingredients_text`, `barcode`, `price`, `quantity`) | 201 / 400 |
| PATCH | `/inventory/<id>` | Update fields (e.g. `price`, `quantity`) | 200 / 404 / 400 |
| DELETE | `/inventory/<id>` | Remove item | 200 / 404 |
| GET | `/external/search?barcode=...` or `?name=...` | Look up a product on OpenFoodFacts (not saved) | 200 / 404 / 502 |
| POST | `/inventory/import` | Fetch from OpenFoodFacts by `barcode` or `name` and add to inventory (with `price`, `quantity`) | 201 / 404 / 502 |

Example:
```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Rice", "price": 2.5, "quantity": 10}'
```

## CLI Usage
```
=== Inventory Manager ===
1. View all items
2. View one item
3. Add item
4. Update price/stock
5. Delete item
6. Find item on OpenFoodFacts
q. Quit
```
Example: choose `6`, search by barcode `3017620422003`, then answer `y` to add the product with a price and quantity.

Invalid input (letters instead of numbers, unknown IDs) and API failures (server down, OpenFoodFacts unreachable) print friendly messages instead of crashing.

## Testing
```bash
pytest -v
```
Tests cover the API endpoints, CLI commands, and external API calls. `unittest.mock.patch` replaces `requests` so tests never hit the real network.

## Project Structure
```
app.py            Flask routes
data.py           mock database array
openfoodfacts.py  external API helpers
cli.py            command-line interface
tests/            pytest suite
```

## Maintainability
Each module has one job, functions have docstrings, and the data layer (`data.py`) can later be swapped for a real database without touching the CLI.
