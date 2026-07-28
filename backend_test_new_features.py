"""Backend API tests for EcoAndes NEW FEATURES: Analytics, Orders Management, Stripe Integration."""
import requests
import sys
import time
from typing import Dict, List, Optional

BASE_URL = "https://eco-andes-test.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@ecoandes.com"
ADMIN_PASSWORD = "Admin123!"


class TestRunner:
    def __init__(self):
        self.token: Optional[str] = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures: List[Dict] = []

    def test(self, name: str, method: str, endpoint: str, expected_status: int, 
             data: Optional[dict] = None, params: Optional[dict] = None, 
             auth: bool = False, validate_fn=None, headers_extra: Optional[dict] = None) -> tuple:
        """Run a single test."""
        url = f"{BASE_URL}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if headers_extra:
            headers.update(headers_extra)

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == "PATCH":
                response = requests.patch(url, json=data, headers=headers, timeout=15)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            
            if success:
                # Additional validation if provided
                if validate_fn:
                    try:
                        resp_data = response.json() if response.text else {}
                        validation_result = validate_fn(resp_data)
                        if not validation_result:
                            success = False
                            print(f"❌ FAILED - Validation failed")
                            self.failures.append({
                                "test": name,
                                "reason": "Validation failed",
                                "endpoint": endpoint
                            })
                    except Exception as e:
                        success = False
                        print(f"❌ FAILED - Validation error: {e}")
                        self.failures.append({
                            "test": name,
                            "reason": f"Validation error: {e}",
                            "endpoint": endpoint
                        })
                
                if success:
                    self.tests_passed += 1
                    print(f"✅ PASSED - Status: {response.status_code}")
                    return True, response.json() if response.text and response.headers.get('content-type', '').startswith('application/json') else {}
                else:
                    self.tests_failed += 1
                    return False, {}
            else:
                self.tests_failed += 1
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Response: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")
                self.failures.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "endpoint": endpoint
                })
                return False, {}

        except Exception as e:
            self.tests_failed += 1
            print(f"❌ FAILED - Exception: {str(e)}")
            self.failures.append({
                "test": name,
                "reason": str(e),
                "endpoint": endpoint
            })
            return False, {}

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total tests: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0:.1f}%")
        
        if self.failures:
            print("\n❌ FAILED TESTS:")
            for f in self.failures:
                print(f"  - {f['test']}")
                if 'expected' in f:
                    print(f"    Expected: {f['expected']}, Got: {f['actual']}")
                if 'reason' in f:
                    print(f"    Reason: {f['reason']}")
        
        return self.tests_failed == 0


def main():
    runner = TestRunner()
    
    print("="*60)
    print("🧪 ECOANDES NEW FEATURES BACKEND TESTS")
    print("="*60)
    
    # ========== AUTHENTICATION ==========
    print("\n" + "="*60)
    print("🔐 AUTHENTICATION")
    print("="*60)
    
    success, response = runner.test(
        "Admin login",
        "POST",
        "auth/login",
        200,
        data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if not success:
        print("\n❌ Cannot proceed without admin authentication")
        return 1
    
    runner.token = response.get("token") or response.get("access_token")
    if runner.token:
        print(f"✅ Admin token obtained: {runner.token[:20]}...")
    else:
        print(f"❌ No token in response: {response}")
        return 1
    
    # ========== ANALYTICS & TRACKING ==========
    print("\n" + "="*60)
    print("📊 ANALYTICS & TRACKING")
    print("="*60)
    
    # Test 1: POST /api/track/pageview with X-Forwarded-For header
    runner.test(
        "Track pageview with X-Forwarded-For header and referrer",
        "POST",
        "track/pageview",
        200,
        data={
            "session_id": "test-session-123",
            "visitor_id": "test-visitor-456",
            "path": "/tienda",
            "referrer": "https://www.instagram.com/",
            "utm_source": "",
            "utm_medium": "",
            "utm_campaign": ""
        },
        headers_extra={"X-Forwarded-For": "83.56.20.10"},
        validate_fn=lambda r: r.get("ok") == True
    )
    
    # Test 2: GET /api/admin/analytics/summary with date range
    runner.test(
        "Get analytics summary with date range",
        "GET",
        "admin/analytics/summary",
        200,
        params={"date_from": "2026-07-01", "date_to": "2026-07-31"},
        auth=True,
        validate_fn=lambda r: (
            "totals" in r and 
            "series" in r and 
            "sources" in r and 
            "countries" in r and 
            "referrers" in r and 
            "pages" in r and
            isinstance(r["totals"], dict) and
            "pageviews" in r["totals"] and
            "sessions" in r["totals"] and
            "visitors" in r["totals"] and
            "orders" in r["totals"] and
            "revenue" in r["totals"]
        )
    )
    
    # ========== ORDERS MANAGEMENT ==========
    print("\n" + "="*60)
    print("📦 ORDERS MANAGEMENT")
    print("="*60)
    
    # Test 3: GET /api/orders/admin/status-counts
    success, counts_response = runner.test(
        "Get order status counts",
        "GET",
        "orders/admin/status-counts",
        200,
        auth=True,
        validate_fn=lambda r: (
            "all" in r and
            "Pendiente" in r and
            "Pagado" in r and
            "Enviado" in r and
            "Completado" in r and
            "Cancelado" in r
        )
    )
    
    # Test 4: GET /api/orders/admin/list with filters
    runner.test(
        "Get orders list without filters",
        "GET",
        "orders/admin/list",
        200,
        auth=True,
        validate_fn=lambda r: isinstance(r, list)
    )
    
    runner.test(
        "Get orders list with date filter",
        "GET",
        "orders/admin/list",
        200,
        params={"date_from": "2026-01-01", "date_to": "2026-12-31"},
        auth=True,
        validate_fn=lambda r: isinstance(r, list)
    )
    
    runner.test(
        "Get orders list with source filter",
        "GET",
        "orders/admin/list",
        200,
        params={"source": "direct"},
        auth=True,
        validate_fn=lambda r: isinstance(r, list)
    )
    
    runner.test(
        "Get orders list with registered filter",
        "GET",
        "orders/admin/list",
        200,
        params={"registered": "1"},
        auth=True,
        validate_fn=lambda r: isinstance(r, list)
    )
    
    runner.test(
        "Get orders list with customer_type filter",
        "GET",
        "orders/admin/list",
        200,
        params={"customer_type": "retail"},
        auth=True,
        validate_fn=lambda r: isinstance(r, list)
    )
    
    runner.test(
        "Search orders by order number",
        "GET",
        "orders/admin/list",
        200,
        params={"search": "ECO-1"},
        auth=True,
        validate_fn=lambda r: isinstance(r, list)
    )
    
    # Test 5: Get a real product first
    print("\n📝 Getting real product for order test...")
    try:
        import requests
        prod_resp = requests.get(f"{BASE_URL}/products?limit=1", timeout=10)
        if prod_resp.status_code == 200:
            products = prod_resp.json()
            if products and len(products) > 0:
                product = products[0]
                product_id = product["id"]
                product_sku = product["sku"]
                product_name = product["name"]
                product_price = product.get("price_retail", 10.0)
                product_image = product.get("image_url", "")
                print(f"✅ Using product: {product_name} (SKU: {product_sku}, Price: {product_price})")
            else:
                print("❌ No products found, skipping order creation test")
                product_id = None
        else:
            print(f"❌ Failed to get products: {prod_resp.status_code}")
            product_id = None
    except Exception as e:
        print(f"❌ Error getting product: {e}")
        product_id = None
    
    # Test 5: Create order with acquisition data
    success = False
    order_response = {}
    if product_id:
        print("\n📝 Creating test order with acquisition data...")
        success, order_response = runner.test(
            "Create order with acquisition data",
            "POST",
            "orders",
            200,
            data={
                "email": "test-analytics@example.com",
                "customer_type": "retail",
                "items": [
                    {
                        "product_id": product_id,
                        "sku": product_sku,
                        "name": product_name,
                        "variation_name": None,
                        "unit_price": product_price,
                        "quantity": 1,
                        "image_url": product_image
                    }
                ],
                "shipping_address": {
                    "full_name": "Test User Analytics",
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
                "notes": "",
                "coupon_code": "",
                "acquisition": {
                    "referrer": "https://www.google.com/",
                    "landing_page": "/tienda",
                    "utm_source": "",
                    "utm_medium": "",
                    "utm_campaign": ""
                }
            },
            validate_fn=lambda r: (
                "id" in r and
                "order_number" in r and
                "acquisition" in r and
                r["acquisition"].get("source") == "google" and
                r["acquisition"].get("medium") == "organic"
            )
        )
    else:
        print("⚠️  Skipping order creation test - no product available")
    
    test_order_id = None
    if success and order_response:
        test_order_id = order_response.get("id")
        print(f"✅ Test order created: {order_response.get('order_number')} (ID: {test_order_id})")
    
    # Test 6: Bulk status update
    if test_order_id:
        runner.test(
            "Bulk update order status",
            "POST",
            "orders/admin/bulk-status",
            200,
            data={"ids": [test_order_id], "status": "Pagado"},
            auth=True,
            validate_fn=lambda r: r.get("updated") >= 0
        )
    
    # ========== STRIPE INTEGRATION ==========
    print("\n" + "="*60)
    print("💳 STRIPE INTEGRATION")
    print("="*60)
    
    # Test 7: Create Stripe checkout session
    if test_order_id:
        success, stripe_response = runner.test(
            "Create Stripe checkout session",
            "POST",
            "payments/stripe/checkout",
            200,
            data={
                "order_id": test_order_id,
                "origin_url": "https://eco-andes-test.preview.emergentagent.com"
            },
            validate_fn=lambda r: (
                "url" in r and
                "session_id" in r and
                r["url"].startswith("https://checkout.stripe.com")
            )
        )
        
        if success and stripe_response:
            session_id = stripe_response.get("session_id")
            print(f"✅ Stripe checkout URL created: {stripe_response.get('url')[:60]}...")
            
            # Test 8: Get Stripe payment status
            time.sleep(1)  # Brief pause before checking status
            runner.test(
                "Get Stripe payment status",
                "GET",
                f"payments/stripe/status/{session_id}",
                200,
                validate_fn=lambda r: (
                    "payment_status" in r and
                    "status" in r and
                    "order" in r
                )
            )
    
    # ========== PRINT SUMMARY ==========
    success = runner.print_summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
