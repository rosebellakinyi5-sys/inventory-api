"""Helpers for talking to the external OpenFoodFacts API."""
import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryCLI/1.0 (student project)"}
TIMEOUT = 10


class ExternalAPIError(Exception):
    """Raised when OpenFoodFacts fails or is unreachable."""


def _clean(product, barcode=None):
    """Keep only the fields we store."""
    return {
        "product_name": product.get("product_name", "Unknown"),
        "brands": product.get("brands", "Unknown"),
        "ingredients_text": product.get("ingredients_text", ""),
        "barcode": barcode or product.get("code", ""),
    }


def fetch_by_barcode(barcode):
    """Return cleaned product dict, or None if not found."""
    try:
        resp = requests.get(f"{BASE_URL}/api/v0/product/{barcode}.json",
                            headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise ExternalAPIError(f"OpenFoodFacts request failed: {exc}") from exc
    if data.get("status") != 1:
        return None
    return _clean(data["product"], barcode)


def search_by_name(name):
    """Return the first matching cleaned product, or None."""
    try:
        resp = requests.get(f"{BASE_URL}/cgi/search.pl",
                            params={"search_terms": name, "json": 1, "page_size": 1},
                            headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise ExternalAPIError(f"OpenFoodFacts request failed: {exc}") from exc
    products = data.get("products", [])
    return _clean(products[0]) if products else None
