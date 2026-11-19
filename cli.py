"""Menu-driven CLI that talks to the Flask API. Start the API first: python app.py"""
import requests

API_URL = "http://127.0.0.1:5000"
TIMEOUT = 10


def call_api(method, path, **kwargs):
    """Make a request; return (data, error_message). Never raises."""
    try:
        resp = requests.request(method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs)
    except requests.RequestException:
        return None, "Could not reach the API. Is the server running?"
    try:
        body = resp.json()
    except ValueError:
        return None, f"Unexpected response (status {resp.status_code})"
    if resp.status_code >= 400:
        return None, body.get("error", f"Request failed ({resp.status_code})")
    return body, None


def read_int(prompt):
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("Please enter a whole number.")
        return None


def read_float(prompt, allow_blank=False):
    raw = input(prompt).strip()
    if allow_blank and raw == "":
        return ""
    try:
        return float(raw)
    except ValueError:
        print("Please enter a valid number.")
        return None


def show_item(item):
    print(f"[{item['id']}] {item['product_name']} ({item.get('brands', '')}) "
          f"- ${item.get('price', 0):.2f}, stock: {item.get('quantity', 0)}")


def view_all():
    items, err = call_api("GET", "/inventory")
    if err:
        print(err)
    elif not items:
        print("Inventory is empty.")
    else:
        for i in items:
            show_item(i)


def view_one():
    item_id = read_int("Item ID: ")
    if item_id is None:
        return
    item, err = call_api("GET", f"/inventory/{item_id}")
    if err:
        print(err)
        return
    for key, value in item.items():
        print(f"  {key}: {value}")


def add_item():
    name = input("Product name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    price = read_float("Price: ")
    qty = read_int("Quantity: ")
    if price is None or qty is None:
        return
    item, err = call_api("POST", "/inventory",
                         json={"product_name": name, "price": price, "quantity": qty})
    print(err if err else f"Added item #{item['id']}.")


def update_item():
    item_id = read_int("Item ID to update: ")
    if item_id is None:
        return
    price = read_float("New price (blank to skip): ", allow_blank=True)
    if price is None:
        return
    qty_raw = input("New stock (blank to skip): ").strip()
    changes = {}
    if price != "":
        changes["price"] = price
    if qty_raw:
        try:
            changes["quantity"] = int(qty_raw)
        except ValueError:
            print("Stock must be a whole number.")
            return
    if not changes:
        print("Nothing to update.")
        return
    item, err = call_api("PATCH", f"/inventory/{item_id}", json=changes)
    if err:
        print(err)
    else:
        print("Updated:")
        show_item(item)


def delete_item():
    item_id = read_int("Item ID to delete: ")
    if item_id is None:
        return
    _, err = call_api("DELETE", f"/inventory/{item_id}")
    print(err if err else "Item deleted.")


def find_on_api():
    choice = input("Search by (1) barcode or (2) name? ").strip()
    if choice == "1":
        params = {"barcode": input("Barcode: ").strip()}
    elif choice == "2":
        params = {"name": input("Product name: ").strip()}
    else:
        print("Invalid choice.")
        return
    if not list(params.values())[0]:
        print("Search term cannot be empty.")
        return
    product, err = call_api("GET", "/external/search", params=params)
    if err:
        print(err)
        return
    print(f"Found: {product['product_name']} ({product['brands']})")
    print(f"Ingredients: {product['ingredients_text'] or 'n/a'}")
    if input("Add to inventory? (y/n) ").strip().lower() == "y":
        price = read_float("Price: ")
        qty = read_int("Quantity: ")
        if price is None or qty is None:
            return
        body = {**params, "price": price, "quantity": qty}
        item, err = call_api("POST", "/inventory/import", json=body)
        print(err if err else f"Added item #{item['id']}.")


MENU = {
    "1": ("View all items", view_all),
    "2": ("View one item", view_one),
    "3": ("Add item", add_item),
    "4": ("Update price/stock", update_item),
    "5": ("Delete item", delete_item),
    "6": ("Find item on OpenFoodFacts", find_on_api),
}


def main():
    while True:
        print("\n=== Inventory Manager ===")
        for key, (label, _) in MENU.items():
            print(f"{key}. {label}")
        print("q. Quit")
        choice = input("> ").strip().lower()
        if choice == "q":
            break
        action = MENU.get(choice)
        if action:
            action[1]()
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
