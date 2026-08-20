"""
EcoAndes Backend Testing - Carousel Categories Feature
Tests: Carousel API (public + admin CRUD with auto-generated descriptions)
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

    # ========== BLOG API TESTS ==========
    def test_blog_public_list():
        """Test GET /api/blog returns published posts"""
        resp = requests.get(f"{BASE_URL}/api/blog")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        posts = resp.json()
        assert isinstance(posts, list), "Response should be a list"
        print(f"   Found {len(posts)} published post(s)")
        
        # Verify we have the expected 12 posts
        assert len(posts) == 12, f"Expected 12 posts, got {len(posts)}"
        
        # Check structure of first post
        if posts:
            p = posts[0]
            assert "slug" in p, "Missing slug"
            assert "title" in p, "Missing title"
            assert "excerpt" in p, "Missing excerpt"
            assert "cover" in p, "Missing cover"
            assert "category" in p, "Missing category"
            assert "seo" in p, "Missing seo"
            print(f"   First post: {p['title'][:50]}")
            print(f"   SEO meta_title: {p['seo'].get('meta_title', 'N/A')[:50]}")

    def test_blog_public_get_by_slug():
        """Test GET /api/blog/{slug} returns full post"""
        slug = "quinoa-real-ecologica-superalimento"
        resp = requests.get(f"{BASE_URL}/api/blog/{slug}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        post = resp.json()
        
        assert post["slug"] == slug, f"Wrong slug: {post['slug']}"
        assert "body" in post, "Missing body"
        assert "sources" in post, "Missing sources"
        assert isinstance(post["body"], list), "body should be a list"
        assert isinstance(post["sources"], list), "sources should be a list"
        print(f"   Post: {post['title']}")
        print(f"   Body sections: {len(post['body'])}")
        print(f"   Sources: {len(post['sources'])}")

    def test_blog_public_404():
        """Test GET /api/blog/{slug} returns 404 for invalid slug"""
        resp = requests.get(f"{BASE_URL}/api/blog/nonexistent-slug-12345")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print(f"   Correctly returns 404 for invalid slug")

    def test_blog_admin_requires_auth():
        """Test GET /api/blog/admin/list requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/blog/admin/list")
        assert resp.status_code == 401, f"Expected 401 without token, got {resp.status_code}"
        print(f"   Correctly returns 401 without token")

    def test_blog_admin_list():
        """Test GET /api/blog/admin/list with auth"""
        resp = requests.get(f"{BASE_URL}/api/blog/admin/list", headers=runner.headers())
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        posts = resp.json()
        assert isinstance(posts, list), "Response should be a list"
        print(f"   Found {len(posts)} post(s) in admin view")
        assert len(posts) == 12, f"Expected 12 posts, got {len(posts)}"
        return posts

    def test_blog_admin_crud():
        """Test CREATE, UPDATE, DELETE blog post"""
        # CREATE
        new_post = {
            "title": "TEST Post - Automated Testing",
            "slug": "test-post-automated",
            "excerpt": "This is a test post created by automated testing",
            "cover": "/blog/test.webp",
            "category": "TEST",
            "read_time": "1 min",
            "date": "2026-03-15",
            "author": "Test Bot",
            "related_query": "test",
            "body": [
                {"h": "Test Section", "p": "Test content for automated testing"}
            ],
            "sources": [
                {"label": "Test Source", "url": "https://example.com/test"}
            ],
            "seo": {
                "meta_title": "Test Post SEO Title",
                "meta_description": "Test post meta description",
                "keywords": ["test", "automated"]
            },
            "published": True
        }
        
        resp = requests.post(
            f"{BASE_URL}/api/blog/admin",
            headers=runner.headers(),
            json=new_post
        )
        assert resp.status_code == 200, f"Failed to create post: {resp.status_code} {resp.text}"
        created = resp.json()
        assert "id" in created, "No id in created post"
        post_id = created["id"]
        print(f"   ✅ Created post: {post_id}")
        
        # Verify it appears in public list
        resp = requests.get(f"{BASE_URL}/api/blog")
        posts = resp.json()
        assert len(posts) == 13, f"Expected 13 posts after creation, got {len(posts)}"
        print(f"   ✅ Post appears in public list (13 posts)")
        
        # UPDATE
        updated_post = new_post.copy()
        updated_post["title"] = "TEST Post - UPDATED"
        updated_post["published"] = False
        
        resp = requests.put(
            f"{BASE_URL}/api/blog/admin/{post_id}",
            headers=runner.headers(),
            json=updated_post
        )
        assert resp.status_code == 200, f"Failed to update post: {resp.status_code} {resp.text}"
        updated = resp.json()
        assert updated["title"] == "TEST Post - UPDATED", "Title not updated"
        assert updated["published"] is False, "Published flag not updated"
        print(f"   ✅ Updated post: title changed, published=false")
        
        # Verify it's hidden from public list
        resp = requests.get(f"{BASE_URL}/api/blog")
        posts = resp.json()
        assert len(posts) == 12, f"Expected 12 posts after unpublish, got {len(posts)}"
        print(f"   ✅ Unpublished post hidden from public (12 posts)")
        
        # DELETE
        resp = requests.delete(
            f"{BASE_URL}/api/blog/admin/{post_id}",
            headers=runner.headers()
        )
        assert resp.status_code == 200, f"Failed to delete post: {resp.status_code}"
        print(f"   ✅ Deleted post: {post_id}")
        
        # Verify it's gone
        resp = requests.get(f"{BASE_URL}/api/blog/admin/list", headers=runner.headers())
        posts = resp.json()
        assert len(posts) == 12, f"Expected 12 posts after deletion, got {len(posts)}"
        print(f"   ✅ Post removed from admin list (12 posts)")

    # ========== SITE IMAGES API TESTS ==========
    def test_site_images_public():
        """Test GET /api/site-images returns all image keys"""
        resp = requests.get(f"{BASE_URL}/api/site-images")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "images" in data, "No 'images' in response"
        images = data["images"]
        
        # Check all 4 keys exist
        required_keys = ["collection_main", "b2b_landscape", "b2b_portrait", "philosophy"]
        for key in required_keys:
            assert key in images, f"Missing key: {key}"
            assert images[key], f"Empty value for key: {key}"
            print(f"   {key}: {images[key][:60]}...")

    def test_site_images_admin_requires_auth():
        """Test GET /api/site-images/admin requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/site-images/admin")
        assert resp.status_code == 401, f"Expected 401 without token, got {resp.status_code}"
        print(f"   Correctly returns 401 without token")

    def test_site_images_admin_get():
        """Test GET /api/site-images/admin with auth"""
        resp = requests.get(f"{BASE_URL}/api/site-images/admin", headers=runner.headers())
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "images" in data, "No 'images' in response"
        assert "defaults" in data, "No 'defaults' in response"
        assert "spots" in data, "No 'spots' in response"
        print(f"   Found {len(data['spots'])} image spot(s)")
        for spot in data['spots']:
            print(f"   - {spot['label']}: {spot['where']}")

    def test_site_images_admin_update_and_restore():
        """Test PUT /api/site-images/admin - update and restore"""
        # Get current images
        resp = requests.get(f"{BASE_URL}/api/site-images/admin", headers=runner.headers())
        assert resp.status_code == 200, "Failed to get current images"
        original = resp.json()
        original_images = original["images"]
        defaults = original["defaults"]
        print(f"   Original collection_main: {original_images['collection_main'][:60]}...")
        
        # Update collection_main to test URL
        test_url = "https://picsum.photos/seed/eco-col/800/600.jpg"
        updated_images = original_images.copy()
        updated_images["collection_main"] = test_url
        
        resp = requests.put(
            f"{BASE_URL}/api/site-images/admin",
            headers=runner.headers(),
            json={"images": updated_images}
        )
        assert resp.status_code == 200, f"Failed to update: {resp.status_code} {resp.text}"
        data = resp.json()
        assert data["images"]["collection_main"] == test_url, "URL not updated"
        print(f"   ✅ Updated collection_main to: {test_url}")
        
        # Verify public endpoint returns new URL
        resp = requests.get(f"{BASE_URL}/api/site-images")
        assert resp.status_code == 200, "Failed to get public images"
        public_images = resp.json()["images"]
        assert public_images["collection_main"] == test_url, "Public endpoint not updated"
        print(f"   ✅ Public endpoint reflects new URL")
        
        # Restore to default
        restored_images = original_images.copy()
        restored_images["collection_main"] = defaults["collection_main"]
        
        resp = requests.put(
            f"{BASE_URL}/api/site-images/admin",
            headers=runner.headers(),
            json={"images": restored_images}
        )
        assert resp.status_code == 200, f"Failed to restore: {resp.status_code}"
        data = resp.json()
        assert data["images"]["collection_main"] == defaults["collection_main"], "Not restored to default"
        print(f"   ✅ Restored collection_main to default: {defaults['collection_main'][:60]}...")

    # ========== CAROUSEL CATEGORIES API TESTS ==========
    def test_carousel_public_get():
        """Test GET /api/carousel-categories returns 15 items with auto-descriptions"""
        resp = requests.get(f"{BASE_URL}/api/carousel-categories")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "items" in data, "No 'items' in response"
        items = data["items"]
        
        # Should have 15 items (default seed)
        assert len(items) == 15, f"Expected 15 items, got {len(items)}"
        print(f"   Found {len(items)} carousel items")
        
        # Check structure of first item
        first = items[0]
        assert "id" in first, "Missing id"
        assert "title" in first, "Missing title"
        assert "cat" in first, "Missing cat"
        assert "img" in first, "Missing img"
        assert "description" in first, "Missing description"
        assert "product_count" in first, "Missing product_count"
        
        print(f"   First item: {first['title']}")
        print(f"   Category: {first['cat']}")
        print(f"   Product count: {first['product_count']}")
        print(f"   Description: {first['description'][:80]}...")
        
        # Verify all items have descriptions (auto-generated or manual)
        for idx, item in enumerate(items):
            assert "description" in item, f"Item {idx} missing description"
            assert "product_count" in item, f"Item {idx} missing product_count"
            if item.get("cat"):
                # Items with categories should have product info
                print(f"   Item {idx+1}: {item['title']} - {item['product_count']} productos")
        
        return items

    def test_carousel_admin_requires_auth():
        """Test GET /api/admin/carousel-categories requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/admin/carousel-categories")
        assert resp.status_code == 401, f"Expected 401 without token, got {resp.status_code}"
        print(f"   Correctly returns 401 without token")

    def test_carousel_admin_get():
        """Test GET /api/admin/carousel-categories with auth"""
        resp = requests.get(f"{BASE_URL}/api/admin/carousel-categories", headers=runner.headers())
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "items" in data, "No 'items' in response"
        items = data["items"]
        print(f"   Found {len(items)} items in admin view")
        return items

    def test_carousel_admin_manual_description():
        """Test manual description save and auto-generation restore"""
        # Get current items
        resp = requests.get(f"{BASE_URL}/api/admin/carousel-categories", headers=runner.headers())
        assert resp.status_code == 200, "Failed to get carousel items"
        data = resp.json()
        items = data["items"]
        assert len(items) > 0, "No items to test"
        
        # Save original first item
        original_first = items[0].copy()
        print(f"   Original first item: {original_first['title']}")
        print(f"   Original description: {original_first.get('description', '')[:80]}...")
        
        # Set manual description on first item
        manual_desc = "Esta es una descripción manual de prueba para testing automatizado."
        items[0]["description"] = manual_desc
        
        resp = requests.put(
            f"{BASE_URL}/api/admin/carousel-categories",
            headers=runner.headers(),
            json={"items": items}
        )
        assert resp.status_code == 200, f"Failed to save: {resp.status_code} {resp.text}"
        print(f"   ✅ Saved manual description")
        
        # Verify manual description appears in public endpoint
        resp = requests.get(f"{BASE_URL}/api/carousel-categories")
        assert resp.status_code == 200, "Failed to get public carousel"
        public_items = resp.json()["items"]
        first_public = public_items[0]
        assert first_public["description"] == manual_desc, "Manual description not used"
        print(f"   ✅ Manual description appears in public endpoint")
        
        # Clear description (empty string) to restore auto-generation
        resp = requests.get(f"{BASE_URL}/api/admin/carousel-categories", headers=runner.headers())
        items = resp.json()["items"]
        items[0]["description"] = ""
        
        resp = requests.put(
            f"{BASE_URL}/api/admin/carousel-categories",
            headers=runner.headers(),
            json={"items": items}
        )
        assert resp.status_code == 200, f"Failed to clear description: {resp.status_code}"
        print(f"   ✅ Cleared description")
        
        # Verify auto-generated description is restored
        resp = requests.get(f"{BASE_URL}/api/carousel-categories")
        public_items = resp.json()["items"]
        first_public = public_items[0]
        assert first_public["description"] != manual_desc, "Manual description still present"
        assert first_public["description"] != "", "Description should be auto-generated"
        # Auto-generated should contain product names
        assert len(first_public["description"]) > 0, "Auto-generated description is empty"
        print(f"   ✅ Auto-generated description restored: {first_public['description'][:80]}...")

    # ========== RUN ALL TESTS ==========
    runner.test("Carousel: GET /api/carousel-categories (public)", test_carousel_public_get)
    runner.test("Carousel: GET /api/admin/carousel-categories requires auth", test_carousel_admin_requires_auth)
    runner.test("Carousel: GET /api/admin/carousel-categories with auth", test_carousel_admin_get)
    runner.test("Carousel: Manual description save and auto-restore", test_carousel_admin_manual_description)

    return runner.summary()


if __name__ == "__main__":
    sys.exit(main())
