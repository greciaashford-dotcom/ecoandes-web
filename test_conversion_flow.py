"""
Test the conversion flow by:
1. Creating a cart via API
2. Creating an order with the same email (transfer payment)
3. Verifying the cart status is 'converted' with converted_order set
4. Cleaning up the test order and cart
"""
import sys
import os
import uuid
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

sys.path.insert(0, '/app/backend')

BASE_URL = "https://eco-andes-test.preview.emergentagent.com/api"
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"
ADMIN_EMAIL = "admin@ecoandes.com"
ADMIN_PASSWORD = "Admin123!"

async def test_conversion_flow():
    print("="*60)
    print("TESTING CONVERSION FLOW")
    print("="*60)
    
    # Step 1: Login as admin to get token
    print(f"\n1️⃣ Logging in as admin...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code != 200:
        print(f"❌ Admin login failed: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    print(f"✅ Admin login successful")
    
    # Step 2: Create a test cart via API
    cart_id = f"test-convert-{uuid.uuid4().hex[:8]}"
    test_email = f"convert-test-{uuid.uuid4().hex[:8]}@test.com"
    
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
    
    print(f"\n2️⃣ Creating test cart via API...")
    print(f"   cart_id: {cart_id}")
    print(f"   email: {test_email}")
    
    response = requests.post(f"{BASE_URL}/cart/track", json=payload)
    if response.status_code != 200:
        print(f"❌ Failed to create cart: {response.status_code} - {response.text}")
        return False
    
    print(f"✅ Cart created successfully: {response.json()}")
    
    # Step 3: Get a real product from the database to create a valid order
    print(f"\n3️⃣ Fetching a real product from database...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    product = await db.products.find_one({"active": True}, {"_id": 0})
    if not product:
        print(f"❌ No active products found in database")
        client.close()
        return False
    
    print(f"✅ Found product: {product.get('name')} (id: {product.get('id')})")
    
    # Step 4: Create an order with the same email (transfer payment)
    print(f"\n4️⃣ Creating order with email {test_email}...")
    
    order_payload = {
        "email": test_email,
        "items": [
            {
                "product_id": product["id"],
                "sku": product.get("sku", ""),
                "name": product["name"],
                "variation_name": None,
                "unit_price": product["price_retail"],
                "quantity": 1,
                "image_url": product.get("image_url", "")
            }
        ],
        "shipping_address": {
            "full_name": "Test Conversion User",
            "phone": "123456789",
            "street": "Test Street 123",
            "city": "Madrid",
            "province": "Madrid",
            "postal_code": "28001",
            "country": "España",
            "notes": "Test order for conversion flow"
        },
        "customer_type": "retail",
        "payment_method": "transfer",
        "delivery_method": "shipping",
        "coupon_code": None,
        "acquisition": {}
    }
    
    response = requests.post(f"{BASE_URL}/orders", json=order_payload)
    if response.status_code != 200:
        print(f"❌ Failed to create order: {response.status_code} - {response.text}")
        client.close()
        return False
    
    order = response.json()
    order_id = order["id"]
    order_number = order["order_number"]
    print(f"✅ Order created successfully: {order_number} (id: {order_id})")
    
    # Step 5: Verify the cart status is 'converted'
    print(f"\n5️⃣ Verifying cart status after order creation...")
    
    # Wait a moment for the conversion to process
    await asyncio.sleep(1)
    
    cart_doc = await db.abandoned_carts.find_one({"cart_id": cart_id}, {"_id": 0})
    
    if not cart_doc:
        print(f"❌ Cart not found after order creation")
        # Cleanup order
        await db.orders.delete_one({"id": order_id})
        await db.buyers.delete_one({"email": test_email.lower()})
        client.close()
        return False
    
    print(f"   Cart status: {cart_doc.get('status')}")
    print(f"   converted_order: {cart_doc.get('converted_order')}")
    print(f"   converted_at: {cart_doc.get('converted_at')}")
    
    success = True
    
    if cart_doc.get('status') != 'converted':
        print(f"❌ FAILED: Expected status='converted', got '{cart_doc.get('status')}'")
        success = False
    else:
        print(f"✅ Status correctly set to 'converted'")
    
    if cart_doc.get('converted_order') != order_number:
        print(f"❌ FAILED: Expected converted_order='{order_number}', got '{cart_doc.get('converted_order')}'")
        success = False
    else:
        print(f"✅ converted_order correctly set to '{order_number}'")
    
    if not cart_doc.get('converted_at'):
        print(f"❌ FAILED: converted_at is not set")
        success = False
    else:
        print(f"✅ converted_at is set: {cart_doc.get('converted_at')}")
    
    # Step 6: Cleanup
    print(f"\n6️⃣ Cleaning up test data...")
    
    # Delete test order
    delete_result = await db.orders.delete_one({"id": order_id})
    if delete_result.deleted_count > 0:
        print(f"✅ Test order deleted from MongoDB")
    else:
        print(f"⚠️ Order was not deleted")
    
    # Delete buyer entry
    delete_result = await db.buyers.delete_one({"email": test_email.lower()})
    if delete_result.deleted_count > 0:
        print(f"✅ Test buyer entry deleted from MongoDB")
    else:
        print(f"⚠️ Buyer entry was not found")
    
    # Delete test cart
    delete_result = await db.abandoned_carts.delete_one({"cart_id": cart_id})
    if delete_result.deleted_count > 0:
        print(f"✅ Test cart deleted from MongoDB")
    else:
        print(f"⚠️ Cart was not deleted")
    
    client.close()
    
    print("\n" + "="*60)
    if success:
        print("✅ CONVERSION FLOW TEST PASSED")
    else:
        print("❌ CONVERSION FLOW TEST FAILED")
    print("="*60)
    
    return success

if __name__ == "__main__":
    result = asyncio.run(test_conversion_flow())
    sys.exit(0 if result else 1)
