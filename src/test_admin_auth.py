"""
Test Suite: Admin Authentication
Tests valid login (via session fixture), invalid credentials, missing fields.
"""
import requests
import pytest
from conftest import BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD


def test_admin_login_token_is_valid(admin_token):
    print(f"\n  Checking: admin_token fixture returned a non-empty string...")
    assert admin_token and isinstance(admin_token, str)
    print(f"  [PASS] Admin token acquired: {admin_token[:20]}...")


def test_admin_login_wrong_password():
    print(f"\n  Sending POST /auth.php with correct email but WRONG password...")
    resp = requests.post(
        f"{BASE_URL}/auth.php",
        json={"email": ADMIN_EMAIL, "password": "wrongpassword"},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: success == False...")
    assert resp.status_code == 200
    assert data["success"] is False
    assert "error" in data
    print(f"  [PASS] Wrong password correctly rejected: {data['error']}")


def test_admin_login_wrong_email():
    print(f"\n  Sending POST /auth.php with a non-existent admin email...")
    resp = requests.post(
        f"{BASE_URL}/auth.php",
        json={"email": "ghost_admin@jazsam.com", "password": "anything"},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: success == False...")
    assert resp.status_code == 200
    assert data["success"] is False
    print(f"  [PASS] Unknown email correctly rejected: {data['error']}")


def test_admin_login_missing_fields():
    print(f"\n  Sending POST /auth.php with completely empty JSON body {{}}...")
    resp = requests.post(f"{BASE_URL}/auth.php", json={})
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: server does not return success == True...")
    assert resp.status_code in (200, 400)
    assert data.get("success") is not True
    print(f"  [PASS] Empty body correctly rejected: {data.get('error')}")
