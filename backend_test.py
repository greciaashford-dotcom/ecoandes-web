"""
EcoAndes Backend Testing - Batch 6 Features
Tests: Recipes API, External Files API, Abandoned Carts 2nd Reminder
"""
import sys
import requests
from datetime import datetime, timedelta, timezone

BASE_URL = "https://eco-andes-test.preview.emergentagent.com"
ADMIN_EMAIL = "admin@ecoandes.com"
ADMIN_PASSWORD = "Admin123!"

class TestRunner:
    def __init__(self):
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def test(self, name, fn):
        """Run a single test"""
        self.tests_run += 1
        print(f"\n{'='*60}")
        print(f"TEST {self.tests_run}: {name}")
        print('='*60)
        try:
            fn()
            self.tests_passed += 1
            print(f"✅ PASSED: {name}")
            return True
        except AssertionError as e:
            self.tests_failed += 1
            self.failures.append(f"{name}: {e}")
            print(f"❌ FAILED: {name}")
            print(f"   Error: {e}")
            return False
        except Exception as e:
            self.tests_failed += 1
            self.failures.append(f"{name}: Unexpected error: {e}")
            print(f"❌ FAILED: {name}")
            print(f"   Unexpected error: {e}")
            return False

    def login_admin(self):
        """Login as admin and get token"""
        print(f"\n🔐 Logging in as admin: {ADMIN_EMAIL}")
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
        data = resp.json()
        assert "access_token" in data, "No access_token in response"
        self.token = data["access_token"]
        print(f"✅ Admin login successful")

    def headers(self):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        print(f"Total tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {self.tests_failed} ❌")
        if self.failures:
            print("\nFailed tests:")
            for f in self.failures:
                print(f"  - {f}")
        print('='*60)
        return 0 if self.tests_failed == 0 else 1


def main():
    runner = TestRunner()

    # Login first
    try:
        runner.login_admin()
    except Exception as e:
        print(f"❌ CRITICAL: Admin login failed: {e}")
        return 1

    # ========== RECIPES API TESTS ==========
    def test_recipes_public():
        """Test GET /api/recipes (public endpoint)"""
        resp = requests.get(f"{BASE_URL}/api/recipes")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "items" in data, "No 'items' in response"
        print(f"   Found {len(data['items'])} active recipe(s)")
        for item in data['items']:
            assert "video_url" in item, "Missing video_url"
            assert item.get("active") is not False, "Inactive item in public response"
            print(f"   - {item.get('title', 'Untitled')}: {item['video_url'][:50]}...")

    def test_recipes_admin_requires_auth():
        """Test GET /api/recipes/admin requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/recipes/admin")
        assert resp.status_code == 401, f"Expected 401 without token, got {resp.status_code}"
        print(f"   Correctly returns 401 without token")

    def test_recipes_admin_get():
        """Test GET /api/recipes/admin with auth"""
        resp = requests.get(f"{BASE_URL}/api/recipes/admin", headers=runner.headers())
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "items" in data, "No 'items' in response"
        print(f"   Found {len(data['items'])} recipe(s) in admin view")
        return data['items']

    def test_recipes_admin_put():
        """Test PUT /api/recipes/admin - save and restore"""
        # Get current list
        resp = requests.get(f"{BASE_URL}/api/recipes/admin", headers=runner.headers())
        assert resp.status_code == 200, f"Failed to get current recipes"
        original_items = resp.json()['items']
        print(f"   Original list has {len(original_items)} items")

        # Add a test item
        test_item = {
            "id": None,
            "order": len(original_items),
            "active": True,
            "video_url": "https://test.example.com/test-recipe.mp4",
            "title": "TEST Recipe (to be deleted)",
            "description": "Test recipe for automated testing"
        }
        test_list = original_items + [test_item]
        
        # Save with test item
        resp = requests.put(
            f"{BASE_URL}/api/recipes/admin",
            headers=runner.headers(),
            json={"items": test_list}
        )
        assert resp.status_code == 200, f"Failed to save: {resp.status_code} {resp.text}"
        data = resp.json()
        assert len(data['items']) == len(test_list), "Item count mismatch after save"
        print(f"   ✅ Saved list with test item ({len(data['items'])} items)")

        # Restore original list (cleanup)
        resp = requests.put(
            f"{BASE_URL}/api/recipes/admin",
            headers=runner.headers(),
            json={"items": original_items}
        )
        assert resp.status_code == 200, f"Failed to restore: {resp.status_code}"
        print(f"   ✅ Restored original list ({len(original_items)} items)")

    # ========== EXTERNAL FILES API TESTS ==========
    def test_external_files_requires_auth():
        """Test POST /api/admin/files/external requires auth"""
        resp = requests.post(
            f"{BASE_URL}/api/admin/files/external",
            json={"url": "https://example.com/test.jpg"}
        )
        assert resp.status_code in [401, 403], f"Expected 401/403 without token, got {resp.status_code}"
        print(f"   Correctly returns {resp.status_code} without token")

    def test_external_files_invalid_url():
        """Test POST /api/admin/files/external with invalid URL"""
        resp = requests.post(
            f"{BASE_URL}/api/admin/files/external",
            headers=runner.headers(),
            json={"url": "not-a-valid-url"}
        )
        assert resp.status_code == 400, f"Expected 400 for invalid URL, got {resp.status_code}"
        print(f"   Correctly rejects invalid URL with 400")

    def test_external_files_add_and_delete():
        """Test POST /api/admin/files/external and DELETE"""
        # Add external file
        test_url = "https://picsum.photos/seed/ecotest/400/300.jpg"
        resp = requests.post(
            f"{BASE_URL}/api/admin/files/external",
            headers=runner.headers(),
            json={"url": test_url}
        )
        assert resp.status_code == 200, f"Failed to add external file: {resp.status_code} {resp.text}"
        data = resp.json()
        assert "id" in data, "No 'id' in response"
        assert data.get("external") is True, "external flag not set"
        file_id = data["id"]
        print(f"   ✅ Added external file: {file_id}")

        # Verify it appears in list
        resp = requests.get(f"{BASE_URL}/api/admin/files?kind=image", headers=runner.headers())
        assert resp.status_code == 200, "Failed to list files"
        files = resp.json()['files']
        found = any(f['id'] == file_id for f in files)
        assert found, f"External file {file_id} not found in list"
        print(f"   ✅ External file appears in image list")

        # Delete the test file (cleanup)
        resp = requests.delete(f"{BASE_URL}/api/admin/files/{file_id}", headers=runner.headers())
        assert resp.status_code == 200, f"Failed to delete: {resp.status_code}"
        print(f"   ✅ Deleted test file {file_id}")

    def test_files_filter_video():
        """Test GET /api/admin/files?kind=video"""
        resp = requests.get(f"{BASE_URL}/api/admin/files?kind=video", headers=runner.headers())
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "files" in data, "No 'files' in response"
        print(f"   Found {len(data['files'])} video file(s)")
        for f in data['files']:
            ct = f.get('content_type', '')
            assert ct.startswith('video/'), f"Non-video file in video filter: {ct}"

    # ========== ABANDONED CARTS 2ND REMINDER TEST ==========
    def test_abandoned_carts_2nd_reminder():
        """Test 2nd reminder logic (24h) via direct DB manipulation"""
        print("   Testing 2nd reminder logic via Python...")
        
        # Import MongoDB client
        from pymongo import MongoClient
        from datetime import datetime, timedelta, timezone
        import uuid
        
        client = MongoClient("mongodb://localhost:27017")
        db = client["test_database"]
        
        # Create test cart with status 'reminded', updated 25h ago, reminder_sent 21h ago
        now = datetime.now(timezone.utc)
        test_cart_id = f"test_cart_{uuid.uuid4().hex[:8]}"
        test_cart = {
            "cart_id": test_cart_id,
            "email": "test_2nd_reminder@example.com",
            "items": [
                {
                    "product_id": "test-prod",
                    "name": "Test Product",
                    "quantity": 1,
                    "unit_price": 10.0
                }
            ],
            "subtotal": 10.0,
            "status": "reminded",
            "created_at": (now - timedelta(hours=26)).isoformat(),
            "updated_at": (now - timedelta(hours=25)).isoformat(),
            "reminder_sent_at": (now - timedelta(hours=21)).isoformat(),
            "reminder2_sent_at": None,
            "reminder_count": 1
        }
        
        db.abandoned_carts.insert_one(test_cart)
        print(f"   ✅ Created test cart: {test_cart_id}")
        
        # Import and run process_abandoned_carts
        sys.path.insert(0, '/app/backend')
        from routes.carts import process_abandoned_carts
        import asyncio
        
        sent_count = asyncio.run(process_abandoned_carts())
        print(f"   📧 process_abandoned_carts() sent {sent_count} reminder(s)")
        
        # Verify the cart was updated
        updated_cart = db.abandoned_carts.find_one({"cart_id": test_cart_id})
        assert updated_cart is not None, "Test cart not found after processing"
        assert updated_cart.get("reminder2_sent_at") is not None, "reminder2_sent_at not set"
        assert updated_cart.get("reminder_count") == 2, f"reminder_count should be 2, got {updated_cart.get('reminder_count')}"
        print(f"   ✅ Cart updated: reminder2_sent_at={updated_cart['reminder2_sent_at'][:19]}, reminder_count=2")
        
        # Run again - should NOT send again (idempotent)
        sent_count_2 = asyncio.run(process_abandoned_carts())
        print(f"   📧 Second run sent {sent_count_2} reminder(s) (should be 0)")
        assert sent_count_2 == 0, f"Expected 0 reminders on second run, got {sent_count_2}"
        print(f"   ✅ Idempotent: no duplicate reminders sent")
        
        # Cleanup
        db.abandoned_carts.delete_one({"cart_id": test_cart_id})
        print(f"   🧹 Cleaned up test cart")
        
        # Note about email failures
        print(f"   ℹ️  Email send failures are EXPECTED (Resend domain not verified)")

    # ========== RUN ALL TESTS ==========
    runner.test("Recipes: GET /api/recipes (public)", test_recipes_public)
    runner.test("Recipes: GET /api/recipes/admin requires auth", test_recipes_admin_requires_auth)
    runner.test("Recipes: GET /api/recipes/admin with auth", test_recipes_admin_get)
    runner.test("Recipes: PUT /api/recipes/admin (save & restore)", test_recipes_admin_put)
    
    runner.test("External Files: POST requires auth", test_external_files_requires_auth)
    runner.test("External Files: Invalid URL returns 400", test_external_files_invalid_url)
    runner.test("External Files: Add and delete", test_external_files_add_and_delete)
    runner.test("Files: Filter by kind=video", test_files_filter_video)
    
    runner.test("Abandoned Carts: 2nd reminder logic", test_abandoned_carts_2nd_reminder)

    return runner.summary()


if __name__ == "__main__":
    sys.exit(main())
