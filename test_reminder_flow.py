"""
Test the reminder flow by:
1. Creating a cart via API
2. Manipulating MongoDB to set updated_at to 5 hours ago
3. Calling process_abandoned_carts()
4. Verifying the cart status is 'reminded' and reminder_sent_at is set
"""
import sys
import os
import uuid
import requests
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Add backend to path
sys.path.insert(0, '/app/backend')

BASE_URL = "https://eco-andes-test.preview.emergentagent.com/api"
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

async def test_reminder_flow():
    print("="*60)
    print("TESTING REMINDER FLOW")
    print("="*60)
    
    # Step 1: Create a test cart via API
    cart_id = f"test-reminder-{uuid.uuid4().hex[:8]}"
    test_email = f"reminder-test-{uuid.uuid4().hex[:8]}@test.com"
    
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
    
    print(f"\n1️⃣ Creating test cart via API...")
    print(f"   cart_id: {cart_id}")
    print(f"   email: {test_email}")
    
    response = requests.post(f"{BASE_URL}/cart/track", json=payload)
    if response.status_code != 200:
        print(f"❌ Failed to create cart: {response.status_code} - {response.text}")
        return False
    
    print(f"✅ Cart created successfully: {response.json()}")
    
    # Step 2: Connect to MongoDB and update the cart's updated_at to 5 hours ago
    print(f"\n2️⃣ Connecting to MongoDB and updating cart timestamp...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    five_hours_ago = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    
    result = await db.abandoned_carts.update_one(
        {"cart_id": cart_id},
        {"$set": {"updated_at": five_hours_ago}}
    )
    
    if result.matched_count == 0:
        print(f"❌ Cart not found in MongoDB")
        client.close()
        return False
    
    print(f"✅ Cart timestamp updated to 5 hours ago: {five_hours_ago}")
    
    # Verify the update
    cart_doc = await db.abandoned_carts.find_one({"cart_id": cart_id}, {"_id": 0})
    print(f"   Cart document: status={cart_doc.get('status')}, updated_at={cart_doc.get('updated_at')}")
    
    # Step 3: Call process_abandoned_carts()
    print(f"\n3️⃣ Calling process_abandoned_carts()...")
    
    from routes.carts import process_abandoned_carts
    
    sent_count = await process_abandoned_carts()
    print(f"✅ process_abandoned_carts() completed, sent {sent_count} reminder(s)")
    
    # Step 4: Verify the cart status
    print(f"\n4️⃣ Verifying cart status after reminder...")
    
    cart_doc = await db.abandoned_carts.find_one({"cart_id": cart_id}, {"_id": 0})
    
    if not cart_doc:
        print(f"❌ Cart not found after reminder processing")
        client.close()
        return False
    
    print(f"   Cart status: {cart_doc.get('status')}")
    print(f"   reminder_sent_at: {cart_doc.get('reminder_sent_at')}")
    
    success = True
    
    if cart_doc.get('status') != 'reminded':
        print(f"❌ FAILED: Expected status='reminded', got '{cart_doc.get('status')}'")
        success = False
    else:
        print(f"✅ Status correctly set to 'reminded'")
    
    if not cart_doc.get('reminder_sent_at'):
        print(f"❌ FAILED: reminder_sent_at is not set")
        success = False
    else:
        print(f"✅ reminder_sent_at is set: {cart_doc.get('reminder_sent_at')}")
    
    # Step 5: Cleanup
    print(f"\n5️⃣ Cleaning up test data...")
    
    delete_result = await db.abandoned_carts.delete_one({"cart_id": cart_id})
    if delete_result.deleted_count > 0:
        print(f"✅ Test cart deleted from MongoDB")
    else:
        print(f"⚠️ Cart was not deleted (may have been already removed)")
    
    client.close()
    
    print("\n" + "="*60)
    if success:
        print("✅ REMINDER FLOW TEST PASSED")
    else:
        print("❌ REMINDER FLOW TEST FAILED")
    print("="*60)
    
    return success

if __name__ == "__main__":
    result = asyncio.run(test_reminder_flow())
    sys.exit(0 if result else 1)
