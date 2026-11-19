"""Mock database: a list of dicts that simulates storage.
Shaped like OpenFoodFacts product data, plus our own fields (id, price, quantity)."""

inventory = [
    {"id": 1, "product_name": "Organic Almond Milk", "brands": "Silk",
     "ingredients_text": "Filtered water, almonds, cane sugar", "barcode": "025293600232",
     "price": 4.99, "quantity": 20},
    {"id": 2, "product_name": "Peanut Butter", "brands": "Jif",
     "ingredients_text": "Roasted peanuts, sugar, salt", "barcode": "051500255162",
     "price": 3.49, "quantity": 35},
]


def next_id():
    """Return the next unused id (max existing id + 1)."""
    return max((item["id"] for item in inventory), default=0) + 1
