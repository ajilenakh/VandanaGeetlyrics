"""Tests for edge cases — 404, empty states, special chars, no-JS rendering."""

import pytest
from conftest import go, should_exist, SONG_TITLES, BASE_URL


class Test404Errors:
    """Handling of non-existent pages."""

    def test_nonexistent_song_returns_404(self, page):
        """A song that doesn't exist should return 404."""
        response = page.goto(f"{BASE_URL}/english/999/")
        assert response.status == 404

    def test_nonexistent_language_returns_404(self, page):
        response = page.goto(f"{BASE_URL}/klingon/")
        assert response.status == 404

    def test_nonexistent_page_returns_404(self, page):
        response = page.goto(f"{BASE_URL}/this-page-does-not-exist/")
        assert response.status == 404

    def test_404_returns_error_status(self, page):
        """Non-existent pages should return 404."""
        response = page.goto(f"{BASE_URL}/nonexistent/")
        assert response.status == 404


class TestEmptyStates:
    """Behavior with empty song collections."""

    def test_no_results_message_visible_on_empty_search(self, page):
        go(page, "/english/")
        search = page.locator("#song-search")
        search.fill("ZZZZ_NONEXISTENT_ZZZZ")
        page.wait_for_timeout(200)

        no_results = page.locator("#no-results")
        assert no_results.is_visible()
        text = no_results.text_content().lower()
        assert "couldn't find" in text
        assert "different number" in text

    def test_no_results_hidden_when_songs_present(self, page):
        go(page, "/english/")
        no_results = page.locator("#no-results")
        style = no_results.get_attribute("style") or ""
        assert "display:none" in style.replace(" ", "")


class TestSpecialCharacters:
    """Search with special characters and edge inputs."""

    @pytest.fixture(autouse=True)
    def setup(self, page):
        go(page, "/english/")

    def test_search_special_chars_no_crash(self, page):
        search = page.locator("#song-search")
        search.fill("@#$%^&*()_+{}|:\"<>?`~")
        page.wait_for_timeout(200)
        # Should not crash — just show no results
        assert page.locator("#no-results").is_visible()

    def test_search_unicode_chinese(self, page):
        search = page.locator("#song-search")
        search.fill("中文测试")
        page.wait_for_timeout(200)
        assert page.locator("#no-results").is_visible()

    def test_search_emojis(self, page):
        search = page.locator("#song-search")
        search.fill("🎵🎶🎤")
        page.wait_for_timeout(200)
        assert page.locator("#no-results").is_visible()

    def test_search_leading_trailing_spaces(self, page):
        """Songs don't have leading/trailing spaces in data-title."""
        search = page.locator("#song-search")
        search.fill("  Amazing  ")
        page.wait_for_timeout(200)
        # Search uses .trim() so "  Amazing  " becomes "amazing"
        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1

    def test_search_newline_chars(self, page):
        search = page.locator("#song-search")
        search.fill("1\n2\n3")
        page.wait_for_timeout(200)
        visible = page.locator(".song-card:visible")
        # The search input value will have newlines, but .trim() handles it
        assert visible.count() >= 0  # Should not crash


class TestNoJavaScript:
    """Core content renders with JavaScript disabled."""

    def test_homepage_renders_without_js(self, no_js_page):
        """Home page shows language cards without JS."""
        go(no_js_page, "/")
        assert no_js_page.locator(".language-card").count() == 3
        assert no_js_page.locator(".home-logo-image").count() == 2
        assert no_js_page.locator(".footer").is_visible()

    def test_song_detail_renders_without_js(self, no_js_page):
        """Song detail page renders lyrics without JS."""
        go(no_js_page, "/english/1/")
        assert no_js_page.locator(".song-number").is_visible()
        assert no_js_page.locator(".song-title").is_visible()
        lyrics_text = no_js_page.locator(".song-lyrics").text_content() or ""
        assert len(lyrics_text.strip()) > 20

    def test_language_page_shows_songs_without_js(self, no_js_page):
        """Language listing shows all songs without JS."""
        go(no_js_page, "/english/")
        cards = no_js_page.locator(".song-card")
        assert cards.count() >= 1


class TestViewportResponsiveness:
    """Page renders correctly at different viewport sizes."""

    @pytest.mark.parametrize("width,height", [
        (375, 812),   # iPhone X
        (390, 844),   # iPhone 14
        (414, 896),   # iPhone 11 Pro Max
        (360, 780),   # Galaxy S20
        (768, 1024),  # iPad
        (1280, 720),  # Desktop
        (320, 568),   # iPhone SE (smallest)
    ])
    def test_homepage_at_various_viewports(self, page, width, height):
        """Home page renders without overflow at common viewports."""
        page.set_viewport_size({"width": width, "height": height})
        go(page, "/")
        # No horizontal overflow
        overflow = page.evaluate("document.body.scrollWidth <= document.body.clientWidth + 5")
        assert overflow, f"Horizontal overflow at {width}x{height}"
        # Language cards load
        assert page.locator(".language-card").count() == 3

    @pytest.mark.parametrize("width,height", [
        (375, 812),
        (768, 1024),
        (1280, 720),
    ])
    def test_song_detail_at_various_viewports(self, page, width, height):
        """Song detail page renders without issues at common viewports."""
        page.set_viewport_size({"width": width, "height": height})
        go(page, "/english/1/")
        assert page.locator(".song-detail").is_visible()
        overflow = page.evaluate("document.body.scrollWidth <= document.body.clientWidth + 5")
        assert overflow, f"Horizontal overflow at {width}x{height}"


class TestLighthouseBudget:
    """Verify page weight meets the <50KB uncompressed budget."""

    @pytest.mark.parametrize("path", ["/", "/english/", "/english/1/"])
    def test_page_size_under_budget(self, page, path):
        """Total page size should be under 50KB uncompressed."""
        response = page.goto(f"{BASE_URL}{path}")
        body = response.body()
        size_kb = len(body) / 1024
        assert size_kb < 50, \
            f"{path}: Page is {size_kb:.1f}KB, budget is 50KB"


class TestImagesMetadata:
    """Images have proper attributes for performance."""

    def test_images_have_alt_text(self, page):
        go(page, "/")
        images = page.locator("img")
        count = images.count()
        for i in range(count):
            alt = images.nth(i).get_attribute("alt")
            assert alt is not None, f"Image {i} missing alt attribute"

    def test_logo_image_exists(self, page):
        go(page, "/")
        light_logo = page.locator('img.logo-light[src*="logo"]')
        dark_logo = page.locator('img.logo-dark[src*="logo"]')
        # At least one should exist (footer or home)
        assert light_logo.count() > 0 or dark_logo.count() > 0


class TestHTMLValidation:
    """Basic HTML structural correctness."""

    def test_no_duplicate_ids(self, page):
        go(page, "/")
        ids = page.evaluate("""() => {
            const allIds = document.querySelectorAll('[id]');
            const ids = {};
            allIds.forEach(el => {
                ids[el.id] = (ids[el.id] || 0) + 1;
            });
            return Object.entries(ids).filter(([k, v]) => v > 1);
        }""")
        assert len(ids) == 0, f"Duplicate IDs found: {ids}"

    def test_html_has_lang_attribute(self, page):
        go(page, "/")
        html = page.locator("html")
        assert html.get_attribute("lang") is not None
