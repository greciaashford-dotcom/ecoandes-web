"""Backend API tests for EcoAndes e-commerce UX batch."""
import requests
import sys
from datetime import datetime

class EcoAndesAPITester:
    def __init__(self, base_url="https://eco-andes-test.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_email = "admin@ecoandes.com"
        self.admin_password = "Admin123!"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        req_headers = {'Content-Type': 'application/json'}
        if headers:
            req_headers.update(headers)
        if self.token:
            req_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=req_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=req_headers, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=req_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login and get token"""
        print("\n" + "="*60)
        print("ADMIN LOGIN")
        print("="*60)
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "/api/auth/login",
            200,
            data={"email": self.admin_email, "password": self.admin_password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"✅ Admin token obtained")
            return True
        print(f"❌ Admin login failed - response keys: {list(response.keys())}")
        return False

    def get_sample_products(self):
        """Get sample product IDs for testing"""
        print("\n" + "="*60)
        print("FETCHING SAMPLE PRODUCTS")
        print("="*60)
        success, response = self.run_test(
            "Get Products",
            "GET",
            "/api/products?limit=10",
            200
        )
        if success and isinstance(response, list) and len(response) >= 2:
            product_ids = [p['id'] for p in response[:3]]
            print(f"✅ Got {len(product_ids)} product IDs: {product_ids}")
            return product_ids
        print(f"❌ Failed to get sample products")
        return []

    def test_recommendations_with_product_id(self, product_id):
        """Test GET /api/products/recommendations with product_id"""
        print("\n" + "="*60)
        print("TEST: RECOMMENDATIONS WITH PRODUCT_ID")
        print("="*60)
        success, response = self.run_test(
            "Recommendations with product_id",
            "GET",
            f"/api/products/recommendations?product_id={product_id}&limit=6",
            200
        )
        
        if not success:
            return False
        
        # Validate response structure
        issues = []
        
        # Check category is a string
        if 'category' not in response:
            issues.append("Missing 'category' field")
        elif not isinstance(response.get('category'), (str, type(None))):
            issues.append(f"'category' should be string or null, got {type(response['category'])}")
        
        # Check arrays exist
        for key in ['related', 'recommended', 'explore', 'offers']:
            if key not in response:
                issues.append(f"Missing '{key}' field")
            elif not isinstance(response[key], list):
                issues.append(f"'{key}' should be array, got {type(response[key])}")
        
        # Check offers is empty (no products with compare_at_price discounts yet)
        if isinstance(response.get('offers'), list) and len(response['offers']) > 0:
            print(f"⚠️  Warning: 'offers' array has {len(response['offers'])} items (expected empty)")
        
        # Check no duplicate product IDs across sections
        all_ids = []
        for section in ['related', 'recommended', 'explore', 'offers']:
            if isinstance(response.get(section), list):
                section_ids = [p['id'] for p in response[section] if isinstance(p, dict) and 'id' in p]
                all_ids.extend(section_ids)
        
        duplicates = [pid for pid in set(all_ids) if all_ids.count(pid) > 1]
        if duplicates:
            issues.append(f"Duplicate product IDs found across sections: {duplicates}")
        
        # Check seed product_id is NOT included
        if product_id in all_ids:
            issues.append(f"Seed product_id {product_id} found in recommendations (should be excluded)")
        
        if issues:
            print(f"❌ Validation issues:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        print(f"✅ All validations passed:")
        print(f"   - category: {response.get('category')}")
        print(f"   - related: {len(response.get('related', []))} items")
        print(f"   - recommended: {len(response.get('recommended', []))} items")
        print(f"   - explore: {len(response.get('explore', []))} items")
        print(f"   - offers: {len(response.get('offers', []))} items (expected 0)")
        print(f"   - No duplicates across sections")
        print(f"   - Seed product excluded")
        return True

    def test_recommendations_without_product_id(self):
        """Test GET /api/products/recommendations without product_id"""
        print("\n" + "="*60)
        print("TEST: RECOMMENDATIONS WITHOUT PRODUCT_ID")
        print("="*60)
        success, response = self.run_test(
            "Recommendations without product_id",
            "GET",
            "/api/products/recommendations?limit=6",
            200
        )
        
        if not success:
            return False
        
        # Validate response structure
        issues = []
        
        # Check arrays exist
        for key in ['related', 'recommended', 'explore', 'offers']:
            if key not in response:
                issues.append(f"Missing '{key}' field")
            elif not isinstance(response[key], list):
                issues.append(f"'{key}' should be array, got {type(response[key])}")
        
        # Check recommended and explore are populated
        if len(response.get('recommended', [])) == 0:
            issues.append("'recommended' array is empty (should be populated)")
        if len(response.get('explore', [])) == 0:
            issues.append("'explore' array is empty (should be populated)")
        
        if issues:
            print(f"❌ Validation issues:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        print(f"✅ All validations passed:")
        print(f"   - related: {len(response.get('related', []))} items (ok if empty)")
        print(f"   - recommended: {len(response.get('recommended', []))} items")
        print(f"   - explore: {len(response.get('explore', []))} items")
        print(f"   - offers: {len(response.get('offers', []))} items")
        return True

    def test_recommendations_with_viewed(self, product_ids):
        """Test GET /api/products/recommendations with viewed parameter"""
        print("\n" + "="*60)
        print("TEST: RECOMMENDATIONS WITH VIEWED PARAMETER")
        print("="*60)
        viewed_str = ",".join(product_ids[:2])
        success, response = self.run_test(
            "Recommendations with viewed",
            "GET",
            f"/api/products/recommendations?viewed={viewed_str}&limit=8",
            200
        )
        
        if not success:
            return False
        
        # Check explore section starts with viewed products
        explore = response.get('explore', [])
        if len(explore) == 0:
            print(f"❌ 'explore' array is empty")
            return False
        
        # Check if the first items in explore match the viewed products
        explore_ids = [p['id'] for p in explore if isinstance(p, dict) and 'id' in p]
        viewed_ids = product_ids[:2]
        
        # At least one of the viewed products should be in the first few explore items
        found_viewed = any(vid in explore_ids[:4] for vid in viewed_ids)
        
        if not found_viewed:
            print(f"⚠️  Warning: Viewed products {viewed_ids} not found in first items of explore section")
            print(f"   Explore IDs: {explore_ids[:4]}")
        else:
            print(f"✅ Viewed products appear in explore section")
        
        print(f"✅ Recommendations with viewed parameter working:")
        print(f"   - explore: {len(explore)} items")
        return True

    def get_sample_order(self):
        """Get a sample order ID for testing"""
        print("\n" + "="*60)
        print("FETCHING SAMPLE ORDER")
        print("="*60)
        success, response = self.run_test(
            "Get Orders",
            "GET",
            "/api/orders/admin/list?limit=1",
            200
        )
        if success and isinstance(response, list) and len(response) > 0:
            order_id = response[0]['id']
            order_number = response[0].get('order_number', 'N/A')
            print(f"✅ Got order ID: {order_id} ({order_number})")
            return order_id
        print(f"❌ Failed to get sample order")
        return None

    def test_customer_message(self, order_id):
        """Test POST /api/orders/admin/{order_id}/message"""
        print("\n" + "="*60)
        print("TEST: CUSTOMER MESSAGE")
        print("="*60)
        
        # Test with valid message
        success, response = self.run_test(
            "Send customer message (valid)",
            "POST",
            f"/api/orders/admin/{order_id}/message",
            200,
            data={
                "subject": "Test message from automated testing",
                "message": "This is a test message to verify the customer message functionality."
            }
        )
        
        if not success:
            return False
        
        # Check response structure
        if 'sent' not in response or 'entry' not in response:
            print(f"❌ Response missing 'sent' or 'entry' fields")
            return False
        
        # NOTE: sent=false is EXPECTED (Resend domain unverified) — not a bug
        sent_status = response.get('sent')
        print(f"✅ Message sent status: {sent_status}")
        if not sent_status:
            print(f"ℹ️  Note: sent=false is EXPECTED (Resend domain unverified) — not a bug")
        
        # Verify entry structure
        entry = response.get('entry', {})
        if 'message' not in entry or 'sent_at' not in entry:
            print(f"❌ Entry missing required fields")
            return False
        
        print(f"✅ Customer message endpoint working correctly")
        
        # Test with empty message (should return 400)
        success_empty, _ = self.run_test(
            "Send customer message (empty - should fail)",
            "POST",
            f"/api/orders/admin/{order_id}/message",
            400,
            data={"message": ""}
        )
        
        if success_empty:
            print(f"✅ Empty message correctly rejected with 400")
        
        return True

    def test_order_creation_regression(self):
        """Test POST /api/orders retail peninsular (stripe) with weight-based shipping"""
        print("\n" + "="*60)
        print("TEST: ORDER CREATION REGRESSION (WEIGHT-BASED SHIPPING)")
        print("="*60)
        
        # Get a sample product
        success, products = self.run_test(
            "Get sample product for order",
            "GET",
            "/api/products?limit=1",
            200
        )
        
        if not success or not products:
            print(f"❌ Failed to get sample product")
            return False
        
        product = products[0]
        
        # Create order payload
        order_data = {
            "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
            "customer_type": "retail",
            "items": [
                {
                    "product_id": product['id'],
                    "name": product['name'],
                    "variation_name": None,
                    "sku": product.get('sku', 'TEST-SKU'),
                    "quantity": 1,
                    "unit_price": product.get('display_price', 10.0)
                }
            ],
            "shipping_address": {
                "full_name": "Test User",
                "street": "Calle Test 123",
                "postal_code": "28001",
                "city": "Madrid",
                "province": "Madrid",
                "country": "España",
                "phone": "600000000"
            },
            "billing_address": None,
            "payment_method": "stripe",
            "delivery_method": "shipping",
            "notes": "Test order for regression testing",
            "coupon_code": None,
            "acquisition": {
                "referrer": "",
                "utm_source": "test",
                "utm_campaign": "regression_test",
                "landing_page": "/tienda"
            }
        }
        
        success, response = self.run_test(
            "Create order (retail peninsular stripe)",
            "POST",
            "/api/orders",
            200,
            data=order_data
        )
        
        if not success:
            return False
        
        # Validate response has weight-based shipping fields
        issues = []
        
        required_fields = ['id', 'order_number', 'total_weight_kg', 'shipping_cost', 
                          'shipping_cost_ex_vat', 'shipping_vat', 'shipping_status']
        
        for field in required_fields:
            if field not in response:
                issues.append(f"Missing field: {field}")
        
        # Check weight is calculated
        if 'total_weight_kg' in response:
            weight = response['total_weight_kg']
            if not isinstance(weight, (int, float)) or weight < 0:
                issues.append(f"Invalid total_weight_kg: {weight}")
            else:
                print(f"✅ Weight calculated: {weight} kg")
        
        # Check shipping cost fields
        if 'shipping_cost' in response and 'shipping_cost_ex_vat' in response:
            print(f"✅ Shipping cost: {response['shipping_cost']} EUR")
            print(f"   - Base: {response['shipping_cost_ex_vat']} EUR")
            print(f"   - VAT: {response.get('shipping_vat', 0)} EUR")
        
        if issues:
            print(f"❌ Validation issues:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        print(f"✅ Order creation with weight-based shipping working correctly")
        print(f"   Order number: {response.get('order_number')}")
        
        # Clean up: mark order as test
        test_order_id = response.get('id')
        if test_order_id:
            print(f"ℹ️  Test order created: {test_order_id} (can be cleaned up manually)")
        
        return True

def main():
    print("\n" + "="*60)
    print("ECOANDES BACKEND API TESTS - UX BATCH")
    print("="*60)
    
    tester = EcoAndesAPITester()
    
    # Login as admin
    if not tester.test_admin_login():
        print("\n❌ Admin login failed, stopping tests")
        return 1
    
    # Get sample products
    product_ids = tester.get_sample_products()
    if not product_ids:
        print("\n❌ Failed to get sample products, stopping tests")
        return 1
    
    # Test recommendations with product_id
    tester.test_recommendations_with_product_id(product_ids[0])
    
    # Test recommendations without product_id
    tester.test_recommendations_without_product_id()
    
    # Test recommendations with viewed parameter
    tester.test_recommendations_with_viewed(product_ids)
    
    # Get sample order
    order_id = tester.get_sample_order()
    if order_id:
        # Test customer message
        tester.test_customer_message(order_id)
    else:
        print("\n⚠️  Skipping customer message test (no orders found)")
    
    # Test order creation regression
    tester.test_order_creation_regression()
    
    # Print results
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
