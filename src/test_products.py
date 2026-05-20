"""
Test Suite: Products API
Tests GET (public), POST/PUT/DELETE (admin-only), and input validation.
"""
import uuid
import requests
import pytest
from conftest import BASE_URL


def unique_id(prefix="P"):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


# ── GET ────────────────────────────────────────────────────────────────────────

def test_get_products_returns_list():
    print(f"\n  Sending GET /products.php with no authentication (public endpoint)...")
    resp = requests.get(f"{BASE_URL}/products.php")
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: status is 200...")
    assert resp.status_code == 200
    data = resp.json()
    print(f"  Checking: response is a list (not a dict or error)...")
    assert isinstance(data, list)
    print(f"  [PASS] GET products returned {len(data)} product(s)")


def test_get_products_structure():
    print(f"\n  Fetching products and checking the structure of each item...")
    resp = requests.get(f"{BASE_URL}/products.php")
    data = resp.json()
    if not data:
        pytest.skip("No products in database — skipping structure check")

    required_fields = {"id", "name", "category", "price", "status"}
    print(f"  Required fields to check: {required_fields}")
    for product in data[:3]:
        print(f"  Checking product '{product.get('name')}' for missing fields...")
        missing = required_fields - set(product.keys())
        assert not missing, f"Product missing fields: {missing}"
    print(f"  [PASS] Product structure validated for {min(3, len(data))} product(s)")


# ── POST ───────────────────────────────────────────────────────────────────────

def test_post_product_requires_auth():
    print(f"\n  Sending POST /products.php with NO Authorization header...")
    resp = requests.post(
        f"{BASE_URL}/products.php",
        json={"name": "Unauthorized Coffee", "category": "Coffee", "price": 80},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: server returns 401 (Unauthorized)...")
    assert resp.status_code in (401, 403)
    print(f"  [PASS] Unauthenticated product creation correctly rejected ({resp.status_code})")


def test_post_product_missing_name(admin_headers):
    print(f"\n  Sending POST /products.php with admin token but NO 'name' field...")
    resp = requests.post(
        f"{BASE_URL}/products.php",
        headers=admin_headers,
        json={"category": "Coffee", "price": 80},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: server rejects request and returns an error...")
    assert resp.status_code in (200, 400, 422)
    assert "error" in data or data.get("success") is False
    print(f"  [PASS] Missing product name correctly rejected")


def test_post_product_valid(admin_headers):
    pid = unique_id("P")
    print(f"\n  Sending POST /products.php with admin token and all valid fields...")
    print(f"  Product ID used : {pid}")
    resp = requests.post(
        f"{BASE_URL}/products.php",
        headers=admin_headers,
        json={
            "id":       pid,
            "name":     "AutoTest Brew",
            "category": "Coffee",
            "price":    95,
            "sizes":    ["Small", "Medium", "Large"],
            "temps":    ["Hot"],
            "status":   "available",
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: status is 200 or 201 and response contains 'id'...")
    assert resp.status_code in (200, 201)
    assert "id" in data
    print(f"  [PASS] Product created successfully: {data['id']}")


# ── PUT / DELETE ───────────────────────────────────────────────────────────────

def test_put_and_delete_product(admin_headers):
    pid = unique_id("P")
    print(f"\n  --- FULL PRODUCT LIFECYCLE TEST ---")

    print(f"  Step 1 - CREATE: POST /products.php with ID {pid}...")
    r1 = requests.post(
        f"{BASE_URL}/products.php",
        headers=admin_headers,
        json={
            "id":       pid,
            "name":     "Lifecycle Test Coffee",
            "category": "Coffee",
            "price":    100,
            "sizes":    ["Medium"],
            "temps":    ["Hot"],
            "status":   "available",
        },
    )
    print(f"  Create status   : {r1.status_code}")
    assert r1.status_code in (200, 201), f"Create failed: {r1.text}"
    print(f"  Create OK.")

    print(f"  Step 2 - UPDATE: PUT /products.php — changing name and price...")
    r2 = requests.put(
        f"{BASE_URL}/products.php",
        headers=admin_headers,
        json={
            "id":       pid,
            "name":     "Lifecycle Test Coffee UPDATED",
            "category": "Coffee",
            "price":    110,
            "sizes":    ["Medium"],
            "temps":    ["Hot"],
            "status":   "available",
        },
    )
    print(f"  Update status   : {r2.status_code}")
    print(f"  Update body     : {r2.json()}")
    assert r2.status_code == 200, f"Update failed: {r2.text}"
    assert r2.json().get("id") == pid
    print(f"  Update OK.")

    print(f"  Step 3 - DELETE: DELETE /products.php?id={pid}...")
    r3 = requests.delete(f"{BASE_URL}/products.php?id={pid}", headers=admin_headers)
    print(f"  Delete status   : {r3.status_code}")
    print(f"  Delete body     : {r3.json()}")
    assert r3.status_code == 200, f"Delete failed: {r3.text}"
    assert r3.json().get("deleted") == pid
    print(f"  [PASS] Full product lifecycle (create -> update -> delete) passed")


def test_delete_nonexistent_product(admin_headers):
    print(f"\n  Sending DELETE /products.php?id=DOESNOTEXIST999 (ID that does not exist)...")
    resp = requests.delete(
        f"{BASE_URL}/products.php?id=DOESNOTEXIST999",
        headers=admin_headers,
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: server returns 404 Not Found...")
    assert resp.status_code == 404
    print(f"  [PASS] Delete non-existent product correctly returned 404")
