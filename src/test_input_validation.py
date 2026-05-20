"""
Test Suite: Input Validation and Error Handling
Tests edge cases: unsupported HTTP methods, SQL injection, extreme input sizes,
empty required fields, and missing ID parameters.
"""
import requests
import pytest
from conftest import BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD


# ── Unsupported HTTP methods ───────────────────────────────────────────────────

def test_invalid_method_on_products():
    print(f"\n  Sending PATCH /products.php (PATCH is not a supported method)...")
    resp = requests.patch(f"{BASE_URL}/products.php")
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: server returns 405 Method Not Allowed...")
    assert resp.status_code == 405
    print(f"  [PASS] PATCH /products.php -> 405 Method Not Allowed")


def test_invalid_method_on_rewards():
    print(f"\n  Sending PATCH /rewards.php (PATCH is not a supported method)...")
    resp = requests.patch(f"{BASE_URL}/rewards.php")
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: server returns 405 Method Not Allowed...")
    assert resp.status_code == 405
    print(f"  [PASS] PATCH /rewards.php -> 405 Method Not Allowed")


# ── SQL injection / dangerous input ───────────────────────────────────────────

def test_login_with_sql_injection_email():
    injection = "' OR '1'='1"
    print(f"\n  Sending POST /auth.php with SQL injection string as email...")
    print(f"  Injection input : {injection}")
    resp = requests.post(
        f"{BASE_URL}/auth.php",
        json={"email": injection, "password": "anything"},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: login is rejected and server did NOT crash (no 500)...")
    assert resp.status_code in (200, 400, 429)
    assert data.get("success") is not True
    print(f"  [PASS] SQL injection safely rejected (HTTP {resp.status_code})")


def test_login_with_very_long_email():
    long_email = "a" * 500 + "@test.com"
    print(f"\n  Sending POST /auth.php with an extremely long email (500+ characters)...")
    print(f"  Email length    : {len(long_email)} characters")
    resp = requests.post(
        f"{BASE_URL}/auth.php",
        json={"email": long_email, "password": "test"},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: server does NOT return 500 (no crash)...")
    assert resp.status_code in (200, 400, 413, 422, 429)
    assert resp.status_code != 500
    print(f"  [PASS] Very long email handled gracefully (HTTP {resp.status_code})")


def test_login_with_numeric_email():
    print(f"\n  Sending POST /auth.php with an integer (12345) instead of a string for email...")
    resp = requests.post(
        f"{BASE_URL}/auth.php",
        json={"email": 12345, "password": "test"},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: server does NOT crash (no 500)...")
    assert resp.status_code in (200, 400, 422, 429)
    assert resp.status_code != 500
    print(f"  [PASS] Numeric email handled gracefully (HTTP {resp.status_code})")


# ── Customer registration edge cases ──────────────────────────────────────────

def test_register_with_empty_strings():
    print(f"\n  Sending POST /customers.php register with all fields set to empty strings...")
    resp = requests.post(
        f"{BASE_URL}/customers.php",
        json={
            "action":    "register",
            "firstName": "",
            "lastName":  "",
            "email":     "",
            "password":  "",
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    if resp.status_code == 429:
        pytest.skip("Registration rate limit reached")
    data = resp.json()
    print(f"  Checking: server rejects empty fields (success != True)...")
    assert data.get("success") is not True
    print(f"  [PASS] Empty string registration correctly rejected: {data.get('error')}")


def test_register_with_invalid_email_format():
    print(f"\n  Sending POST /customers.php register with 'not-an-email' as the email value...")
    resp = requests.post(
        f"{BASE_URL}/customers.php",
        json={
            "action":    "register",
            "firstName": "Bad",
            "lastName":  "Email",
            "email":     "not-an-email",
            "password":  "password123",
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: server does NOT crash (no 500)...")
    assert resp.status_code != 500
    print(f"  [PASS] Invalid email format handled without crash (HTTP {resp.status_code})")


# ── Missing ID parameters ──────────────────────────────────────────────────────

def test_delete_product_missing_id(admin_headers):
    print(f"\n  Sending DELETE /products.php with NO ?id= parameter (admin authenticated)...")
    resp = requests.delete(f"{BASE_URL}/products.php", headers=admin_headers)
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: server returns an error message about missing ID...")
    assert resp.status_code in (200, 400, 422, 401)
    assert "error" in data
    print(f"  [PASS] DELETE product without id correctly rejected: {data['error']}")


def test_delete_reward_missing_id(admin_headers):
    print(f"\n  Sending DELETE /rewards.php with NO ?id= parameter (admin authenticated)...")
    resp = requests.delete(f"{BASE_URL}/rewards.php", headers=admin_headers)
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: server returns an error message about missing ID...")
    assert resp.status_code in (200, 400, 422, 401)
    assert "error" in data
    print(f"  [PASS] DELETE reward without id correctly rejected: {data['error']}")


# ── Public endpoints ───────────────────────────────────────────────────────────

def test_get_products_with_no_params():
    print(f"\n  Sending plain GET /products.php with no query parameters...")
    resp = requests.get(f"{BASE_URL}/products.php")
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: status is 200 and response is a JSON list...")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    print(f"  [PASS] GET products with no params returns a list ({len(resp.json())} items)")
