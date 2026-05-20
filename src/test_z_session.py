"""
Test Suite: Session Handling (runs last — z_ prefix ensures alphabetical order)
Tests admin logout and that a revoked token is rejected on subsequent requests.
"""
import requests
import pytest
from conftest import BASE_URL


def test_admin_logout_revokes_token(admin_headers, admin_token):
    print(f"\n  Sending DELETE /auth.php with the current session bearer token...")
    print(f"  Token being revoked: {admin_token[:20]}...")
    resp = requests.delete(f"{BASE_URL}/auth.php", headers=admin_headers)
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    print(f"  Checking: success == True (logout confirmed)...")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    print(f"  [PASS] Admin logout: token revoked successfully")


def test_revoked_token_is_rejected(admin_headers, admin_token):
    print(f"\n  Attempting POST /products.php using the ALREADY REVOKED token...")
    print(f"  Token being used : {admin_token[:20]}... (this was logged out in previous test)")
    resp = requests.post(
        f"{BASE_URL}/products.php",
        headers=admin_headers,
        json={"name": "Should Fail", "category": "Coffee", "price": 10},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    print(f"  Checking: server returns 401 (token no longer valid)...")
    assert resp.status_code == 401
    print(f"  [PASS] Revoked token correctly rejected on protected endpoint (401)")
