"""Tests for PWA features — manifest, service worker, offline page, CSP."""

import pytest
from conftest import go, should_have_text, should_exist, BASE_URL


class TestManifest:
    """PWA Web App Manifest tests."""

    def test_manifest_returns_json(self, page):
        response = page.goto(f"{BASE_URL}/manifest.json")
        assert response.status == 200
        content_type = response.headers.get("content-type", "")
        assert "json" in content_type

    def test_manifest_content(self, page):
        response = page.goto(f"{BASE_URL}/manifest.json")
        data = response.json()
        assert data["name"] == "Vandana Geet"
        assert data["short_name"] == "songbook"
        assert data["display"] == "standalone"
        assert data["start_url"] == "/"
        assert data["scope"] == "/"
        assert "icons" in data
        assert len(data["icons"]) >= 2

    def test_manifest_has_masked_icon(self, page):
        response = page.goto(f"{BASE_URL}/manifest.json")
        data = response.json()
        maskable = [i for i in data["icons"] if "purpose" in i and "maskable" in i["purpose"]]
        assert len(maskable) >= 1


class TestOfflinePage:
    """Offline fallback page tests."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/offline.html")

    def test_offline_page_loads(self, page):
        assert page.locator("h1").is_visible()

    def test_offline_page_title(self, page):
        assert "Offline" in page.title()

    def test_offline_message(self, page):
        """Find the offline message heading."""
        should_have_text(page, "h1", "No internet connection")

    def test_offline_has_helpful_text(self, page):
        """The offline text is in a paragraph inside the main content area."""
        content_paragraphs = page.locator(".container p")
        found = False
        for i in range(content_paragraphs.count()):
            text = content_paragraphs.nth(i).text_content() or ""
            if "couldn't find" in text.lower() or "connection" in text.lower():
                found = True
                break
        assert found, "Could not find helpful offline text"

    def test_offline_has_home_link(self, page):
        """Find the 'Go to Home' link specifically (not the header home link)."""
        # The offline page has a specific link styled as a button
        link = page.locator('.container a[href="/"]')
        assert link.is_visible()
        assert "Home" in (link.text_content() or "")

    def test_offline_home_link_works(self, page):
        """Clicking the Go to Home link navigates to homepage."""
        link = page.locator('.container a[href="/"]')
        link.click()
        page.wait_for_load_state("networkidle")
        assert page.locator(".language-card").count() == 3

    def test_offline_page_has_header(self, page):
        """Offline page still has the main navigation header."""
        should_exist(page, ".header")

    def test_offline_page_has_footer(self, page):
        should_exist(page, ".footer")


class TestServiceWorker:
    """Service worker registration and offline support."""

    def test_service_worker_registered(self, page):
        go(page, "/")
        # Service worker registration happens on window load
        registered = page.evaluate("""async () => {
            if ('serviceWorker' in navigator) {
                const reg = await navigator.serviceWorker.ready;
                return reg.active !== null;
            }
            return false;
        }""")
        assert registered, "Service Worker not registered"

    def test_service_worker_scope(self, page):
        go(page, "/")
        scope = page.evaluate("""async () => {
            if ('serviceWorker' in navigator) {
                const reg = await navigator.serviceWorker.ready;
                return reg.scope;
            }
            return null;
        }""")
        assert scope is not None
        # Scope should be the origin root
        assert "/" in scope

    def test_offline_indicator_present(self, page):
        go(page, "/")
        indicator = page.locator("#offline-indicator")
        assert indicator.count() > 0
        assert "Viewing offline" in (indicator.text_content() or "")


class TestCSP:
    """Content Security Policy tests."""

    def test_csp_meta_tag_present(self, page):
        go(page, "/")
        meta = page.locator('meta[http-equiv="Content-Security-Policy"]')
        assert meta.count() > 0
        content = meta.get_attribute("content") or ""
        assert "default-src 'self'" in content

    def test_csp_allows_inline_styles(self, page):
        go(page, "/")
        meta = page.locator('meta[http-equiv="Content-Security-Policy"]')
        content = meta.get_attribute("content") or ""
        assert "style-src 'self' 'unsafe-inline'" in content

    def test_csp_restricts_scripts_to_self(self, page):
        go(page, "/")
        meta = page.locator('meta[http-equiv="Content-Security-Policy"]')
        content = meta.get_attribute("content") or ""
        assert "script-src 'self'" in content

    def test_csp_restricts_fonts_to_self(self, page):
        go(page, "/")
        meta = page.locator('meta[http-equiv="Content-Security-Policy"]')
        content = meta.get_attribute("content") or ""
        assert "font-src 'self'" in content


class TestPWAFeatures:
    """PWA-specific features and metadata."""

    def test_apple_touch_icon(self, page):
        go(page, "/")
        link = page.locator('link[rel="apple-touch-icon"]')
        assert link.count() > 0
        assert "icon-192" in (link.get_attribute("href") or "")

    def test_mobile_web_app_capable(self, page):
        go(page, "/")
        meta = page.locator('meta[name="mobile-web-app-capable"]')
        assert meta.get_attribute("content") == "yes"

    def test_apple_webapp_title(self, page):
        go(page, "/")
        meta = page.locator('meta[name="apple-mobile-web-app-title"]')
        assert meta.get_attribute("content") == "Vandana Geet"

    def test_ios_install_hint_initialized(self, page):
        """iOS install hint div exists (hidden by default)."""
        go(page, "/")
        hint = page.locator("#ios-install-hint")
        assert hint.count() > 0
        style = hint.get_attribute("style") or ""
        assert "display:none" in style.replace(" ", "")
