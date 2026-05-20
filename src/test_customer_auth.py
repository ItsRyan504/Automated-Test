"""
Test Suite: Customer Registration and Login
"""
import uuid
import requests
import pytest
from conftest import (
    BASE_URL,
    TEST_CUSTOMER_EMAIL,
    TEST_CUSTOMER_PASSWORD,
    TEST_CUSTOMER_FIRST,
    TEST_CUSTOMER_LAST,
    TEST_CUSTOMER_PHONE,
)


def unique_email():
    return f"autotest_{uuid.uuid4().hex[:8]}@jazsam.com"


# ── Registration ───────────────────────────────────────────────────────────────

def test_customer_register_valid():
    email = unique_email()
    print(f"\n  Sending POST /customers.php with action=register and all required fields...")
    print(f"  Email used: {email}")
    resp = requests.post(
        f"{BASE_URL}/customers.php",
        json={
            "action":    "register",
            "firstName": TEST_CUSTOMER_FIRST,
            "lastName":  TEST_CUSTOMER_LAST,
            "email":     email,
            "phone":     TEST_CUSTOMER_PHONE,
            "password":  TEST_CUSTOMER_PASSWORD,
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    if resp.status_code == 429:
        pytest.skip("Registration rate limit reached — run again after 1 hour")
    data = resp.json()
    print(f"  Checking: success == True...")
    assert resp.status_code in (200, 201)
    assert data["success"] is True
    print(f"  Checking: returned email matches submitted email...")
    assert data["user"]["email"] == email
    print(f"  Checking: new account starts at Bronze tier with 0 points...")
    assert data["user"]["tier"] == "Bronze"
    assert data["user"]["points"] == 0
    print(f"  [PASS] Customer registered successfully: {email}")


def test_customer_register_duplicate_email():
    email = unique_email()
    payload = {
        "action":    "register",
        "firstName": TEST_CUSTOMER_FIRST,
        "lastName":  TEST_CUSTOMER_LAST,
        "email":     email,
        "phone":     TEST_CUSTOMER_PHONE,
        "password":  TEST_CUSTOMER_PASSWORD,
    }
    print(f"\n  Step 1 - Registering a new customer with email: {email}...")
    r1 = requests.post(f"{BASE_URL}/customers.php", json=payload)
    print(f"  First attempt status: {r1.status_code}")
    if r1.status_code == 429:
        pytest.skip("Registration rate limit reached")

    print(f"  Step 2 - Registering again with the SAME email...")
    r2 = requests.post(f"{BASE_URL}/customers.php", json=payload)
    print(f"  Second attempt status : {r2.status_code}")
    print(f"  Second attempt body   : {r2.json()}")
    data = r2.json()
    print(f"  Checking: duplicate email is rejected with success == False...")
    assert data["success"] is False
    assert "error" in data
    print(f"  [PASS] Duplicate email correctly rejected: {data['error']}")


def test_customer_register_missing_required_fields():
    print(f"\n  Sending POST /customers.php with missing firstName and password...")
    resp = requests.post(
        f"{BASE_URL}/customers.php",
        json={
            "action":   "register",
            "lastName": TEST_CUSTOMER_LAST,
            "email":    unique_email(),
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    if resp.status_code == 429:
        pytest.skip("Registration rate limit reached")
    data = resp.json()
    print(f"  Checking: server rejects registration without required fields...")
    assert data.get("success") is not True
    print(f"  [PASS] Missing required fields correctly rejected: {data.get('error')}")


# ── Login ──────────────────────────────────────────────────────────────────────

def test_customer_login_valid():
    print(f"\n  Sending POST /customers.php with action=login using stable test account...")
    print(f"  Email used: {TEST_CUSTOMER_EMAIL}")
    resp = requests.post(
        f"{BASE_URL}/customers.php",
        json={
            "action":   "login",
            "email":    TEST_CUSTOMER_EMAIL,
            "password": TEST_CUSTOMER_PASSWORD,
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: success == True...")
    assert resp.status_code == 200
    assert data["success"] is True
    print(f"  Checking: returned email matches login email...")
    assert data["user"]["email"] == TEST_CUSTOMER_EMAIL
    print(f"  [PASS] Customer login successful: {TEST_CUSTOMER_EMAIL}")


def test_customer_login_wrong_password():
    print(f"\n  Sending POST /customers.php with correct email but WRONG password...")
    resp = requests.post(
        f"{BASE_URL}/customers.php",
        json={
            "action":   "login",
            "email":    TEST_CUSTOMER_EMAIL,
            "password": "wrongpassword",
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: success == False...")
    assert resp.status_code == 200
    assert data["success"] is False
    assert "error" in data
    print(f"  [PASS] Wrong password correctly rejected: {data['error']}")


def test_customer_login_nonexistent_email():
    print(f"\n  Sending POST /customers.php login with an email that was never registered...")
    resp = requests.post(
        f"{BASE_URL}/customers.php",
        json={
            "action":   "login",
            "email":    "ghost_user_xyz@jazsam.com",
            "password": "anything",
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: success == False...")
    assert data["success"] is False
    print(f"  [PASS] Non-existent email correctly rejected: {data['error']}")


def test_customer_login_missing_fields():
    print(f"\n  Sending POST /customers.php login with no email or password...")
    resp = requests.post(
        f"{BASE_URL}/customers.php",
        json={"action": "login"},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: server returns an error (not a crash)...")
    assert resp.status_code in (200, 400)
    assert data.get("success") is not True
    print(f"  [PASS] Login with no credentials correctly rejected: {data.get('error')}")
