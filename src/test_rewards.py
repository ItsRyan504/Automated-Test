"""
Test Suite: Rewards API
Tests GET (public), POST/PUT/DELETE (admin-only), and input validation.
"""
import uuid
import requests
import pytest
from conftest import BASE_URL


def unique_id(prefix="R"):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


# ── GET ────────────────────────────────────────────────────────────────────────

def test_get_rewards_returns_list():
    print(f"\n  Sending GET /rewards.php with no authentication (public endpoint)...")
    resp = requests.get(f"{BASE_URL}/rewards.php")
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: status is 200 and response is a list...")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    print(f"  [PASS] GET rewards returned {len(data)} reward(s)")


def test_get_rewards_structure():
    print(f"\n  Fetching rewards and validating each item has the required fields...")
    resp = requests.get(f"{BASE_URL}/rewards.php")
    data = resp.json()
    if not data:
        pytest.skip("No rewards in database — skipping structure check")

    required_fields = {"id", "name", "type", "value", "stamps"}
    print(f"  Required fields to check: {required_fields}")
    for reward in data[:3]:
        print(f"  Checking reward '{reward.get('name')}' for missing fields...")
        missing = required_fields - set(reward.keys())
        assert not missing, f"Reward missing fields: {missing}"
    print(f"  [PASS] Reward structure validated for {min(3, len(data))} reward(s)")


# ── POST ───────────────────────────────────────────────────────────────────────

def test_post_reward_requires_auth():
    print(f"\n  Sending POST /rewards.php with NO Authorization header...")
    resp = requests.post(
        f"{BASE_URL}/rewards.php",
        json={"name": "Unauthorized Reward", "stamps": 5, "rawType": "Free Item", "rawValue": 0},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: server returns 401 (Unauthorized)...")
    assert resp.status_code in (401, 403)
    print(f"  [PASS] Unauthenticated reward creation correctly rejected ({resp.status_code})")


def test_post_reward_missing_name(admin_headers):
    print(f"\n  Sending POST /rewards.php with admin token but NO 'name' field...")
    resp = requests.post(
        f"{BASE_URL}/rewards.php",
        headers=admin_headers,
        json={"stamps": 10, "rawType": "Free Item", "rawValue": 0},
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: server returns an error message...")
    assert "error" in data
    print(f"  [PASS] Missing reward name correctly rejected: {data['error']}")


def test_post_reward_free_item(admin_headers):
    rid = unique_id("R")
    print(f"\n  Sending POST /rewards.php to create a 'Free Item' reward...")
    print(f"  Reward ID used  : {rid}")
    resp = requests.post(
        f"{BASE_URL}/rewards.php",
        headers=admin_headers,
        json={
            "id":       rid,
            "name":     "AutoTest Free Coffee",
            "stamps":   10,
            "rawType":  "Free Item",
            "rawValue": 0,
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: status is 201 and response contains 'id'...")
    assert resp.status_code in (200, 201)
    assert "id" in data
    print(f"  [PASS] Free Item reward created successfully: {data['id']}")


def test_post_reward_percentage_discount(admin_headers):
    rid = unique_id("R")
    print(f"\n  Sending POST /rewards.php to create a 'Percentage' discount reward...")
    print(f"  Reward ID used  : {rid}")
    resp = requests.post(
        f"{BASE_URL}/rewards.php",
        headers=admin_headers,
        json={
            "id":       rid,
            "name":     "AutoTest 10% Off",
            "stamps":   5,
            "rawType":  "Percentage",
            "rawValue": 10,
        },
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Response body   : {resp.json()}")
    data = resp.json()
    print(f"  Checking: status is 201 and response contains 'id'...")
    assert resp.status_code in (200, 201)
    assert "id" in data
    print(f"  [PASS] Percentage discount reward created successfully: {data['id']}")


# ── PUT / DELETE ───────────────────────────────────────────────────────────────

def test_put_and_delete_reward(admin_headers):
    rid = unique_id("R")
    print(f"\n  --- FULL REWARD LIFECYCLE TEST ---")

    print(f"  Step 1 - CREATE: POST /rewards.php with ID {rid}...")
    r1 = requests.post(
        f"{BASE_URL}/rewards.php",
        headers=admin_headers,
        json={
            "id":       rid,
            "name":     "Lifecycle Reward",
            "stamps":   8,
            "rawType":  "Fixed Amount",
            "rawValue": 50,
        },
    )
    print(f"  Create status   : {r1.status_code}")
    assert r1.status_code in (200, 201), f"Create failed: {r1.text}"
    print(f"  Create OK.")

    print(f"  Step 2 - UPDATE: PUT /rewards.php — changing name and stamps from 8 to 12...")
    r2 = requests.put(
        f"{BASE_URL}/rewards.php",
        headers=admin_headers,
        json={"id": rid, "name": "Lifecycle Reward UPDATED", "stamps": 12},
    )
    print(f"  Update status   : {r2.status_code}")
    print(f"  Update body     : {r2.json()}")
    assert r2.status_code == 200, f"Update failed: {r2.text}"
    updated = r2.json()
    print(f"  Checking: stamps value updated to 12...")
    assert updated.get("stamps") == 12
    print(f"  Update OK.")

    print(f"  Step 3 - DELETE: DELETE /rewards.php?id={rid}...")
    r3 = requests.delete(f"{BASE_URL}/rewards.php?id={rid}", headers=admin_headers)
    print(f"  Delete status   : {r3.status_code}")
    print(f"  Delete body     : {r3.json()}")
    assert r3.status_code == 200, f"Delete failed: {r3.text}"
    assert r3.json().get("deleted") == rid
    print(f"  [PASS] Full reward lifecycle (create -> update -> delete) passed")


def test_delete_nonexistent_reward(admin_headers):
    print(f"\n  Sending DELETE /rewards.php?id=DOESNOTEXIST999 (ID that does not exist)...")
    resp = requests.delete(
        f"{BASE_URL}/rewards.php?id=DOESNOTEXIST999",
        headers=admin_headers,
    )
    print(f"  Response status : {resp.status_code}")
    print(f"  Checking: server returns 404 Not Found...")
    assert resp.status_code == 404
    print(f"  [PASS] Delete non-existent reward correctly returned 404")
