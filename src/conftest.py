"""
Shared configuration and fixtures for JazSam / SalesPresso API tests.
"""
import sys
import uuid
import requests
import pytest

# Force UTF-8 output so special characters (e.g. ₱) print correctly on Windows
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost/salespresso-api"

ADMIN_EMAIL    = "admin@jazsam.com"
ADMIN_PASSWORD = "admin123"

# Fixed email so the same customer is reused across runs (avoids exhausting
# the registration rate limit of 5 per hour).
TEST_CUSTOMER_EMAIL    = "autotest_stable@jazsam.com"
TEST_CUSTOMER_PASSWORD = "TestPass123!"
TEST_CUSTOMER_FIRST    = "Auto"
TEST_CUSTOMER_LAST     = "Tester"
TEST_CUSTOMER_PHONE    = "09123456789"


@pytest.fixture(scope="session", autouse=True)
def admin_token():
    """
    Logs in as admin ONCE at session start (autouse=True ensures this runs
    before any individual test consumes rate-limit slots).
    Rate limit: 5 login attempts per 5 minutes.  This fixture uses slot #1.
    """
    resp = requests.post(
        f"{BASE_URL}/auth.php",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    data = resp.json()
    assert data.get("success"), (
        f"Admin login failed during fixture setup — "
        f"check credentials or wait for rate limit to reset. Response: {data}"
    )
    return data["token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session", autouse=True)
def ensure_test_customer():
    """
    Pre-creates (or silently skips if already exists) a stable test customer
    so that login tests don't need to register a new account each run.
    """
    requests.post(
        f"{BASE_URL}/customers.php",
        json={
            "action":    "register",
            "firstName": TEST_CUSTOMER_FIRST,
            "lastName":  TEST_CUSTOMER_LAST,
            "email":     TEST_CUSTOMER_EMAIL,
            "phone":     TEST_CUSTOMER_PHONE,
            "password":  TEST_CUSTOMER_PASSWORD,
        },
    )
    # We don't assert here — if the account already exists, the API returns
    # success=false but the account is still usable for login tests.
