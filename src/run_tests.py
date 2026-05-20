"""
JazSam / SalesPresso - Test Runner
Runs each test file individually and shows its own output block.
Run: python run_tests.py
"""
import os
import sys
import subprocess

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

TEST_FILES = [
    "test_admin_auth.py",
    "test_customer_auth.py",
    "test_products.py",
    "test_rewards.py",
    "test_input_validation.py",
    "test_z_session.py",
]

print("=" * 60)
print("  JazSam / SalesPresso - Automated Test Suite")
print("=" * 60)
print()

print("Installing dependencies...")
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
    check=True,
)
print()

results = []

for test_file in TEST_FILES:
    if not os.path.exists(test_file):
        print(f"  [SKIP] {test_file} not found — skipping.")
        results.append((test_file, "SKIPPED"))
        print()
        continue

    print("=" * 60)
    print(f"  Running: {test_file}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v", "-s", "--tb=short"],
    )

    results.append((test_file, result.returncode))
    print()

print("=" * 60)
print("  SUMMARY")
print("=" * 60)
all_passed = True
for test_file, code in results:
    if code == "SKIPPED":
        status = "SKIP  "
    elif code == 0:
        status = "PASSED"
    else:
        status = "FAILED"
        all_passed = False
    print(f"  {status}  {test_file}")
print("=" * 60)
print()

sys.exit(0 if all_passed else 1)
