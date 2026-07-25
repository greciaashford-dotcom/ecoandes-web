"""Backend API tests for EcoAndes NEW FEATURES: enriched product pages + admin management."""
import requests
import sys
from typing import Dict, List, Optional

BASE_URL = "https://eco-andes-test.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@ecoandes.com"
ADMIN_PASSWORD = "Admin123!"

# Expected best-seller products
EXPECTED_BEST_SELLERS = ["Cacao Nibs", "Quinoa Real Tricolor", "Maca Negra", "Cúrcuma", "Canela"]


class TestRunner:
    def __init__(self):
        self.token: Optional[str] = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures: List[Dict] = []

    def test(self, name: str, method: str, endpoint: str, expected_status: int, 
             data: Optional[dict] = None, params: Optional[dict] = None, 
             auth: bool = False, validate_fn=None, files=None) -> tuple:
        """Run a single test."""
        url = f"{BASE_URL}/{endpoint}"
        headers = {}
        if method != "UPLOAD":
            headers["Content-Type"] = "application/json"
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == "PATCH":
                response = requests.patch(url, json=data, headers=headers, timeout=15)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=15)
            elif method == "UPLOAD":
                response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
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
            print(f"❌ FAILED - Error: {str(e)}")
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
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failures:
            print("\n❌ FAILED TESTS:")
            for i, failure in enumerate(self.failures, 1):
                print(f"\n{i}. {failure['test']}")
                print(f"   Endpoint: {failure.get('endpoint', 'N/A')}")
                if 'expected' in failure:
                    print(f"   Expected: {failure['expected']}, Got: {failure['actual']}")
                if 'reason' in failure:
                    print(f"   Reason: {failure['reason']}")
        print("="*60)


def main():
    runner = TestRunner()

    # Test 1: Admin login
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
    if success:
        if "token" in response:
            runner.token = response["token"]
            print(f"   ✓ Token obtained: {runner.token[:20]}...")
        elif "access_token" in response:
            runner.token = response["access_token"]
            print(f"   ✓ Token obtained: {runner.token[:20]}...")
        else:
            print(f"   ⚠️  WARNING: No token in response: {list(response.keys())}")
    else:
        print("⚠️  WARNING: Admin login failed, admin-only tests will be skipped")

    # Test 2: Best-seller products
    print("\n" + "="*60)
    print("⭐ BEST-SELLER PRODUCTS")
    print("="*60)
    
    def validate_best_sellers(data):
        """Validate best-seller products."""
        if not isinstance(data, list):
            print(f"   ⚠️  Response is not a list")
            return False
        
        print(f"   ✓ {len(data)} best-seller products returned")
        
        # Check if we have the expected products
        product_names = [p.get('name', '') for p in data]
        print(f"   Products: {', '.join(product_names[:10])}")
        
        # Verify all have best_seller flag
        all_best_sellers = all(p.get('best_seller', False) for p in data)
        if not all_best_sellers:
            print(f"   ⚠️  Not all products have best_seller=true")
            return False
        
        print(f"   ✓ All products have best_seller=true")
        return True
    
    runner.test(
        "GET /api/products?best_seller=true",
        "GET",
        "products",
        200,
        params={"best_seller": True},
        validate_fn=validate_best_sellers
    )

    # Test 3: Product detail with new fields (cacao-nibs-criollo-bio)
    print("\n" + "="*60)
    print("📦 PRODUCT DETAIL (NEW FIELDS)")
    print("="*60)
    
    def validate_product_detail(data):
        """Validate product detail has new fields and doesn't leak translations."""
        if not isinstance(data, dict):
            print(f"   ⚠️  Response is not a dict")
            return False
        
        # Check translations field is NOT leaked
        if "translations" in data:
            print(f"   ⚠️  SECURITY ISSUE: 'translations' field leaked!")
            return False
        
        print(f"   ✓ 'translations' field NOT leaked")
        
        # Check new fields
        new_fields = ["highlights", "badges", "description_blocks", "gallery", "web_rating", "web_reviews", "best_seller"]
        missing = [f for f in new_fields if f not in data]
        if missing:
            print(f"   ⚠️  Missing new fields: {missing}")
            return False
        
        print(f"   ✓ All new fields present: {', '.join(new_fields)}")
        print(f"   Product: {data.get('name', 'N/A')}")
        print(f"   Highlights: {data.get('highlights', '')[:60]}...")
        print(f"   Badges count: {len(data.get('badges', []))}")
        print(f"   Gallery count: {len(data.get('gallery', []))}")
        print(f"   Web rating: {data.get('web_rating', 0)}")
        print(f"   Web reviews: {data.get('web_reviews', 0)}")
        print(f"   Best seller: {data.get('best_seller', False)}")
        
        return True
    
    runner.test(
        "GET /api/products/slug/cacao-nibs-criollo-bio",
        "GET",
        "products/slug/cacao-nibs-criollo-bio",
        200,
        validate_fn=validate_product_detail
    )

    # Test 4: Products by IDs (for wishlist/compare)
    print("\n" + "="*60)
    print("🔗 PRODUCTS BY IDS (WISHLIST/COMPARE)")
    print("="*60)
    
    # First get some product IDs
    success, products = runner.test(
        "Get products for IDs",
        "GET",
        "products",
        200,
        params={"limit": 5}
    )
    
    if success and products:
        product_ids = [p['id'] for p in products[:3]]
        
        def validate_by_ids(data):
            if not isinstance(data, list):
                print(f"   ⚠️  Response is not a list")
                return False
            print(f"   ✓ {len(data)} products hydrated")
            return len(data) == len(product_ids)
        
        runner.test(
            "POST /api/products/by-ids",
            "POST",
            "products/by-ids",
            200,
            data={"ids": product_ids},
            validate_fn=validate_by_ids
        )

    # Test 5: Newsletter subscription
    print("\n" + "="*60)
    print("📧 NEWSLETTER SUBSCRIPTION")
    print("="*60)
    
    import time
    test_email = f"test_{int(time.time())}@example.com"
    
    def validate_newsletter(data):
        if not isinstance(data, dict):
            return False
        if "ok" not in data:
            print(f"   ⚠️  Missing 'ok' field")
            return False
        print(f"   ✓ Newsletter subscription: ok={data.get('ok')}, already={data.get('already', False)}")
        return data.get('ok') == True
    
    runner.test(
        "POST /api/newsletter/subscribe (new email)",
        "POST",
        "newsletter/subscribe",
        200,
        data={"email": test_email},
        validate_fn=validate_newsletter
    )
    
    # Test duplicate
    def validate_duplicate(data):
        if not isinstance(data, dict):
            return False
        if data.get('already') != True:
            print(f"   ⚠️  Expected 'already=true' for duplicate email")
            return False
        print(f"   ✓ Duplicate email handled correctly: already={data.get('already')}")
        return True
    
    runner.test(
        "POST /api/newsletter/subscribe (duplicate)",
        "POST",
        "newsletter/subscribe",
        200,
        data={"email": test_email},
        validate_fn=validate_duplicate
    )

    # Test 6: Wishlist/Compare (auth required)
    if runner.token:
        print("\n" + "="*60)
        print("❤️  WISHLIST (AUTH REQUIRED)")
        print("="*60)
        
        # Get wishlist
        success, wishlist_data = runner.test(
            "GET /api/me/wishlist",
            "GET",
            "me/wishlist",
            200,
            auth=True
        )
        
        if success and products:
            product_id = products[0]['id']
            
            # Add to wishlist
            runner.test(
                "POST /api/me/wishlist/{id}",
                "POST",
                f"me/wishlist/{product_id}",
                200,
                auth=True
            )
            
            # Get wishlist again
            def validate_wishlist(data):
                if not isinstance(data, dict):
                    return False
                if "product_ids" not in data or "items" not in data:
                    print(f"   ⚠️  Missing 'product_ids' or 'items'")
                    return False
                print(f"   ✓ Wishlist: {len(data.get('product_ids', []))} IDs, {len(data.get('items', []))} items hydrated")
                return True
            
            runner.test(
                "GET /api/me/wishlist (after add)",
                "GET",
                "me/wishlist",
                200,
                auth=True,
                validate_fn=validate_wishlist
            )
            
            # Remove from wishlist
            runner.test(
                "DELETE /api/me/wishlist/{id}",
                "DELETE",
                f"me/wishlist/{product_id}",
                200,
                auth=True
            )
        
        print("\n" + "="*60)
        print("⚖️  COMPARE (AUTH REQUIRED)")
        print("="*60)
        
        # Get compare
        success, compare_data = runner.test(
            "GET /api/me/compare",
            "GET",
            "me/compare",
            200,
            auth=True
        )
        
        if success and products:
            product_id = products[0]['id']
            
            # Add to compare
            runner.test(
                "POST /api/me/compare/{id}",
                "POST",
                f"me/compare/{product_id}",
                200,
                auth=True
            )
            
            # Get compare again
            def validate_compare(data):
                if not isinstance(data, dict):
                    return False
                if "product_ids" not in data or "items" not in data:
                    print(f"   ⚠️  Missing 'product_ids' or 'items'")
                    return False
                print(f"   ✓ Compare: {len(data.get('product_ids', []))} IDs, {len(data.get('items', []))} items hydrated")
                return True
            
            runner.test(
                "GET /api/me/compare (after add)",
                "GET",
                "me/compare",
                200,
                auth=True,
                validate_fn=validate_compare
            )
            
            # Remove from compare
            runner.test(
                "DELETE /api/me/compare/{id}",
                "DELETE",
                f"me/compare/{product_id}",
                200,
                auth=True
            )

    # Test 7: Admin upload (image)
    if runner.token:
        print("\n" + "="*60)
        print("📤 ADMIN UPLOAD (IMAGE)")
        print("="*60)
        
        # Create a small test image (1x1 PNG)
        import io
        test_image = io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
        test_image.name = 'test.png'
        
        def validate_upload(data):
            if not isinstance(data, dict):
                return False
            if "url" not in data:
                print(f"   ⚠️  Missing 'url' field")
                return False
            if not data['url'].startswith('/api/files/'):
                print(f"   ⚠️  URL doesn't start with /api/files/: {data['url']}")
                return False
            print(f"   ✓ Upload successful: {data['url']}")
            return True
        
        success, upload_data = runner.test(
            "POST /api/admin/uploads (image)",
            "UPLOAD",
            "admin/uploads",
            200,
            files={'file': ('test.png', test_image, 'image/png')},
            data={'kind': 'image'},
            auth=True,
            validate_fn=validate_upload
        )
        
        # Test serving the uploaded file
        if success and upload_data.get('url'):
            file_path = upload_data['url'].replace('/api/files/', '')
            runner.test(
                "GET /api/files/{path} (serve uploaded image)",
                "GET",
                f"files/{file_path}",
                200
            )
        
        # Test PDF upload rejection with non-PDF
        print("\n" + "="*60)
        print("📤 ADMIN UPLOAD (PDF VALIDATION)")
        print("="*60)
        
        test_image.seek(0)
        runner.test(
            "POST /api/admin/uploads (reject non-PDF)",
            "UPLOAD",
            "admin/uploads",
            400,
            files={'file': ('test.png', test_image, 'image/png')},
            data={'kind': 'pdf'},
            auth=True
        )

    # Test 7b: File management - list, filter, delete
    if runner.token:
        print("\n" + "="*60)
        print("📁 FILE MANAGEMENT - LIST & FILTER")
        print("="*60)
        
        # Get all files
        def validate_files_list(data):
            if not isinstance(data, dict):
                return False
            if "files" not in data or "total" not in data:
                print(f"   ⚠️  Missing 'files' or 'total' field")
                return False
            files = data.get("files", [])
            total = data.get("total", 0)
            print(f"   ✓ Files list: {total} total files")
            if len(files) > 0:
                first_file = files[0]
                print(f"   ✓ First file: {first_file.get('original_filename', 'N/A')}")
                print(f"   ✓ URL field: {first_file.get('url', 'N/A')}")
                if "url" not in first_file:
                    print(f"   ⚠️  Missing 'url' field in file object")
                    return False
            return True
        
        success, files_data = runner.test(
            "GET /api/admin/files (list all)",
            "GET",
            "admin/files",
            200,
            auth=True,
            validate_fn=validate_files_list
        )
        
        # Test filter by kind=image
        def validate_image_filter(data):
            if not isinstance(data, dict):
                return False
            files = data.get("files", [])
            print(f"   ✓ Image files: {len(files)}")
            # Check all are images
            for f in files:
                if not (f.get("content_type", "").startswith("image/")):
                    print(f"   ⚠️  Non-image file in image filter: {f.get('content_type')}")
                    return False
            print(f"   ✓ All files are images")
            return True
        
        runner.test(
            "GET /api/admin/files?kind=image",
            "GET",
            "admin/files",
            200,
            params={"kind": "image"},
            auth=True,
            validate_fn=validate_image_filter
        )
        
        # Test filter by kind=pdf
        def validate_pdf_filter(data):
            if not isinstance(data, dict):
                return False
            files = data.get("files", [])
            print(f"   ✓ PDF files: {len(files)}")
            # Check all are PDFs
            for f in files:
                if f.get("content_type") != "application/pdf":
                    print(f"   ⚠️  Non-PDF file in PDF filter: {f.get('content_type')}")
                    return False
            if len(files) > 0:
                print(f"   ✓ All files are PDFs")
            return True
        
        runner.test(
            "GET /api/admin/files?kind=pdf",
            "GET",
            "admin/files",
            200,
            params={"kind": "pdf"},
            auth=True,
            validate_fn=validate_pdf_filter
        )
        
        # Test auth protection - no token should return 401
        print("\n" + "="*60)
        print("🔒 FILE MANAGEMENT - AUTH PROTECTION")
        print("="*60)
        
        saved_token = runner.token
        runner.token = None
        
        runner.test(
            "GET /api/admin/files (no auth - should fail)",
            "GET",
            "admin/files",
            401
        )
        
        runner.token = saved_token
        
        # Test soft-delete
        print("\n" + "="*60)
        print("🗑️  FILE MANAGEMENT - SOFT DELETE")
        print("="*60)
        
        if success and files_data and files_data.get("files"):
            # Upload a test file specifically for deletion
            test_image_delete = io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
            test_image_delete.name = 'test_delete.png'
            
            success_upload, upload_delete_data = runner.test(
                "POST /api/admin/uploads (for delete test)",
                "UPLOAD",
                "admin/uploads",
                200,
                files={'file': ('test_delete.png', test_image_delete, 'image/png')},
                data={'kind': 'image'},
                auth=True
            )
            
            if success_upload:
                # Get the file ID by listing files again
                success_list, files_list_data = runner.test(
                    "GET /api/admin/files (to get file ID)",
                    "GET",
                    "admin/files",
                    200,
                    auth=True
                )
                
                if success_list and files_list_data.get("files"):
                    # Find the file we just uploaded
                    file_to_delete = None
                    for f in files_list_data["files"]:
                        if f.get("original_filename") == "test_delete.png":
                            file_to_delete = f
                            break
                    
                    if file_to_delete:
                        file_id = file_to_delete.get("id")
                        storage_path = file_to_delete.get("storage_path")
                        
                        # Delete the file
                        def validate_delete(data):
                            if not isinstance(data, dict):
                                return False
                            if data.get('ok') != True:
                                print(f"   ⚠️  Expected ok=true")
                                return False
                            print(f"   ✓ File soft-deleted: ok={data.get('ok')}")
                            return True
                        
                        success_delete, _ = runner.test(
                            f"DELETE /api/admin/files/{file_id}",
                            "DELETE",
                            f"admin/files/{file_id}",
                            200,
                            auth=True,
                            validate_fn=validate_delete
                        )
                        
                        if success_delete:
                            # Verify file is not in list anymore
                            def validate_file_removed(data):
                                if not isinstance(data, dict):
                                    return False
                                files = data.get("files", [])
                                for f in files:
                                    if f.get("id") == file_id:
                                        print(f"   ⚠️  Deleted file still in list!")
                                        return False
                                print(f"   ✓ Deleted file removed from list")
                                return True
                            
                            runner.test(
                                "GET /api/admin/files (verify file removed from list)",
                                "GET",
                                "admin/files",
                                200,
                                auth=True,
                                validate_fn=validate_file_removed
                            )
                            
                            # Verify public serving returns 404
                            runner.test(
                                f"GET /api/files/{storage_path} (should return 404 after delete)",
                                "GET",
                                f"files/{storage_path}",
                                404
                            )
        
        # Test upload validation - reject non-image for kind=image
        print("\n" + "="*60)
        print("📤 UPLOAD VALIDATION - REJECT WRONG FILE TYPES")
        print("="*60)
        
        # Create a fake PDF (just text)
        fake_pdf = io.BytesIO(b'This is not a real PDF')
        fake_pdf.name = 'fake.pdf'
        
        runner.test(
            "POST /api/admin/uploads (reject PDF as image)",
            "UPLOAD",
            "admin/uploads",
            400,
            files={'file': ('fake.pdf', fake_pdf, 'application/pdf')},
            data={'kind': 'image'},
            auth=True
        )
        
        # Create a fake image (just text)
        fake_image = io.BytesIO(b'This is not a real image')
        fake_image.name = 'fake.jpg'
        
        runner.test(
            "POST /api/admin/uploads (reject non-PDF as PDF)",
            "UPLOAD",
            "admin/uploads",
            400,
            files={'file': ('fake.jpg', fake_image, 'image/jpeg')},
            data={'kind': 'pdf'},
            auth=True
        )

    # Test 8: Admin stock update
    if runner.token and products:
        print("\n" + "="*60)
        print("📦 ADMIN STOCK UPDATE")
        print("="*60)
        
        product_id = products[0]['id']
        
        def validate_stock_update(data):
            if not isinstance(data, dict):
                return False
            if "stock" not in data:
                print(f"   ⚠️  Missing 'stock' field")
                return False
            print(f"   ✓ Stock updated: {data.get('stock')}")
            return True
        
        runner.test(
            "PATCH /api/products/{id}/stock",
            "PATCH",
            f"products/{product_id}/stock",
            200,
            data={"stock": 100},
            auth=True,
            validate_fn=validate_stock_update
        )

    # Test 9: Admin product update
    if runner.token and products:
        print("\n" + "="*60)
        print("✏️  ADMIN PRODUCT UPDATE")
        print("="*60)
        
        product_id = products[0]['id']
        
        def validate_product_update(data):
            if not isinstance(data, dict):
                return False
            print(f"   ✓ Product updated: {data.get('name', 'N/A')}")
            return True
        
        runner.test(
            "PATCH /api/products/{id} (update description_blocks)",
            "PATCH",
            f"products/{product_id}",
            200,
            data={
                "description_blocks": {
                    "ingredients": "Test ingredients",
                    "origin": "Test origin"
                },
                "best_seller": True
            },
            auth=True,
            validate_fn=validate_product_update
        )

    # Test 10: Multilingual product detail
    print("\n" + "="*60)
    print("🌍 MULTILINGUAL PRODUCT DETAIL")
    print("="*60)
    
    for lang in ["en", "es", "fr", "zh"]:
        def validate_multilingual(data):
            if not isinstance(data, dict):
                return False
            if "translations" in data:
                print(f"   ⚠️  'translations' field leaked!")
                return False
            print(f"   ✓ Product ({lang}): {data.get('name', 'N/A')[:50]}")
            print(f"   ✓ Highlights: {data.get('highlights', '')[:50]}...")
            return True
        
        runner.test(
            f"GET /api/products/slug/cacao-nibs-criollo-bio?lang={lang}",
            "GET",
            "products/slug/cacao-nibs-criollo-bio",
            200,
            params={"lang": lang},
            validate_fn=validate_multilingual
        )

    # Test 11: Hero carousel - public endpoint
    print("\n" + "="*60)
    print("🎨 HERO CAROUSEL - PUBLIC")
    print("="*60)
    
    def validate_hero_public(data):
        if not isinstance(data, dict):
            print(f"   ⚠️  Response is not a dict")
            return False
        if "slides" not in data or "b2b" not in data:
            print(f"   ⚠️  Missing 'slides' or 'b2b' field")
            return False
        slides = data.get("slides", [])
        if not isinstance(slides, list):
            print(f"   ⚠️  'slides' is not a list")
            return False
        print(f"   ✓ Hero has {len(slides)} active slides")
        if len(slides) > 0:
            first_slide = slides[0]
            print(f"   ✓ First slide title: {first_slide.get('h1', 'N/A')[:60]}")
            print(f"   ✓ First slide image: {first_slide.get('image', 'N/A')}")
            # Check no translations leaked
            if "translations" in first_slide:
                print(f"   ⚠️  SECURITY: 'translations' field leaked in slide!")
                return False
        b2b = data.get("b2b", {})
        print(f"   ✓ B2B button: {b2b.get('label', 'N/A')}")
        return True
    
    runner.test(
        "GET /api/hero (Spanish)",
        "GET",
        "hero",
        200,
        params={"lang": "es"},
        validate_fn=validate_hero_public
    )
    
    # Test hero in different languages
    for lang in ["en", "fr"]:
        def validate_hero_lang(data):
            if not isinstance(data, dict):
                return False
            slides = data.get("slides", [])
            if len(slides) > 0:
                first_slide = slides[0]
                title = first_slide.get('h1', '')
                print(f"   ✓ First slide title ({lang}): {title[:60]}")
                # For EN, check if it's actually English (not Spanish)
                if lang == "en" and "Nibs" in title:
                    # Should contain English words
                    print(f"   ✓ Title appears to be in English")
            b2b_label = data.get("b2b", {}).get("label", "")
            print(f"   ✓ B2B button ({lang}): {b2b_label}")
            return True
        
        runner.test(
            f"GET /api/hero?lang={lang}",
            "GET",
            "hero",
            200,
            params={"lang": lang},
            validate_fn=validate_hero_lang
        )

    # Test 12: Hero carousel - admin endpoints
    if runner.token:
        print("\n" + "="*60)
        print("🎨 HERO CAROUSEL - ADMIN")
        print("="*60)
        
        # Get admin hero config
        def validate_admin_hero(data):
            if not isinstance(data, dict):
                print(f"   ⚠️  Response is not a dict")
                return False
            if "slides" not in data:
                print(f"   ⚠️  Missing 'slides' field")
                return False
            slides = data.get("slides", [])
            print(f"   ✓ Admin hero has {len(slides)} slides (including inactive)")
            if len(slides) > 0:
                first_slide = slides[0]
                print(f"   ✓ First slide ID: {first_slide.get('id', 'N/A')}")
                print(f"   ✓ First slide title: {first_slide.get('h1', 'N/A')[:60]}")
                print(f"   ✓ First slide active: {first_slide.get('active', False)}")
                # Admin endpoint SHOULD have translations
                if "translations" in first_slide:
                    print(f"   ✓ Translations present (admin view)")
            return True
        
        success, admin_hero_data = runner.test(
            "GET /api/admin/hero",
            "GET",
            "admin/hero",
            200,
            auth=True,
            validate_fn=validate_admin_hero
        )
        
        # Test PUT /api/admin/hero (update hero config)
        if success and admin_hero_data:
            slides = admin_hero_data.get("slides", [])
            b2b = admin_hero_data.get("b2b", {})
            
            # Modify first slide title slightly
            if len(slides) > 0:
                slides[0]["h1"] = slides[0].get("h1", "") + " [TEST]"
            
            def validate_hero_save(data):
                if not isinstance(data, dict):
                    return False
                if "ok" not in data:
                    print(f"   ⚠️  Missing 'ok' field")
                    return False
                print(f"   ✓ Hero saved: ok={data.get('ok')}, slides={data.get('slides')}, translating={data.get('translating')}")
                return data.get('ok') == True
            
            runner.test(
                "PUT /api/admin/hero",
                "PUT",
                "admin/hero",
                200,
                data={
                    "slides": slides,
                    "b2b": b2b,
                    "autotranslate": False  # Don't trigger translation in test
                },
                auth=True,
                validate_fn=validate_hero_save
            )
        
        # Test POST /api/admin/hero/translate
        def validate_translate_trigger(data):
            if not isinstance(data, dict):
                return False
            if "ok" not in data or "started" not in data:
                print(f"   ⚠️  Missing 'ok' or 'started' field")
                return False
            print(f"   ✓ Translation triggered: ok={data.get('ok')}, started={data.get('started')}")
            return data.get('ok') == True and data.get('started') == True
        
        runner.test(
            "POST /api/admin/hero/translate",
            "POST",
            "admin/hero/translate",
            200,
            auth=True,
            validate_fn=validate_translate_trigger
        )

    # Test 13: Search relevance - 'maca' should return Maca products, NOT macarrones
    print("\n" + "="*60)
    print("🔍 SEARCH RELEVANCE (MACA)")
    print("="*60)
    
    def validate_maca_search(data):
        if not isinstance(data, list):
            print(f"   ⚠️  Response is not a list")
            return False
        if len(data) == 0:
            print(f"   ⚠️  No results for 'maca'")
            return False
        print(f"   ✓ {len(data)} results for 'maca'")
        # Check first result contains 'maca' as whole word, not 'macarrones'
        first_name = data[0].get('name', '').lower()
        print(f"   First result: {data[0].get('name', 'N/A')}")
        # Should match 'maca' but NOT 'macarrones'
        if 'macarrones' in first_name or 'macarrón' in first_name:
            print(f"   ⚠️  FAILED: First result is macarrones, not maca!")
            return False
        if 'maca' not in first_name:
            print(f"   ⚠️  First result doesn't contain 'maca'")
            return False
        print(f"   ✓ Search relevance correct: 'maca' returns Maca products first")
        return True
    
    runner.test(
        "GET /api/products?search=maca (relevance check)",
        "GET",
        "products",
        200,
        params={"search": "maca"},
        validate_fn=validate_maca_search
    )

    # Test 14: ECOBONUS coupon validation
    print("\n" + "="*60)
    print("🎟️  ECOBONUS COUPON VALIDATION")
    print("="*60)
    
    # Test 14a: Valid coupon with >=60€ subtotal for first-time buyer
    def validate_coupon_valid(data):
        if not isinstance(data, dict):
            return False
        if not data.get('valid'):
            print(f"   ⚠️  Coupon should be valid for >=60€ first-time buyer")
            return False
        if data.get('discount') != 5.0:
            print(f"   ⚠️  Discount should be 5.0, got {data.get('discount')}")
            return False
        print(f"   ✓ Coupon valid: discount={data.get('discount')}€, message={data.get('message')}")
        return True
    
    test_email_new = f"newbuyer_{int(time.time())}@example.com"
    runner.test(
        "POST /api/orders/validate-coupon (valid: >=60€, first-time)",
        "POST",
        "orders/validate-coupon",
        200,
        data={"code": "ECOBONUS", "email": test_email_new, "subtotal": 65.0},
        validate_fn=validate_coupon_valid
    )
    
    # Test 14b: Invalid coupon with <60€ subtotal
    def validate_coupon_min_subtotal(data):
        if not isinstance(data, dict):
            return False
        if data.get('valid'):
            print(f"   ⚠️  Coupon should be invalid for <60€")
            return False
        print(f"   ✓ Coupon rejected for <60€: message={data.get('message')}")
        return True
    
    runner.test(
        "POST /api/orders/validate-coupon (invalid: <60€)",
        "POST",
        "orders/validate-coupon",
        200,
        data={"code": "ECOBONUS", "email": test_email_new, "subtotal": 50.0},
        validate_fn=validate_coupon_min_subtotal
    )
    
    # Test 14c: Invalid coupon code
    def validate_coupon_invalid_code(data):
        if not isinstance(data, dict):
            return False
        if data.get('valid'):
            print(f"   ⚠️  Invalid coupon code should be rejected")
            return False
        print(f"   ✓ Invalid coupon code rejected: message={data.get('message')}")
        return True
    
    runner.test(
        "POST /api/orders/validate-coupon (invalid code)",
        "POST",
        "orders/validate-coupon",
        200,
        data={"code": "INVALID", "email": test_email_new, "subtotal": 65.0},
        validate_fn=validate_coupon_invalid_code
    )

    # Test 15: Free shipping threshold (50€)
    print("\n" + "="*60)
    print("🚚 FREE SHIPPING THRESHOLD (50€)")
    print("="*60)
    
    # Test 15a: Below threshold
    def validate_shipping_below(data):
        if not isinstance(data, dict):
            return False
        if data.get('free_shipping'):
            print(f"   ⚠️  Should NOT have free shipping for <50€")
            return False
        if data.get('shipping_cost') <= 0:
            print(f"   ⚠️  Shipping cost should be >0 for <50€")
            return False
        print(f"   ✓ Shipping cost: {data.get('shipping_cost')}€, remaining: {data.get('remaining_for_free_shipping')}€")
        return True
    
    runner.test(
        "POST /api/orders/shipping-quote (below 50€)",
        "POST",
        "orders/shipping-quote",
        200,
        data={"subtotal": 40.0, "customer_type": "retail"},
        validate_fn=validate_shipping_below
    )
    
    # Test 15b: At/above threshold
    def validate_shipping_free(data):
        if not isinstance(data, dict):
            return False
        if not data.get('free_shipping'):
            print(f"   ⚠️  Should have free shipping for >=50€")
            return False
        if data.get('shipping_cost') != 0:
            print(f"   ⚠️  Shipping cost should be 0 for >=50€, got {data.get('shipping_cost')}")
            return False
        print(f"   ✓ Free shipping applied: shipping_cost={data.get('shipping_cost')}€")
        return True
    
    runner.test(
        "POST /api/orders/shipping-quote (at 50€)",
        "POST",
        "orders/shipping-quote",
        200,
        data={"subtotal": 50.0, "customer_type": "retail"},
        validate_fn=validate_shipping_free
    )

    # Test 16: Professional registration with business_type
    print("\n" + "="*60)
    print("🏢 PROFESSIONAL REGISTRATION (business_type)")
    print("="*60)
    
    test_pro_email = f"pro_{int(time.time())}@example.com"
    
    def validate_pro_registration(data):
        if not isinstance(data, dict):
            return False
        if "business_type" not in data:
            print(f"   ⚠️  Missing 'business_type' field in response")
            return False
        if data.get('business_type') != "restaurant":
            print(f"   ⚠️  business_type should be 'restaurant', got {data.get('business_type')}")
            return False
        print(f"   ✓ Professional registered: email={data.get('email')}, business_type={data.get('business_type')}")
        return True
    
    runner.test(
        "POST /api/auth/register (professional with business_type)",
        "POST",
        "auth/register",
        200,
        data={
            "email": test_pro_email,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "Professional",
            "role": "professional",
            "company": "Test Restaurant",
            "tax_id": "B12345678",
            "business_type": "restaurant",
            "phone": "+34600000000"
        },
        validate_fn=validate_pro_registration
    )

    # Test 17: WhatsApp leads - public capture
    print("\n" + "="*60)
    print("💬 WHATSAPP LEADS - PUBLIC CAPTURE")
    print("="*60)
    
    test_phone = f"+34600{int(time.time()) % 1000000}"
    test_name = "Test Lead"
    
    def validate_lead_create(data):
        if not isinstance(data, dict):
            return False
        if "ok" not in data:
            print(f"   ⚠️  Missing 'ok' field")
            return False
        if data.get('ok') != True:
            print(f"   ⚠️  Expected ok=true")
            return False
        print(f"   ✓ Lead created: ok={data.get('ok')}, already={data.get('already', False)}")
        return True
    
    runner.test(
        "POST /api/whatsapp-leads (create new lead)",
        "POST",
        "whatsapp-leads",
        200,
        data={"name": test_name, "phone": test_phone},
        validate_fn=validate_lead_create
    )
    
    # Test duplicate phone (should increment contact_count)
    def validate_lead_duplicate(data):
        if not isinstance(data, dict):
            return False
        if data.get('already') != True:
            print(f"   ⚠️  Expected already=true for duplicate phone")
            return False
        print(f"   ✓ Duplicate phone handled: ok={data.get('ok')}, already={data.get('already')}")
        return True
    
    runner.test(
        "POST /api/whatsapp-leads (duplicate phone - dedupe)",
        "POST",
        "whatsapp-leads",
        200,
        data={"name": "Updated Name", "phone": test_phone},
        validate_fn=validate_lead_duplicate
    )
    
    # Test validation - empty name
    runner.test(
        "POST /api/whatsapp-leads (validation: empty name)",
        "POST",
        "whatsapp-leads",
        422,
        data={"name": "", "phone": test_phone}
    )
    
    # Test validation - invalid phone
    runner.test(
        "POST /api/whatsapp-leads (validation: invalid phone)",
        "POST",
        "whatsapp-leads",
        422,
        data={"name": test_name, "phone": "123"}
    )
    
    # Test 18: WhatsApp leads - admin endpoints
    if runner.token:
        print("\n" + "="*60)
        print("💬 WHATSAPP LEADS - ADMIN")
        print("="*60)
        
        # Get leads list
        def validate_leads_list(data):
            if not isinstance(data, dict):
                return False
            if "leads" not in data or "total" not in data:
                print(f"   ⚠️  Missing 'leads' or 'total' field")
                return False
            leads = data.get("leads", [])
            total = data.get("total", 0)
            print(f"   ✓ Leads list: {total} total leads")
            if len(leads) > 0:
                first_lead = leads[0]
                print(f"   ✓ First lead: {first_lead.get('name', 'N/A')}, {first_lead.get('phone', 'N/A')}")
                print(f"   ✓ Contact count: {first_lead.get('contact_count', 1)}")
            return True
        
        success, leads_data = runner.test(
            "GET /api/admin/whatsapp-leads",
            "GET",
            "admin/whatsapp-leads",
            200,
            auth=True,
            validate_fn=validate_leads_list
        )
        
        # Test Excel export
        def validate_excel_export(data):
            # For blob response, we just check status code
            print(f"   ✓ Excel file downloaded successfully")
            return True
        
        runner.test(
            "GET /api/admin/whatsapp-leads/export (Excel)",
            "GET",
            "admin/whatsapp-leads/export",
            200,
            auth=True
        )
        
        # Test delete lead
        if success and leads_data and leads_data.get("leads"):
            lead_to_delete = leads_data["leads"][0]
            lead_id = lead_to_delete.get("id")
            
            if lead_id:
                def validate_delete(data):
                    if not isinstance(data, dict):
                        return False
                    if data.get('ok') != True:
                        print(f"   ⚠️  Expected ok=true")
                        return False
                    print(f"   ✓ Lead deleted: ok={data.get('ok')}")
                    return True
                
                runner.test(
                    f"DELETE /api/admin/whatsapp-leads/{lead_id}",
                    "DELETE",
                    f"admin/whatsapp-leads/{lead_id}",
                    200,
                    auth=True,
                    validate_fn=validate_delete
                )
    
    # Test 19: WhatsApp leads - auth required
    print("\n" + "="*60)
    print("🔒 WHATSAPP LEADS - AUTH PROTECTION")
    print("="*60)
    
    # Save token temporarily
    saved_token = runner.token
    runner.token = None
    
    runner.test(
        "GET /api/admin/whatsapp-leads (no auth - should fail)",
        "GET",
        "admin/whatsapp-leads",
        401
    )
    
    # Restore token
    runner.token = saved_token

    # Test 20: Catalog sync - product count (174 products from Excel, not 187 from WordPress)
    print("\n" + "="*60)
    print("📊 CATALOG SYNC - PRODUCT COUNT (EXCEL CATALOG)")
    print("="*60)
    
    def validate_product_count(data):
        if not isinstance(data, list):
            print(f"   ⚠️  Response is not a list")
            return False
        count = len(data)
        print(f"   ✓ Total products: {count}")
        if count != 174:
            print(f"   ⚠️  Expected 174 products (Excel catalog), got {count}")
            print(f"   ⚠️  This suggests the old WordPress catalog (187 products) is still in use")
            return False
        print(f"   ✓ Correct product count: 174 (Excel catalog reconciliation successful)")
        return True
    
    runner.test(
        "GET /api/products (verify 174 products from Excel)",
        "GET",
        "products",
        200,
        params={"limit": 200},
        validate_fn=validate_product_count
    )

    # Test 21: Catalog sync - VAT rates
    print("\n" + "="*60)
    print("💶 CATALOG SYNC - VAT RATES (4, 10, 2)")
    print("="*60)
    
    def validate_vat_rates(data):
        if not isinstance(data, list):
            print(f"   ⚠️  Response is not a list")
            return False
        
        # Check all products have vat_rate field
        missing_vat = [p.get('name', 'N/A') for p in data if 'vat_rate' not in p]
        if missing_vat:
            print(f"   ⚠️  {len(missing_vat)} products missing vat_rate field")
            print(f"   ⚠️  Examples: {missing_vat[:5]}")
            return False
        
        print(f"   ✓ All products have vat_rate field")
        
        # Check VAT rate distribution
        vat_rates = {}
        for p in data:
            rate = p.get('vat_rate')
            vat_rates[rate] = vat_rates.get(rate, 0) + 1
        
        print(f"   ✓ VAT rate distribution: {vat_rates}")
        
        # Check only valid rates (4, 10, 2)
        valid_rates = {4, 10, 2}
        invalid_rates = set(vat_rates.keys()) - valid_rates
        if invalid_rates:
            print(f"   ⚠️  Invalid VAT rates found: {invalid_rates}")
            return False
        
        print(f"   ✓ All VAT rates are valid (4, 10, or 2)")
        return True
    
    runner.test(
        "GET /api/products (verify vat_rate field)",
        "GET",
        "products",
        200,
        params={"limit": 200},
        validate_fn=validate_vat_rates
    )

    # Test 22: Catalog sync status - with admin token
    if runner.token:
        print("\n" + "="*60)
        print("🔄 CATALOG SYNC STATUS - ADMIN")
        print("="*60)
        
        def validate_sync_status(data):
            if not isinstance(data, dict):
                print(f"   ⚠️  Response is not a dict")
                return False
            
            # Check required fields
            if "marker" not in data or "products_in_db" not in data:
                print(f"   ⚠️  Missing 'marker' or 'products_in_db' field")
                return False
            
            marker = data.get("marker", {})
            products_in_db = data.get("products_in_db", 0)
            
            print(f"   ✓ Products in DB: {products_in_db}")
            
            # Check marker fields
            if "excel_hash" not in marker:
                print(f"   ⚠️  Missing 'excel_hash' in marker")
                return False
            
            if "in_sync" not in marker:
                print(f"   ⚠️  Missing 'in_sync' in marker")
                return False
            
            print(f"   ✓ Excel hash: {marker.get('excel_hash', 'N/A')[:16]}...")
            print(f"   ✓ In sync: {marker.get('in_sync', False)}")
            print(f"   ✓ Imported at: {marker.get('imported_at', 'N/A')}")
            
            # Verify products count matches
            if products_in_db != 174:
                print(f"   ⚠️  Expected 174 products in DB, got {products_in_db}")
                return False
            
            # Verify in_sync is true
            if not marker.get('in_sync'):
                print(f"   ⚠️  Catalog not in sync (in_sync=false)")
                return False
            
            print(f"   ✓ Catalog in sync with Excel files")
            return True
        
        runner.test(
            "GET /api/admin/catalog/sync-status (with admin token)",
            "GET",
            "admin/catalog/sync-status",
            200,
            auth=True,
            validate_fn=validate_sync_status
        )

    # Test 23: Catalog sync status - without token (401)
    print("\n" + "="*60)
    print("🔒 CATALOG SYNC STATUS - AUTH PROTECTION")
    print("="*60)
    
    saved_token = runner.token
    runner.token = None
    
    runner.test(
        "GET /api/admin/catalog/sync-status (no auth - should fail)",
        "GET",
        "admin/catalog/sync-status",
        401
    )
    
    runner.token = saved_token

    # Test 24: Catalog sync - without token (401)
    print("\n" + "="*60)
    print("🔒 CATALOG SYNC - AUTH PROTECTION")
    print("="*60)
    
    saved_token = runner.token
    runner.token = None
    
    runner.test(
        "POST /api/admin/catalog/sync (no auth - should fail)",
        "POST",
        "admin/catalog/sync",
        401
    )
    
    runner.token = saved_token

    # Test 25: Admin coupons - GET list (should include ECOBONUS)
    if runner.token:
        print("\n" + "="*60)
        print("🎟️  ADMIN COUPONS - GET LIST")
        print("="*60)
        
        def validate_coupons_list(data):
            if not isinstance(data, dict):
                print(f"   ⚠️  Response is not a dict")
                return False
            if "coupons" not in data or "total" not in data:
                print(f"   ⚠️  Missing 'coupons' or 'total' field")
                return False
            coupons = data.get("coupons", [])
            total = data.get("total", 0)
            print(f"   ✓ Coupons list: {total} total coupons")
            
            # Check for ECOBONUS coupon
            ecobonus = None
            for c in coupons:
                if c.get("code") == "ECOBONUS":
                    ecobonus = c
                    break
            
            if not ecobonus:
                print(f"   ⚠️  ECOBONUS coupon not found!")
                return False
            
            print(f"   ✓ ECOBONUS coupon found:")
            print(f"     - discount_value: {ecobonus.get('discount_value')} (expected: 5)")
            print(f"     - discount_type: {ecobonus.get('discount_type')} (expected: fixed)")
            print(f"     - min_subtotal: {ecobonus.get('min_subtotal')} (expected: 60)")
            print(f"     - first_order_only: {ecobonus.get('first_order_only')} (expected: True)")
            print(f"     - active: {ecobonus.get('active')} (expected: True)")
            
            # Validate ECOBONUS fields
            if ecobonus.get('discount_value') != 5.0:
                print(f"   ⚠️  ECOBONUS discount_value should be 5.0")
                return False
            if ecobonus.get('discount_type') != "fixed":
                print(f"   ⚠️  ECOBONUS discount_type should be 'fixed'")
                return False
            if ecobonus.get('min_subtotal') != 60.0:
                print(f"   ⚠️  ECOBONUS min_subtotal should be 60.0")
                return False
            if not ecobonus.get('first_order_only'):
                print(f"   ⚠️  ECOBONUS first_order_only should be True")
                return False
            if not ecobonus.get('active'):
                print(f"   ⚠️  ECOBONUS active should be True")
                return False
            
            print(f"   ✓ ECOBONUS coupon validated successfully")
            return True
        
        success, coupons_data = runner.test(
            "GET /api/admin/coupons (verify ECOBONUS)",
            "GET",
            "admin/coupons",
            200,
            auth=True,
            validate_fn=validate_coupons_list
        )
    
    # Test 26: Admin coupons - GET without auth (should fail)
    print("\n" + "="*60)
    print("🔒 ADMIN COUPONS - AUTH PROTECTION")
    print("="*60)
    
    saved_token = runner.token
    runner.token = None
    
    runner.test(
        "GET /api/admin/coupons (no auth - should fail)",
        "GET",
        "admin/coupons",
        401
    )
    
    runner.token = saved_token
    
    # Test 27: Coupon validation - valid ECOBONUS (>=60€, new email)
    print("\n" + "="*60)
    print("🎟️  COUPON VALIDATION - ECOBONUS VALID")
    print("="*60)
    
    test_email_coupon = f"coupon_test_{int(time.time())}@example.com"
    
    def validate_coupon_valid_70(data):
        if not isinstance(data, dict):
            return False
        if not data.get('valid'):
            print(f"   ⚠️  Coupon should be valid for 70€ subtotal, new email")
            print(f"   Message: {data.get('message')}")
            return False
        if data.get('discount') != 5.0:
            print(f"   ⚠️  Discount should be 5.0, got {data.get('discount')}")
            return False
        print(f"   ✓ Coupon valid: discount={data.get('discount')}€, message={data.get('message')}")
        return True
    
    runner.test(
        "POST /api/orders/validate-coupon (ECOBONUS, 70€, new email)",
        "POST",
        "orders/validate-coupon",
        200,
        data={"code": "ECOBONUS", "email": test_email_coupon, "subtotal": 70.0},
        validate_fn=validate_coupon_valid_70
    )
    
    # Test 28: Coupon validation - invalid ECOBONUS (<60€)
    print("\n" + "="*60)
    print("🎟️  COUPON VALIDATION - ECOBONUS INVALID (<60€)")
    print("="*60)
    
    def validate_coupon_min_40(data):
        if not isinstance(data, dict):
            return False
        if data.get('valid'):
            print(f"   ⚠️  Coupon should be invalid for 40€ subtotal")
            return False
        message = data.get('message', '')
        if '60' not in message:
            print(f"   ⚠️  Error message should mention minimum 60€")
            return False
        print(f"   ✓ Coupon rejected for <60€: message={message}")
        return True
    
    runner.test(
        "POST /api/orders/validate-coupon (ECOBONUS, 40€ - below min)",
        "POST",
        "orders/validate-coupon",
        200,
        data={"code": "ECOBONUS", "email": test_email_coupon, "subtotal": 40.0},
        validate_fn=validate_coupon_min_40
    )
    
    # Test 29: Coupon validation - invalid code
    print("\n" + "="*60)
    print("🎟️  COUPON VALIDATION - INVALID CODE")
    print("="*60)
    
    def validate_coupon_invalid(data):
        if not isinstance(data, dict):
            return False
        if data.get('valid'):
            print(f"   ⚠️  Invalid coupon code should be rejected")
            return False
        print(f"   ✓ Invalid code rejected: message={data.get('message')}")
        return True
    
    runner.test(
        "POST /api/orders/validate-coupon (INVALIDCODE)",
        "POST",
        "orders/validate-coupon",
        200,
        data={"code": "INVALIDCODE", "email": test_email_coupon, "subtotal": 70.0},
        validate_fn=validate_coupon_invalid
    )
    
    # Test 30: Admin coupons - CREATE new coupon
    if runner.token:
        print("\n" + "="*60)
        print("🎟️  ADMIN COUPONS - CREATE")
        print("="*60)
        
        test_coupon_code = f"TESTCOUPON{int(time.time()) % 10000}"
        
        def validate_coupon_create(data):
            if not isinstance(data, dict):
                return False
            if data.get('code') != test_coupon_code:
                print(f"   ⚠️  Created coupon code mismatch")
                return False
            if data.get('discount_type') != "percent":
                print(f"   ⚠️  discount_type should be 'percent'")
                return False
            if data.get('discount_value') != 10.0:
                print(f"   ⚠️  discount_value should be 10.0")
                return False
            if data.get('min_subtotal') != 20.0:
                print(f"   ⚠️  min_subtotal should be 20.0")
                return False
            print(f"   ✓ Coupon created: {data.get('code')}, {data.get('discount_value')}% off, min {data.get('min_subtotal')}€")
            return True
        
        success, created_coupon = runner.test(
            f"POST /api/admin/coupons (create {test_coupon_code})",
            "POST",
            "admin/coupons",
            200,
            data={
                "code": test_coupon_code,
                "description": "Test coupon for automated testing",
                "discount_type": "percent",
                "discount_value": 10,
                "min_subtotal": 20,
                "first_order_only": False,
                "usage_limit": None,
                "expires_at": None,
                "active": True
            },
            auth=True,
            validate_fn=validate_coupon_create
        )
        
        # Test 31: Admin coupons - CREATE duplicate (should fail with 409)
        if success:
            print("\n" + "="*60)
            print("🎟️  ADMIN COUPONS - CREATE DUPLICATE (409)")
            print("="*60)
            
            runner.test(
                f"POST /api/admin/coupons (duplicate {test_coupon_code} - should fail)",
                "POST",
                "admin/coupons",
                409,
                data={
                    "code": test_coupon_code,
                    "description": "Duplicate",
                    "discount_type": "fixed",
                    "discount_value": 5,
                    "min_subtotal": 0,
                    "first_order_only": False,
                    "usage_limit": None,
                    "expires_at": None,
                    "active": True
                },
                auth=True
            )
            
            # Test 32: Admin coupons - UPDATE (toggle active)
            print("\n" + "="*60)
            print("🎟️  ADMIN COUPONS - UPDATE (toggle active)")
            print("="*60)
            
            coupon_id = created_coupon.get('id')
            
            def validate_coupon_update(data):
                if not isinstance(data, dict):
                    return False
                if data.get('active') != False:
                    print(f"   ⚠️  Coupon should be inactive after toggle")
                    return False
                print(f"   ✓ Coupon updated: active={data.get('active')}")
                return True
            
            runner.test(
                f"PUT /api/admin/coupons/{coupon_id} (toggle active to false)",
                "PUT",
                f"admin/coupons/{coupon_id}",
                200,
                data={
                    "code": test_coupon_code,
                    "description": "Test coupon for automated testing",
                    "discount_type": "percent",
                    "discount_value": 10,
                    "min_subtotal": 20,
                    "first_order_only": False,
                    "usage_limit": None,
                    "expires_at": None,
                    "active": False
                },
                auth=True,
                validate_fn=validate_coupon_update
            )
            
            # Test 33: Admin coupons - DELETE
            print("\n" + "="*60)
            print("🎟️  ADMIN COUPONS - DELETE (cleanup)")
            print("="*60)
            
            def validate_coupon_delete(data):
                if not isinstance(data, dict):
                    return False
                if data.get('ok') != True:
                    print(f"   ⚠️  Expected ok=true")
                    return False
                print(f"   ✓ Coupon deleted: ok={data.get('ok')}")
                return True
            
            runner.test(
                f"DELETE /api/admin/coupons/{coupon_id}",
                "DELETE",
                f"admin/coupons/{coupon_id}",
                200,
                auth=True,
                validate_fn=validate_coupon_delete
            )
    
    # Test 34: Hero mobile images - verify new PNG URLs
    print("\n" + "="*60)
    print("📱 HERO MOBILE IMAGES - NEW PNG URLS")
    print("="*60)
    
    # Expected PNG URL identifiers from the new mobile images
    EXPECTED_MOBILE_IDS = [
        'AFpOyXS9EdXcHiOA',  # slide 1
        '9FNNDdbX2vC0F87G',  # slide 2
        'TbzHNlprrFOyaD9M',  # slide 3
        'wMgPeXW98mqWtT29',  # slide 4
        '3dw2ffgiXbdSptJh',  # slide 5
    ]
    
    def validate_hero_mobile_images(data):
        if not isinstance(data, dict):
            print(f"   ⚠️  Response is not a dict")
            return False
        slides = data.get("slides", [])
        if len(slides) < 5:
            print(f"   ⚠️  Expected at least 5 slides, got {len(slides)}")
            return False
        
        print(f"   ✓ Hero has {len(slides)} slides")
        
        # Check each slide's image_mobile URL
        all_valid = True
        for i, slide in enumerate(slides[:5]):
            image_mobile = slide.get("image_mobile", "")
            expected_id = EXPECTED_MOBILE_IDS[i]
            
            if expected_id in image_mobile:
                print(f"   ✓ Slide {i+1} image_mobile contains '{expected_id}'")
            else:
                print(f"   ⚠️  Slide {i+1} image_mobile does NOT contain '{expected_id}'")
                print(f"      Got: {image_mobile}")
                all_valid = False
        
        return all_valid
    
    runner.test(
        "GET /api/hero (verify mobile image URLs)",
        "GET",
        "hero",
        200,
        validate_fn=validate_hero_mobile_images
    )

    # Test 35: Catalog sync - idempotent re-run
    if runner.token:
        print("\n" + "="*60)
        print("🔄 CATALOG SYNC - IDEMPOTENT RE-RUN")
        print("="*60)
        
        def validate_sync_start(data):
            if not isinstance(data, dict):
                print(f"   ⚠️  Response is not a dict")
                return False
            
            if "started" not in data:
                print(f"   ⚠️  Missing 'started' field")
                return False
            
            started = data.get("started")
            print(f"   ✓ Sync started: {started}")
            
            if started:
                print(f"   ✓ Background sync task initiated")
            else:
                reason = data.get("reason", "N/A")
                print(f"   ✓ Sync not started (reason: {reason})")
            
            return True
        
        success, sync_response = runner.test(
            "POST /api/admin/catalog/sync (trigger sync)",
            "POST",
            "admin/catalog/sync",
            200,
            auth=True,
            validate_fn=validate_sync_start
        )
        
        if success and sync_response.get("started"):
            print(f"   ⏳ Waiting for sync to complete (polling sync-status)...")
            import time
            max_wait = 60  # 60 seconds max
            poll_interval = 3  # 3 seconds
            waited = 0
            
            while waited < max_wait:
                time.sleep(poll_interval)
                waited += poll_interval
                
                # Poll sync status
                success_poll, status_data = runner.test(
                    f"GET /api/admin/catalog/sync-status (poll #{waited//poll_interval})",
                    "GET",
                    "admin/catalog/sync-status",
                    200,
                    auth=True
                )
                
                if success_poll:
                    status = status_data.get("status", {})
                    running = status.get("running", False)
                    error = status.get("error")
                    
                    if error:
                        print(f"   ❌ Sync failed with error: {error}")
                        break
                    
                    if not running:
                        print(f"   ✅ Sync completed successfully")
                        
                        # Verify final state
                        marker = status_data.get("marker", {})
                        products_in_db = status_data.get("products_in_db", 0)
                        in_sync = marker.get("in_sync", False)
                        
                        print(f"   ✓ Final state: products={products_in_db}, in_sync={in_sync}")
                        
                        if products_in_db != 174:
                            print(f"   ⚠️  Expected 174 products after sync, got {products_in_db}")
                        
                        if not in_sync:
                            print(f"   ⚠️  Catalog not in sync after sync operation")
                        
                        break
                else:
                    print(f"   ⚠️  Failed to poll sync status")
                    break
            
            if waited >= max_wait:
                print(f"   ⚠️  Sync did not complete within {max_wait} seconds")

    # Print summary
    runner.print_summary()
    
    # Return exit code
    return 0 if runner.tests_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
