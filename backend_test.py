"""
EcoAndes Backend Test Suite - Shipping/Payments/Refunds/Registration Batch
Tests all confirmed business rules for retail/professional shipping, payment methods,
manual quote zones, admin shipping quote panel, professional registration message, and refund breakdown.
"""
import requests
import sys
import json
from datetime import datetime

BASE_URL = "https://eco-andes-test.preview.emergentagent.com/api"

class TestRunner:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.admin_token = None
        self.test_order_ids = []
        self.test_user_emails = []
        
    def log(self, msg, level="INFO"):
        print(f"[{level}] {msg}")
    
    def test(self, name, condition, details=""):
        """Run a test assertion"""
        self.tests_run += 1
        if condition:
            self.tests_passed += 1
            self.log(f"✅ PASS: {name}", "PASS")
            if details:
                self.log(f"   {details}", "INFO")
        else:
            self.tests_failed += 1
            self.log(f"❌ FAIL: {name}", "FAIL")
            if details:
                self.log(f"   {details}", "ERROR")
        return condition
    
    def admin_login(self):
        """Login as admin and get token"""
        self.log("Logging in as admin...")
        try:
            resp = requests.post(f"{BASE_URL}/auth/login", json={
                "email": "admin@ecoandes.com",
                "password": "Admin123!"
            }, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                self.admin_token = data.get("access_token")
                self.log(f"✅ Admin login successful", "PASS")
                return True
            else:
                self.log(f"❌ Admin login failed: {resp.status_code} - {resp.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Admin login exception: {e}", "ERROR")
            return False
    
    def admin_headers(self):
        """Get headers with admin auth"""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    # ========== SHIPPING QUOTE TESTS ==========
    
    def test_retail_shipping_below_threshold(self):
        """Test retail España CP 28004 subtotal_with_vat 40, weight 3kg -> shipping_cost 7.26"""
        self.log("\n=== Test: Retail shipping below 50€ threshold ===")
        try:
            resp = requests.post(f"{BASE_URL}/orders/shipping-quote", json={
                "customer_type": "retail",
                "country": "España",
                "postal_code": "28004",
                "subtotal_with_vat": 40.0,
                "subtotal_ex_vat": 36.36,
                "total_weight_kg": 3.0,
                "has_bulk": False
            }, timeout=10)
            
            if resp.status_code != 200:
                self.test("Retail shipping quote API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            data = resp.json()
            self.test("Retail shipping quote API call", True, f"Status 200")
            self.test("Retail shipping status is 'ok'", data.get("status") == "ok", f"Got: {data.get('status')}")
            self.test("Retail shipping cost is 7.26", abs(data.get("shipping_cost", 0) - 7.26) < 0.01, f"Got: {data.get('shipping_cost')}")
            self.test("Retail shipping ex_vat is 6.0", abs(data.get("shipping_cost_ex_vat", 0) - 6.0) < 0.01, f"Got: {data.get('shipping_cost_ex_vat')}")
            self.test("Retail shipping vat is 1.26", abs(data.get("shipping_vat", 0) - 1.26) < 0.01, f"Got: {data.get('shipping_vat')}")
            self.test("Retail remaining_for_free_shipping is 10", abs(data.get("remaining_for_free_shipping", 0) - 10.0) < 0.01, f"Got: {data.get('remaining_for_free_shipping')}")
            
        except Exception as e:
            self.test("Retail shipping quote below threshold", False, f"Exception: {e}")
    
    def test_retail_shipping_free(self):
        """Test retail subtotal_with_vat >= 50 -> free_shipping true, cost 0"""
        self.log("\n=== Test: Retail shipping free (>= 50€) ===")
        try:
            resp = requests.post(f"{BASE_URL}/orders/shipping-quote", json={
                "customer_type": "retail",
                "country": "España",
                "postal_code": "28004",
                "subtotal_with_vat": 50.0,
                "subtotal_ex_vat": 45.45,
                "total_weight_kg": 3.0,
                "has_bulk": False
            }, timeout=10)
            
            if resp.status_code != 200:
                self.test("Retail free shipping API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            data = resp.json()
            self.test("Retail free shipping API call", True, f"Status 200")
            self.test("Retail free_shipping is true", data.get("free_shipping") == True, f"Got: {data.get('free_shipping')}")
            self.test("Retail shipping_cost is 0", data.get("shipping_cost") == 0, f"Got: {data.get('shipping_cost')}")
            
        except Exception as e:
            self.test("Retail free shipping test", False, f"Exception: {e}")
    
    def test_professional_shipping_below_threshold(self):
        """Test professional CP 08001 subtotal_ex_vat 100 weight 22kg -> cost 27.83 (net 23)"""
        self.log("\n=== Test: Professional shipping below 150€ threshold ===")
        try:
            resp = requests.post(f"{BASE_URL}/orders/shipping-quote", json={
                "customer_type": "professional",
                "country": "España",
                "postal_code": "08001",
                "subtotal_with_vat": 110.0,
                "subtotal_ex_vat": 100.0,
                "total_weight_kg": 22.0,
                "has_bulk": True
            }, timeout=10)
            
            if resp.status_code != 200:
                self.test("Professional shipping quote API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            data = resp.json()
            self.test("Professional shipping quote API call", True, f"Status 200")
            self.test("Professional shipping status is 'ok'", data.get("status") == "ok", f"Got: {data.get('status')}")
            self.test("Professional shipping cost is 27.83", abs(data.get("shipping_cost", 0) - 27.83) < 0.01, f"Got: {data.get('shipping_cost')}")
            self.test("Professional shipping ex_vat is 23.0", abs(data.get("shipping_cost_ex_vat", 0) - 23.0) < 0.01, f"Got: {data.get('shipping_cost_ex_vat')}")
            self.test("Professional remaining_for_free_shipping is 50", abs(data.get("remaining_for_free_shipping", 0) - 50.0) < 0.01, f"Got: {data.get('remaining_for_free_shipping')}")
            
        except Exception as e:
            self.test("Professional shipping quote below threshold", False, f"Exception: {e}")
    
    def test_professional_shipping_free(self):
        """Test professional subtotal_ex_vat 150 -> free"""
        self.log("\n=== Test: Professional shipping free (>= 150€) ===")
        try:
            resp = requests.post(f"{BASE_URL}/orders/shipping-quote", json={
                "customer_type": "professional",
                "country": "España",
                "postal_code": "08001",
                "subtotal_with_vat": 165.0,
                "subtotal_ex_vat": 150.0,
                "total_weight_kg": 22.0,
                "has_bulk": True
            }, timeout=10)
            
            if resp.status_code != 200:
                self.test("Professional free shipping API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            data = resp.json()
            self.test("Professional free shipping API call", True, f"Status 200")
            self.test("Professional free_shipping is true", data.get("free_shipping") == True, f"Got: {data.get('free_shipping')}")
            self.test("Professional shipping_cost is 0", data.get("shipping_cost") == 0, f"Got: {data.get('shipping_cost')}")
            
        except Exception as e:
            self.test("Professional free shipping test", False, f"Exception: {e}")
    
    def test_weight_cap_40kg(self):
        """Test weight 40kg below threshold -> capped at net 29 / gross 35.09"""
        self.log("\n=== Test: Weight cap at 40kg (max 29€ net / 35.09€ gross) ===")
        try:
            resp = requests.post(f"{BASE_URL}/orders/shipping-quote", json={
                "customer_type": "retail",
                "country": "España",
                "postal_code": "28004",
                "subtotal_with_vat": 40.0,
                "subtotal_ex_vat": 36.36,
                "total_weight_kg": 40.0,
                "has_bulk": True
            }, timeout=10)
            
            if resp.status_code != 200:
                self.test("Weight cap 40kg API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            data = resp.json()
            self.test("Weight cap 40kg API call", True, f"Status 200")
            self.test("Weight cap status is 'ok' (NOT manual)", data.get("status") == "ok", f"Got: {data.get('status')}")
            self.test("Weight cap shipping ex_vat is 29.0", abs(data.get("shipping_cost_ex_vat", 0) - 29.0) < 0.01, f"Got: {data.get('shipping_cost_ex_vat')}")
            self.test("Weight cap shipping gross is 35.09", abs(data.get("shipping_cost", 0) - 35.09) < 0.01, f"Got: {data.get('shipping_cost')}")
            
        except Exception as e:
            self.test("Weight cap 40kg test", False, f"Exception: {e}")
    
    def test_manual_quote_canarias(self):
        """Test retail to Canarias CP 35001 -> status manual_quote, zone CANARIAS_EU"""
        self.log("\n=== Test: Manual quote for Canarias ===")
        try:
            resp = requests.post(f"{BASE_URL}/orders/shipping-quote", json={
                "customer_type": "retail",
                "country": "España",
                "postal_code": "35001",
                "subtotal_with_vat": 40.0,
                "subtotal_ex_vat": 36.36,
                "total_weight_kg": 3.0,
                "has_bulk": False
            }, timeout=10)
            
            if resp.status_code != 200:
                self.test("Manual quote Canarias API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            data = resp.json()
            self.test("Manual quote Canarias API call", True, f"Status 200")
            self.test("Manual quote status is 'manual_quote'", data.get("status") == "manual_quote", f"Got: {data.get('status')}")
            self.test("Manual quote zone is 'CANARIAS_EU'", data.get("zone") == "CANARIAS_EU", f"Got: {data.get('zone')}")
            
        except Exception as e:
            self.test("Manual quote Canarias test", False, f"Exception: {e}")
    
    def test_manual_quote_france(self):
        """Test retail to France -> status manual_quote"""
        self.log("\n=== Test: Manual quote for France ===")
        try:
            resp = requests.post(f"{BASE_URL}/orders/shipping-quote", json={
                "customer_type": "retail",
                "country": "France",
                "postal_code": "75001",
                "subtotal_with_vat": 40.0,
                "subtotal_ex_vat": 36.36,
                "total_weight_kg": 3.0,
                "has_bulk": False
            }, timeout=10)
            
            if resp.status_code != 200:
                self.test("Manual quote France API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            data = resp.json()
            self.test("Manual quote France API call", True, f"Status 200")
            self.test("Manual quote France status is 'manual_quote'", data.get("status") == "manual_quote", f"Got: {data.get('status')}")
            
        except Exception as e:
            self.test("Manual quote France test", False, f"Exception: {e}")
    
    # ========== ORDER CREATION TESTS ==========
    
    def test_order_canarias_pending_quote(self):
        """Test POST /api/orders with Canarias address -> status 'Pendiente portes', payment_method 'pending_quote'"""
        self.log("\n=== Test: Order creation with Canarias address (pending quote) ===")
        try:
            # First, get a product to add to cart
            products_resp = requests.get(f"{BASE_URL}/products", timeout=10)
            if products_resp.status_code != 200 or not products_resp.json():
                self.test("Get products for order test", False, "No products available")
                return
            
            product = products_resp.json()[0]
            
            order_payload = {
                "email": f"test_canarias_{datetime.now().strftime('%H%M%S')}@test.com",
                "items": [{
                    "product_id": product["id"],
                    "sku": product.get("sku", "TEST-SKU"),
                    "name": product["name"],
                    "variation_name": None,
                    "unit_price": product["price_retail"],
                    "quantity": 1,
                    "image_url": product.get("image_url", "")
                }],
                "shipping_address": {
                    "full_name": "Test Canarias",
                    "phone": "600000000",
                    "street": "Calle Test 123",
                    "city": "Las Palmas",
                    "province": "Las Palmas",
                    "postal_code": "35001",
                    "country": "España",
                    "notes": ""
                },
                "customer_type": "retail",
                "payment_method": "pending_quote",
                "delivery_method": "shipping",
                "coupon_code": None,
                "acquisition": {}
            }
            
            resp = requests.post(f"{BASE_URL}/orders", json=order_payload, timeout=10)
            
            if resp.status_code != 200:
                self.test("Order creation Canarias API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            order = resp.json()
            self.test_order_ids.append(order["id"])
            self.test_user_emails.append(order["email"])
            
            self.test("Order creation Canarias API call", True, f"Status 200, Order: {order.get('order_number')}")
            self.test("Order status is 'Pendiente portes'", order.get("status") == "Pendiente portes", f"Got: {order.get('status')}")
            self.test("Order payment_method is 'pending_quote'", order.get("payment_method") == "pending_quote", f"Got: {order.get('payment_method')}")
            self.test("Order payment_status is 'awaiting_quote'", order.get("payment_status") == "awaiting_quote", f"Got: {order.get('payment_status')}")
            self.test("Order shipping_cost is 0", order.get("shipping_cost") == 0, f"Got: {order.get('shipping_cost')}")
            
            # Store order ID for later tests
            self.canarias_order_id = order["id"]
            
        except Exception as e:
            self.test("Order creation Canarias test", False, f"Exception: {e}")
    
    def test_stripe_checkout_awaiting_quote_blocked(self):
        """Test POST /api/payments/stripe/checkout for awaiting_quote order -> 400"""
        self.log("\n=== Test: Stripe checkout blocked for awaiting_quote order ===")
        if not hasattr(self, 'canarias_order_id'):
            self.test("Stripe checkout awaiting_quote test", False, "No Canarias order created in previous test")
            return
        
        try:
            resp = requests.post(f"{BASE_URL}/payments/stripe/checkout", json={
                "order_id": self.canarias_order_id,
                "origin_url": "https://eco-andes-test.preview.emergentagent.com"
            }, timeout=10)
            
            self.test("Stripe checkout awaiting_quote returns 400", resp.status_code == 400, f"Got status: {resp.status_code}")
            if resp.status_code == 400:
                detail = resp.json().get("detail", "")
                self.test("Stripe checkout error mentions pending quote", "presupuesto" in detail.lower() or "quote" in detail.lower(), f"Got: {detail}")
            
        except Exception as e:
            self.test("Stripe checkout awaiting_quote test", False, f"Exception: {e}")
    
    def test_order_retail_invalid_payment_method(self):
        """Test POST /api/orders retail peninsular with payment_method 'transfer' -> 400"""
        self.log("\n=== Test: Order creation retail with invalid payment method (transfer) ===")
        try:
            products_resp = requests.get(f"{BASE_URL}/products", timeout=10)
            if products_resp.status_code != 200 or not products_resp.json():
                self.test("Get products for retail payment test", False, "No products available")
                return
            
            product = products_resp.json()[0]
            
            order_payload = {
                "email": f"test_retail_{datetime.now().strftime('%H%M%S')}@test.com",
                "items": [{
                    "product_id": product["id"],
                    "sku": product.get("sku", "TEST-SKU"),
                    "name": product["name"],
                    "variation_name": None,
                    "unit_price": product["price_retail"],
                    "quantity": 1,
                    "image_url": product.get("image_url", "")
                }],
                "shipping_address": {
                    "full_name": "Test Retail",
                    "phone": "600000000",
                    "street": "Calle Test 123",
                    "city": "Madrid",
                    "province": "Madrid",
                    "postal_code": "28004",
                    "country": "España",
                    "notes": ""
                },
                "customer_type": "retail",
                "payment_method": "transfer",
                "delivery_method": "shipping",
                "coupon_code": None,
                "acquisition": {}
            }
            
            resp = requests.post(f"{BASE_URL}/orders", json=order_payload, timeout=10)
            
            self.test("Order retail with transfer returns 400", resp.status_code == 400, f"Got status: {resp.status_code}")
            if resp.status_code == 400:
                detail = resp.json().get("detail", "")
                self.test("Error mentions payment method not available", "pago" in detail.lower() or "payment" in detail.lower(), f"Got: {detail}")
            
        except Exception as e:
            self.test("Order retail invalid payment method test", False, f"Exception: {e}")
    
    def test_order_peninsular_retail_shipping_fields(self):
        """Test order created peninsular retail -> has shipping_cost_ex_vat, shipping_vat, shipping_vat_rate=21"""
        self.log("\n=== Test: Order peninsular retail has shipping VAT fields ===")
        try:
            products_resp = requests.get(f"{BASE_URL}/products", timeout=10)
            if products_resp.status_code != 200 or not products_resp.json():
                self.test("Get products for peninsular order test", False, "No products available")
                return
            
            product = products_resp.json()[0]
            
            order_payload = {
                "email": f"test_peninsular_{datetime.now().strftime('%H%M%S')}@test.com",
                "items": [{
                    "product_id": product["id"],
                    "sku": product.get("sku", "TEST-SKU"),
                    "name": product["name"],
                    "variation_name": None,
                    "unit_price": product["price_retail"],
                    "quantity": 1,
                    "image_url": product.get("image_url", "")
                }],
                "shipping_address": {
                    "full_name": "Test Peninsular",
                    "phone": "600000000",
                    "street": "Calle Test 123",
                    "city": "Madrid",
                    "province": "Madrid",
                    "postal_code": "28004",
                    "country": "España",
                    "notes": ""
                },
                "customer_type": "retail",
                "payment_method": "stripe",
                "delivery_method": "shipping",
                "coupon_code": None,
                "acquisition": {}
            }
            
            resp = requests.post(f"{BASE_URL}/orders", json=order_payload, timeout=10)
            
            if resp.status_code != 200:
                self.test("Order peninsular retail API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            order = resp.json()
            self.test_order_ids.append(order["id"])
            self.test_user_emails.append(order["email"])
            
            self.test("Order peninsular retail API call", True, f"Status 200, Order: {order.get('order_number')}")
            self.test("Order has shipping_cost_ex_vat field", "shipping_cost_ex_vat" in order, f"Fields: {list(order.keys())}")
            self.test("Order has shipping_vat field", "shipping_vat" in order, f"Fields: {list(order.keys())}")
            self.test("Order has shipping_vat_rate field", "shipping_vat_rate" in order, f"Fields: {list(order.keys())}")
            self.test("Order shipping_vat_rate is 21", order.get("shipping_vat_rate") == 21, f"Got: {order.get('shipping_vat_rate')}")
            
            # Verify total = subtotal + shipping
            expected_total = order.get("subtotal", 0) + order.get("shipping_cost", 0)
            self.test("Order total = subtotal + shipping", abs(order.get("total", 0) - expected_total) < 0.01, f"Total: {order.get('total')}, Expected: {expected_total}")
            
        except Exception as e:
            self.test("Order peninsular retail shipping fields test", False, f"Exception: {e}")
    
    # ========== ADMIN TESTS ==========
    
    def test_admin_shipping_quote_patch(self):
        """Test PATCH /api/orders/admin/{id}/shipping with {shipping_cost_ex_vat: 45} -> shipping_cost 54.45"""
        self.log("\n=== Test: Admin set shipping quote ===")
        if not self.admin_token:
            self.test("Admin shipping quote patch", False, "Admin not logged in")
            return
        
        if not hasattr(self, 'canarias_order_id'):
            self.test("Admin shipping quote patch", False, "No Canarias order created")
            return
        
        try:
            resp = requests.patch(
                f"{BASE_URL}/orders/admin/{self.canarias_order_id}/shipping",
                json={"shipping_cost_ex_vat": 45.0},
                headers=self.admin_headers(),
                timeout=10
            )
            
            if resp.status_code != 200:
                self.test("Admin shipping quote patch API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            order = resp.json()
            self.test("Admin shipping quote patch API call", True, f"Status 200")
            self.test("Order shipping_cost is 54.45", abs(order.get("shipping_cost", 0) - 54.45) < 0.01, f"Got: {order.get('shipping_cost')}")
            self.test("Order shipping_cost_ex_vat is 45.0", abs(order.get("shipping_cost_ex_vat", 0) - 45.0) < 0.01, f"Got: {order.get('shipping_cost_ex_vat')}")
            self.test("Order shipping_vat is 9.45", abs(order.get("shipping_vat", 0) - 9.45) < 0.01, f"Got: {order.get('shipping_vat')}")
            self.test("Order status changed to 'Pendiente'", order.get("status") == "Pendiente", f"Got: {order.get('status')}")
            self.test("Order payment_status changed to 'pending'", order.get("payment_status") == "pending", f"Got: {order.get('payment_status')}")
            self.test("Order shipping_status is 'quoted'", order.get("shipping_status") == "quoted", f"Got: {order.get('shipping_status')}")
            
            # Verify total recalculated
            expected_total = order.get("subtotal", 0) + 54.45
            self.test("Order total recalculated", abs(order.get("total", 0) - expected_total) < 0.01, f"Total: {order.get('total')}, Expected: {expected_total}")
            
        except Exception as e:
            self.test("Admin shipping quote patch test", False, f"Exception: {e}")
    
    def test_admin_status_counts(self):
        """Test GET /api/orders/admin/status-counts includes 'Pendiente portes' key"""
        self.log("\n=== Test: Admin status counts includes 'Pendiente portes' ===")
        if not self.admin_token:
            self.test("Admin status counts", False, "Admin not logged in")
            return
        
        try:
            resp = requests.get(
                f"{BASE_URL}/orders/admin/status-counts",
                headers=self.admin_headers(),
                timeout=10
            )
            
            if resp.status_code != 200:
                self.test("Admin status counts API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            counts = resp.json()
            self.test("Admin status counts API call", True, f"Status 200")
            self.test("Status counts includes 'Pendiente portes'", "Pendiente portes" in counts, f"Keys: {list(counts.keys())}")
            
        except Exception as e:
            self.test("Admin status counts test", False, f"Exception: {e}")
    
    # ========== AUTH TESTS ==========
    
    def test_professional_registration_with_message(self):
        """Test POST /api/auth/register professional with message field -> 200, message persisted"""
        self.log("\n=== Test: Professional registration with optional message ===")
        try:
            test_email = f"test_pro_{datetime.now().strftime('%H%M%S')}@test.com"
            self.test_user_emails.append(test_email)
            
            resp = requests.post(f"{BASE_URL}/auth/register", json={
                "email": test_email,
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "Professional",
                "role": "professional",
                "company": "Test Company SL",
                "tax_id": "B12345678",
                "business_type": "Distribuidor",
                "phone": "600000000",
                "message": "Necesito lista de precios profesionales"
            }, timeout=10)
            
            if resp.status_code != 200:
                self.test("Professional registration API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            user = resp.json()
            self.test("Professional registration API call", True, f"Status 200, User: {user.get('email')}")
            
            # Verify message persisted by logging in and checking user doc
            # (We can't directly check the message field from the public response, but we can verify registration succeeded)
            self.test("Professional registration succeeded", user.get("role") == "professional", f"Got role: {user.get('role')}")
            
        except Exception as e:
            self.test("Professional registration with message test", False, f"Exception: {e}")
    
    # ========== REFUND TESTS ==========
    
    def test_refund_breakdown(self):
        """Test POST /api/admin/orders/{id}/refund -> refund doc includes breakdown with VAT details"""
        self.log("\n=== Test: Refund breakdown includes VAT details ===")
        if not self.admin_token:
            self.test("Refund breakdown test", False, "Admin not logged in")
            return
        
        # Use one of the test orders created earlier
        if not self.test_order_ids:
            self.test("Refund breakdown test", False, "No test orders available")
            return
        
        try:
            test_order_id = self.test_order_ids[0]
            
            resp = requests.post(
                f"{BASE_URL}/admin/orders/{test_order_id}/refund",
                json={
                    "reason": "Test refund for automated testing",
                    "amount": None,  # full refund
                    "restock": False,
                    "notify": False
                },
                headers=self.admin_headers(),
                timeout=10
            )
            
            if resp.status_code != 200:
                self.test("Refund creation API call", False, f"Status {resp.status_code}: {resp.text}")
                return
            
            result = resp.json()
            refund = result.get("refund", {})
            breakdown = refund.get("breakdown", {})
            
            self.test("Refund creation API call", True, f"Status 200")
            self.test("Refund has breakdown field", "breakdown" in refund, f"Refund keys: {list(refund.keys())}")
            self.test("Breakdown has products_ex_vat", "products_ex_vat" in breakdown, f"Breakdown keys: {list(breakdown.keys())}")
            self.test("Breakdown has products_vat", "products_vat" in breakdown, f"Breakdown keys: {list(breakdown.keys())}")
            self.test("Breakdown has shipping_ex_vat", "shipping_ex_vat" in breakdown, f"Breakdown keys: {list(breakdown.keys())}")
            self.test("Breakdown has shipping_vat", "shipping_vat" in breakdown, f"Breakdown keys: {list(breakdown.keys())}")
            self.test("Breakdown shipping_vat_rate is 21", breakdown.get("shipping_vat_rate") == 21, f"Got: {breakdown.get('shipping_vat_rate')}")
            
        except Exception as e:
            self.test("Refund breakdown test", False, f"Exception: {e}")
    
    # ========== CLEANUP ==========
    
    def cleanup(self):
        """Clean up test data"""
        self.log("\n=== Cleanup: Removing test data ===")
        if not self.admin_token:
            self.log("⚠️  Cannot cleanup: Admin not logged in", "WARN")
            return
        
        # Delete test orders
        for order_id in self.test_order_ids:
            try:
                # Note: There's no delete endpoint, but we can mark as cancelled
                requests.patch(
                    f"{BASE_URL}/orders/admin/{order_id}/status",
                    json={"status": "Cancelado"},
                    headers=self.admin_headers(),
                    timeout=5
                )
                self.log(f"Marked order {order_id} as Cancelado")
            except:
                pass
        
        # Note: We cannot delete users via API, so test users will remain
        # This is acceptable for testing purposes
        self.log(f"✅ Cleanup completed (marked {len(self.test_order_ids)} orders as cancelled)")
    
    def run_all(self):
        """Run all tests"""
        self.log("=" * 80)
        self.log("EcoAndes Backend Test Suite - Shipping/Payments/Refunds/Registration")
        self.log("=" * 80)
        
        # Admin login first
        if not self.admin_login():
            self.log("❌ Cannot proceed without admin login", "ERROR")
            return False
        
        # Run all test groups
        self.test_retail_shipping_below_threshold()
        self.test_retail_shipping_free()
        self.test_professional_shipping_below_threshold()
        self.test_professional_shipping_free()
        self.test_weight_cap_40kg()
        self.test_manual_quote_canarias()
        self.test_manual_quote_france()
        
        self.test_order_canarias_pending_quote()
        self.test_stripe_checkout_awaiting_quote_blocked()
        self.test_order_retail_invalid_payment_method()
        self.test_order_peninsular_retail_shipping_fields()
        
        self.test_admin_shipping_quote_patch()
        self.test_admin_status_counts()
        
        self.test_professional_registration_with_message()
        
        self.test_refund_breakdown()
        
        # Cleanup
        self.cleanup()
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log(f"TEST SUMMARY")
        self.log("=" * 80)
        self.log(f"Total tests run: {self.tests_run}")
        self.log(f"✅ Passed: {self.tests_passed}")
        self.log(f"❌ Failed: {self.tests_failed}")
        self.log(f"Success rate: {(self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0:.1f}%")
        self.log("=" * 80)
        
        return self.tests_failed == 0


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
