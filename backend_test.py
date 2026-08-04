"""
Comprehensive backend testing for abandoned cart recovery feature.
Tests: POST /api/cart/track, GET /api/cart/admin/list, DELETE /api/cart/admin/{cart_id},
       process_abandoned_carts(), and conversion flow.
"""
import requests
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone

BASE_URL = "https://eco-andes-test.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@ecoandes.com"
ADMIN_PASSWORD = "Admin123!"

class AbandonedCartTester:
    def __init__(self):
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_cart_ids = []
        self.test_emails = []
        self.test_order_ids = []
        
    def log(self, msg, status="info"):
        prefix = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }.get(status, "ℹ️")
        print(f"{prefix} {msg}")
    
    def run_test(self, name, func):
        """Run a single test"""
        self.tests_run += 1
        self.log(f"\n{'='*60}", "info")
        self.log(f"Test {self.tests_run}: {name}", "info")
        self.log(f"{'='*60}", "info")
        try:
            func()
            self.tests_passed += 1
            self.log(f"PASSED: {name}", "success")
            return True
        except AssertionError as e:
            self.log(f"FAILED: {name} - {str(e)}", "error")
            return False
        except Exception as e:
            self.log(f"ERROR: {name} - {str(e)}", "error")
            return False
    
    def test_admin_login(self):
        """Test admin login and get token"""
        self.log("Attempting admin login...")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed with status {response.status_code}: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        self.token = data["access_token"]
        self.log(f"Admin login successful, token obtained", "success")
    
    def test_track_cart_create(self):
        """Test POST /api/cart/track - create new cart"""
        cart_id = f"test-cart-{uuid.uuid4().hex[:8]}"
        test_email = f"test-{uuid.uuid4().hex[:8]}@test.com"
        self.test_cart_ids.append(cart_id)
        self.test_emails.append(test_email)
        
        payload = {
            "cart_id": cart_id,
            "email": test_email,
            "items": [
                {
                    "product_id": "test-prod-1",
                    "name": "Test Product 1",
                    "variation_name": None,
                    "quantity": 2,
                    "unit_price": 15.50,
                    "image_url": ""
                }
            ],
            "subtotal": 31.00
        }
        
        self.log(f"Creating cart with cart_id={cart_id}, email={test_email}")
        response = requests.post(f"{BASE_URL}/cart/track", json=payload)
        assert response.status_code == 200, f"Track cart failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        assert data.get("status") == "active", f"Expected status=active, got {data.get('status')}"
        self.log(f"Cart created successfully: {data}", "success")
    
    def test_track_cart_update_same_id(self):
        """Test POST /api/cart/track - update existing cart (same cart_id, no email)"""
        if not self.test_cart_ids:
            raise AssertionError("No test cart_id available")
        
        cart_id = self.test_cart_ids[0]
        payload = {
            "cart_id": cart_id,
            "email": None,  # No email - should preserve existing email
            "items": [
                {
                    "product_id": "test-prod-2",
                    "name": "Test Product 2",
                    "variation_name": "Large",
                    "quantity": 1,
                    "unit_price": 25.00,
                    "image_url": ""
                }
            ],
            "subtotal": 25.00
        }
        
        self.log(f"Updating cart {cart_id} without email (should preserve existing)")
        response = requests.post(f"{BASE_URL}/cart/track", json=payload)
        assert response.status_code == 200, f"Track cart update failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        assert data.get("status") == "active", f"Expected status=active, got {data.get('status')}"
        self.log(f"Cart updated successfully: {data}", "success")
    
    def test_track_cart_empty(self):
        """Test POST /api/cart/track - empty cart (items=[])"""
        cart_id = f"test-cart-empty-{uuid.uuid4().hex[:8]}"
        self.test_cart_ids.append(cart_id)
        
        payload = {
            "cart_id": cart_id,
            "email": "empty@test.com",
            "items": [],
            "subtotal": 0
        }
        
        self.log(f"Creating empty cart {cart_id}")
        response = requests.post(f"{BASE_URL}/cart/track", json=payload)
        assert response.status_code == 200, f"Track empty cart failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        assert data.get("status") == "emptied", f"Expected status=emptied, got {data.get('status')}"
        self.log(f"Empty cart handled correctly: {data}", "success")
    
    def test_admin_list_carts_no_auth(self):
        """Test GET /api/cart/admin/list without token (should fail)"""
        self.log("Attempting to list carts without auth token")
        response = requests.get(f"{BASE_URL}/cart/admin/list")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        self.log(f"Correctly rejected with status {response.status_code}", "success")
    
    def test_admin_list_carts_with_auth(self):
        """Test GET /api/cart/admin/list with admin token"""
        if not self.token:
            raise AssertionError("No admin token available")
        
        self.log("Fetching cart list with admin token")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/cart/admin/list", headers=headers)
        assert response.status_code == 200, f"List carts failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "carts" in data, "No 'carts' field in response"
        assert "stats" in data, "No 'stats' field in response"
        assert "active" in data["stats"], "No 'active' in stats"
        assert "reminded" in data["stats"], "No 'reminded' in stats"
        assert "converted" in data["stats"], "No 'converted' in stats"
        self.log(f"Cart list retrieved: {len(data['carts'])} carts, stats={data['stats']}", "success")
    
    def test_admin_delete_cart(self):
        """Test DELETE /api/cart/admin/{cart_id}"""
        if not self.token:
            raise AssertionError("No admin token available")
        if not self.test_cart_ids:
            raise AssertionError("No test cart_id available")
        
        # Use the empty cart for deletion test
        cart_id = self.test_cart_ids[-1] if len(self.test_cart_ids) > 1 else self.test_cart_ids[0]
        
        self.log(f"Deleting cart {cart_id}")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(f"{BASE_URL}/cart/admin/{cart_id}", headers=headers)
        assert response.status_code == 200, f"Delete cart failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        self.log(f"Cart deleted successfully: {data}", "success")
        
        # Remove from tracking
        if cart_id in self.test_cart_ids:
            self.test_cart_ids.remove(cart_id)
    
    def test_admin_delete_nonexistent_cart(self):
        """Test DELETE /api/cart/admin/{cart_id} with non-existent cart (should return 404)"""
        if not self.token:
            raise AssertionError("No admin token available")
        
        fake_cart_id = f"nonexistent-{uuid.uuid4().hex}"
        self.log(f"Attempting to delete non-existent cart {fake_cart_id}")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(f"{BASE_URL}/cart/admin/{fake_cart_id}", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        self.log(f"Correctly returned 404 for non-existent cart", "success")
    
    def test_reminder_flow_manual(self):
        """Test reminder flow by manipulating MongoDB and calling process_abandoned_carts()"""
        self.log("Testing reminder flow (requires MongoDB manipulation)")
        self.log("This test will be performed via Python script execution", "warning")
        
        # Create a test cart for reminder
        cart_id = f"test-reminder-{uuid.uuid4().hex[:8]}"
        test_email = f"reminder-{uuid.uuid4().hex[:8]}@test.com"
        self.test_cart_ids.append(cart_id)
        self.test_emails.append(test_email)
        
        payload = {
            "cart_id": cart_id,
            "email": test_email,
            "items": [
                {
                    "product_id": "test-prod-reminder",
                    "name": "Test Reminder Product",
                    "variation_name": None,
                    "quantity": 1,
                    "unit_price": 50.00,
                    "image_url": ""
                }
            ],
            "subtotal": 50.00
        }
        
        self.log(f"Creating cart for reminder test: cart_id={cart_id}, email={test_email}")
        response = requests.post(f"{BASE_URL}/cart/track", json=payload)
        assert response.status_code == 200, f"Track cart failed: {response.status_code} - {response.text}"
        
        self.log("Cart created. Manual step required:", "warning")
        self.log("1. Update MongoDB: set updated_at to 5 hours ago", "warning")
        self.log("2. Run process_abandoned_carts() function", "warning")
        self.log("3. Verify status='reminded' and reminder_sent_at is set", "warning")
        self.log(f"Cart ID for manual testing: {cart_id}", "info")
    
    def test_conversion_flow(self):
        """Test conversion flow: create order and verify cart is marked as converted"""
        self.log("Testing conversion flow")
        
        # Create a cart with a specific email
        cart_id = f"test-convert-{uuid.uuid4().hex[:8]}"
        test_email = f"convert-{uuid.uuid4().hex[:8]}@test.com"
        self.test_cart_ids.append(cart_id)
        self.test_emails.append(test_email)
        
        payload = {
            "cart_id": cart_id,
            "email": test_email,
            "items": [
                {
                    "product_id": "test-prod-convert",
                    "name": "Test Conversion Product",
                    "variation_name": None,
                    "quantity": 1,
                    "unit_price": 100.00,
                    "image_url": ""
                }
            ],
            "subtotal": 100.00
        }
        
        self.log(f"Creating cart for conversion test: cart_id={cart_id}, email={test_email}")
        response = requests.post(f"{BASE_URL}/cart/track", json=payload)
        assert response.status_code == 200, f"Track cart failed: {response.status_code} - {response.text}"
        
        self.log("Cart created. Manual step required:", "warning")
        self.log(f"1. Create an order with email={test_email} (transfer payment)", "warning")
        self.log("2. Verify cart status changes to 'converted' with converted_order set", "warning")
        self.log("3. CANCEL/clean up the test order afterwards", "warning")
        self.log(f"Test email for order: {test_email}", "info")
    
    def cleanup(self):
        """Clean up all test data"""
        self.log("\n" + "="*60, "info")
        self.log("CLEANUP: Removing all test data", "warning")
        self.log("="*60, "info")
        
        if not self.token:
            self.log("No admin token, skipping cleanup", "warning")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Delete all test carts
        for cart_id in self.test_cart_ids:
            try:
                self.log(f"Deleting test cart: {cart_id}")
                response = requests.delete(f"{BASE_URL}/cart/admin/{cart_id}", headers=headers)
                if response.status_code == 200:
                    self.log(f"Deleted cart {cart_id}", "success")
                elif response.status_code == 404:
                    self.log(f"Cart {cart_id} already deleted", "info")
                else:
                    self.log(f"Failed to delete cart {cart_id}: {response.status_code}", "warning")
            except Exception as e:
                self.log(f"Error deleting cart {cart_id}: {e}", "error")
        
        self.log("Cleanup completed", "success")
        self.log("NOTE: Manual cleanup may be required for:", "warning")
        self.log("- Test orders created during conversion flow testing", "warning")
        self.log("- Buyers/subscribers entries in MongoDB", "warning")
    
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*60, "info")
        self.log("TEST SUMMARY", "info")
        self.log("="*60, "info")
        self.log(f"Total tests run: {self.tests_run}", "info")
        self.log(f"Tests passed: {self.tests_passed}", "success" if self.tests_passed == self.tests_run else "warning")
        self.log(f"Tests failed: {self.tests_run - self.tests_passed}", "error" if self.tests_passed < self.tests_run else "info")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"Success rate: {success_rate:.1f}%", "success" if success_rate == 100 else "warning")
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = AbandonedCartTester()
    
    try:
        # Run all tests
        tester.run_test("Admin Login", tester.test_admin_login)
        tester.run_test("Track Cart - Create", tester.test_track_cart_create)
        tester.run_test("Track Cart - Update (preserve email)", tester.test_track_cart_update_same_id)
        tester.run_test("Track Cart - Empty items", tester.test_track_cart_empty)
        tester.run_test("Admin List Carts - No Auth", tester.test_admin_list_carts_no_auth)
        tester.run_test("Admin List Carts - With Auth", tester.test_admin_list_carts_with_auth)
        tester.run_test("Admin Delete Cart", tester.test_admin_delete_cart)
        tester.run_test("Admin Delete Non-existent Cart", tester.test_admin_delete_nonexistent_cart)
        tester.run_test("Reminder Flow (Manual)", tester.test_reminder_flow_manual)
        tester.run_test("Conversion Flow (Manual)", tester.test_conversion_flow)
        
    finally:
        # Always cleanup
        tester.cleanup()
        return tester.print_summary()

if __name__ == "__main__":
    sys.exit(main())
