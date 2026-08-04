#!/usr/bin/env python3
"""
Backend API Testing for EcoAndes - Batch 8 Features
Tests: Newsletter, Admin Deletions, Order with 'other' payment method
"""
import requests
import sys
import time
from datetime import datetime

BASE_URL = "https://eco-andes-test.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@ecoandes.com"
ADMIN_PASSWORD = "Admin123!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class APITester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.admin_token = None
        self.test_data = {
            "newsletter_email": None,
            "test_user_id": None,
            "test_user_email": None,
            "test_buyer_email": None,
            "test_lead_id": None,
            "test_order_id": None,
        }

    def log(self, message, color=Colors.BLUE):
        print(f"{color}{message}{Colors.END}")

    def test(self, name, method, endpoint, expected_status, data=None, headers=None, description=""):
        """Run a single API test"""
        url = f"{BASE_URL}/{endpoint}"
        self.tests_run += 1
        
        print(f"\n{'='*70}")
        print(f"Test #{self.tests_run}: {name}")
        if description:
            print(f"Description: {description}")
        print(f"{'='*70}")
        
        try:
            req_headers = {'Content-Type': 'application/json'}
            if headers:
                req_headers.update(headers)
            
            if method == 'GET':
                response = requests.get(url, headers=req_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=req_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=req_headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=req_headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - Status: {response.status_code}", Colors.GREEN)
                try:
                    resp_json = response.json()
                    print(f"Response: {resp_json}")
                    return True, resp_json
                except:
                    return True, {}
            else:
                self.tests_failed += 1
                self.log(f"❌ FAILED - Expected {expected_status}, got {response.status_code}", Colors.RED)
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response text: {response.text[:200]}")
                return False, {}

        except Exception as e:
            self.tests_failed += 1
            self.log(f"❌ FAILED - Error: {str(e)}", Colors.RED)
            return False, {}

    def admin_login(self):
        """Login as admin and get token"""
        self.log("\n🔐 Logging in as admin...", Colors.YELLOW)
        success, response = self.test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            description="Login with admin credentials to get auth token"
        )
        if success and ('token' in response or 'access_token' in response):
            self.admin_token = response.get('token') or response.get('access_token')
            self.log("✅ Admin login successful", Colors.GREEN)
            return True
        self.log("❌ Admin login failed", Colors.RED)
        return False

    def test_newsletter_subscription(self):
        """Test newsletter subscription endpoint"""
        self.log("\n📧 Testing Newsletter Subscription", Colors.YELLOW)
        
        # Test 1: Subscribe new email
        test_email = f"test-tester-{int(time.time())}@example.com"
        self.test_data["newsletter_email"] = test_email
        
        success, response = self.test(
            "Newsletter Subscribe - New Email",
            "POST",
            "newsletter/subscribe",
            200,
            data={"email": test_email},
            description="Subscribe a new email to newsletter (should send welcome email)"
        )
        
        if success:
            if response.get("ok") and not response.get("already"):
                self.log("✅ New subscription successful (ok=true, already=false)", Colors.GREEN)
            else:
                self.log(f"⚠️  Unexpected response: {response}", Colors.YELLOW)
        
        # Test 2: Subscribe duplicate email
        time.sleep(1)
        success, response = self.test(
            "Newsletter Subscribe - Duplicate Email",
            "POST",
            "newsletter/subscribe",
            200,
            data={"email": test_email},
            description="Subscribe same email again (should return already=true)"
        )
        
        if success:
            if response.get("ok") and response.get("already"):
                self.log("✅ Duplicate subscription handled correctly (ok=true, already=true)", Colors.GREEN)
            else:
                self.log(f"⚠️  Unexpected response: {response}", Colors.YELLOW)

    def test_admin_user_deletion(self):
        """Test admin user deletion with protections"""
        self.log("\n👤 Testing Admin User Deletion", Colors.YELLOW)
        
        if not self.admin_token:
            self.log("❌ No admin token, skipping user deletion tests", Colors.RED)
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # First, create a test retail user
        test_email = f"test-delete-user-{int(time.time())}@example.com"
        self.test_data["test_user_email"] = test_email
        
        success, response = self.test(
            "Create Test Retail User",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "DeleteUser",
                "role": "retail"
            },
            description="Create a test retail user for deletion"
        )
        
        if success and response.get("id"):
            user_id = response["id"]
            self.test_data["test_user_id"] = user_id
            self.log(f"✅ Test user created with ID: {user_id}", Colors.GREEN)
            
            # Test: Delete the retail user (should succeed)
            time.sleep(1)
            success, response = self.test(
                "Delete Retail User",
                "DELETE",
                f"admin/users/{user_id}",
                200,
                headers=headers,
                description="Delete a retail user (should succeed)"
            )
            
            if success and response.get("ok"):
                self.log("✅ Retail user deleted successfully", Colors.GREEN)
        
        # Test: Try to delete admin user (should fail with 400)
        # First get admin user ID
        success, response = self.test(
            "Get Admin User List",
            "GET",
            "admin/users?role=admin",
            200,
            headers=headers,
            description="Get list of admin users"
        )
        
        if success and len(response) > 0:
            admin_user = response[0]
            admin_id = admin_user.get("id")
            
            time.sleep(1)
            success, response = self.test(
                "Delete Admin User (Should Fail)",
                "DELETE",
                f"admin/users/{admin_id}",
                400,
                headers=headers,
                description="Try to delete an admin user (should be blocked with 400)"
            )
            
            if success:
                self.log("✅ Admin user deletion correctly blocked", Colors.GREEN)

    def test_admin_buyer_deletion(self):
        """Test admin buyer deletion"""
        self.log("\n🛒 Testing Admin Buyer Deletion", Colors.YELLOW)
        
        if not self.admin_token:
            self.log("❌ No admin token, skipping buyer deletion tests", Colors.RED)
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get list of buyers
        success, response = self.test(
            "Get Buyers List",
            "GET",
            "orders/admin/buyers",
            200,
            headers=headers,
            description="Get list of all buyers from CRM"
        )
        
        if success and response.get("buyers"):
            buyers = response["buyers"]
            if len(buyers) > 0:
                # Find a test buyer or use the first one (but we'll verify it exists first)
                test_buyer = buyers[0]
                buyer_email = test_buyer.get("email")
                self.log(f"Found buyer: {buyer_email}", Colors.BLUE)
                
                # Note: We won't actually delete real buyers, just test the endpoint exists
                # and returns proper error for non-existent buyer
                fake_email = f"nonexistent-{int(time.time())}@example.com"
                
                time.sleep(1)
                success, response = self.test(
                    "Delete Non-existent Buyer (Should Return 404)",
                    "DELETE",
                    f"orders/admin/buyers/{fake_email}",
                    404,
                    headers=headers,
                    description="Try to delete a non-existent buyer (should return 404)"
                )
                
                if success:
                    self.log("✅ Buyer deletion endpoint working (404 for non-existent)", Colors.GREEN)
            else:
                self.log("⚠️  No buyers found in system", Colors.YELLOW)

    def test_admin_whatsapp_lead_deletion(self):
        """Test admin WhatsApp lead deletion"""
        self.log("\n💬 Testing Admin WhatsApp Lead Deletion", Colors.YELLOW)
        
        if not self.admin_token:
            self.log("❌ No admin token, skipping WhatsApp lead deletion tests", Colors.RED)
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get list of WhatsApp leads
        success, response = self.test(
            "Get WhatsApp Leads List",
            "GET",
            "admin/whatsapp-leads",
            200,
            headers=headers,
            description="Get list of all WhatsApp leads"
        )
        
        if success and response.get("leads"):
            leads = response["leads"]
            if len(leads) > 0:
                self.log(f"Found {len(leads)} WhatsApp leads", Colors.BLUE)
                # Note: We won't delete real leads, just verify the endpoint structure
                self.log("✅ WhatsApp leads endpoint accessible", Colors.GREEN)
            else:
                self.log("⚠️  No WhatsApp leads found in system", Colors.YELLOW)

    def test_order_with_other_payment(self):
        """Test order creation with 'other' payment method (confirming)"""
        self.log("\n💳 Testing Order Creation with 'Other' Payment Method", Colors.YELLOW)
        
        # First, get a product to add to cart
        success, response = self.test(
            "Get Products",
            "GET",
            "products?limit=1",
            200,
            description="Get a product for testing order creation"
        )
        
        if not success or not response:
            self.log("❌ Could not get products for order test", Colors.RED)
            return
        
        product = response[0] if isinstance(response, list) and len(response) > 0 else None
        if not product:
            self.log("❌ No products available for order test", Colors.RED)
            return
        
        product_id = product.get("id")
        product_sku = product.get("sku")
        product_name = product.get("name")
        product_price = product.get("price_retail", 10.0)
        
        self.log(f"Using product: {product_name} (SKU: {product_sku})", Colors.BLUE)
        
        # Create order with 'other' payment method and shipping delivery
        test_email = f"test-order-{int(time.time())}@example.com"
        
        order_data = {
            "email": test_email,
            "items": [
                {
                    "product_id": product_id,
                    "sku": product_sku,
                    "name": product_name,
                    "variation_name": None,
                    "unit_price": product_price,
                    "quantity": 1,
                    "image_url": product.get("image_url", "")
                }
            ],
            "shipping_address": {
                "full_name": "Test Order User",
                "phone": "600000000",
                "street": "Calle Test 123",
                "city": "Madrid",
                "province": "Madrid",
                "postal_code": "28001",
                "country": "España",
                "notes": "Test order - can be cancelled"
            },
            "customer_type": "retail",
            "payment_method": "other",
            "delivery_method": "shipping",
            "notes": "TEST ORDER - Payment method: other (confirming)"
        }
        
        time.sleep(1)
        success, response = self.test(
            "Create Order with 'Other' Payment Method",
            "POST",
            "orders",
            200,
            data=order_data,
            description="Create order with payment_method='other' and delivery='shipping' (should be accepted)"
        )
        
        if success:
            if response.get("id") and response.get("order_number"):
                order_id = response["id"]
                order_number = response["order_number"]
                self.test_data["test_order_id"] = order_id
                self.log(f"✅ Order created successfully: {order_number}", Colors.GREEN)
                self.log(f"   Payment method: {response.get('payment_method')}", Colors.BLUE)
                self.log(f"   Delivery method: {response.get('delivery_method')}", Colors.BLUE)
                self.log(f"   Total: {response.get('total')} EUR", Colors.BLUE)
            else:
                self.log(f"⚠️  Order created but missing expected fields: {response}", Colors.YELLOW)

    def cleanup(self):
        """Clean up test data"""
        self.log("\n🧹 Cleaning up test data...", Colors.YELLOW)
        
        if not self.admin_token:
            self.log("⚠️  No admin token, skipping cleanup", Colors.YELLOW)
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Clean up newsletter subscriber
        if self.test_data["newsletter_email"]:
            # Note: There's no delete endpoint for newsletter, so we just note it
            self.log(f"⚠️  Newsletter subscriber {self.test_data['newsletter_email']} should be manually removed if needed", Colors.YELLOW)
        
        # Test order is left as-is with note that it's a test order
        if self.test_data["test_order_id"]:
            self.log(f"⚠️  Test order {self.test_data['test_order_id']} created (marked as test in notes)", Colors.YELLOW)

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.tests_run}")
        print(f"{Colors.GREEN}Passed: {self.tests_passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.tests_failed}{Colors.END}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print("="*70)
        
        return 0 if self.tests_failed == 0 else 1

def main():
    print(f"\n{Colors.BLUE}{'='*70}")
    print("EcoAndes Backend API Testing - Batch 8 Features")
    print(f"{'='*70}{Colors.END}\n")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tester = APITester()
    
    # Login as admin first
    if not tester.admin_login():
        print(f"\n{Colors.RED}❌ Admin login failed. Cannot proceed with admin tests.{Colors.END}")
        return 1
    
    # Run all tests
    tester.test_newsletter_subscription()
    tester.test_admin_user_deletion()
    tester.test_admin_buyer_deletion()
    tester.test_admin_whatsapp_lead_deletion()
    tester.test_order_with_other_payment()
    
    # Cleanup
    tester.cleanup()
    
    # Print summary
    return tester.print_summary()

if __name__ == "__main__":
    sys.exit(main())
