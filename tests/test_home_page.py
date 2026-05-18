"""Tests for the home page — structure, language cards, header, footer."""

import pytest
from conftest import (
    go, should_have_text, should_have_count, should_exist,
    SONGS_BY_LANG
)


class TestHomePageStructure:
    """Verify the home page renders all expected elements."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_page_title(self, page):
        assert "Church Songbook" in page.title()

    def test_home_subtitle(self, page):
        should_have_text(page, ".home-subtitle", "Select a language to browse songs")

    def test_logo_images_present(self, page):
        """Both light and dark logo images exist in the DOM."""
        should_have_count(page, ".home-logo-image", 2)

    def test_logo_has_alt_text(self, page):
        logos = page.locator(".home-logo-image")
        count = logos.count()
        for i in range(count):
            alt = logos.nth(i).get_attribute("alt")
            assert alt, f"Logo {i} missing alt text"

    def test_language_cards_count(self, page):
        """One card per language with songs."""
        expected = len(SONGS_BY_LANG)
        should_have_count(page, ".language-card", expected)

    def test_bengali_card(self, page):
        card = page.locator('.language-card[href$="/bengali/"]')
        assert card.count() == 1
        assert "বাংলা" in card.text_content()

    def test_hindi_card(self, page):
        card = page.locator('.language-card[href$="/hindi/"]')
        assert card.count() == 1
        assert "हिंदी" in card.text_content()

    def test_english_card(self, page):
        card = page.locator('.language-card[href$="/english/"]')
        assert card.count() == 1
        assert "English" in card.text_content()

    def test_language_card_links(self, page):
        """Each language card links to the correct path."""
        cards = page.locator(".language-card")
        assert cards.nth(0).get_attribute("href").endswith("/bengali/")
        assert cards.nth(1).get_attribute("href").endswith("/hindi/")
        assert cards.nth(2).get_attribute("href").endswith("/english/")


class TestHomePageHeader:
    """Verify the header/navigation on the home page."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_home_link_exists(self, page):
        """Header contains a home link with an SVG icon."""
        link = page.locator('a.home-link[aria-label="Home"]')
        assert link.is_visible()
        assert link.locator("svg.home-icon").count() > 0

    def test_language_switcher_has_three_links(self, page):
        should_have_count(page, ".lang-link", 3)

    def test_language_switcher_labels(self, page):
        langs = page.locator(".lang-link")
        assert langs.nth(0).text_content().strip() == "বাংলা"
        assert langs.nth(1).text_content().strip() == "हिंदी"
        assert langs.nth(2).text_content().strip() == "English"

    def test_language_switcher_has_aria_label(self, page):
        nav = page.locator("nav.language-switcher")
        label = nav.get_attribute("aria-label")
        assert label == "Language navigation"

    def test_theme_toggle_button_exists(self, page):
        btn = page.locator("#theme-toggle")
        assert btn.is_visible()
        assert btn.get_attribute("aria-label") == "Toggle theme"

    def test_font_controls_exist(self, page):
        assert page.locator("#font-decrease").is_visible()
        assert page.locator("#font-increase").is_visible()
        assert page.locator("#font-reset").is_visible()

    def test_install_button_hidden_by_default(self, page):
        """Install button is hidden until beforeinstallprompt fires."""
        btn = page.locator("#install-btn")
        style = btn.get_attribute("style") or ""
        assert "display:none" in style.replace(" ", "")


class TestHomePageFooter:
    """Verify footer content on the home page."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_footer_exists(self, page):
        should_exist(page, ".footer")

    def test_footer_logo(self, page):
        """Footer contains light and dark logo images."""
        logos = page.locator(".footer-logo")
        assert logos.count() == 2

    def test_footer_scripture(self, page):
        should_have_text(page, ".scripture", "II Timothy 2:2")

    def test_footer_address(self, page):
        should_have_text(page, ".address", "Asansol")

    def test_footer_logo_link_external(self, page):
        link = page.locator("a.footer_logo_link")
        assert link.get_attribute("target") == "_blank"
        assert link.get_attribute("rel") == "noopener noreferrer"


class TestHomePageMeta:
    """Verify HTML metadata on the home page."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_viewport_meta(self, page):
        meta = page.locator('meta[name="viewport"]')
        content = meta.get_attribute("content") or ""
        assert "width=device-width" in content

    def test_charset_meta(self, page):
        meta = page.locator('meta[charset]')
        assert meta.get_attribute("charset") == "UTF-8"

    def test_theme_color_meta(self, page):
        meta = page.locator('meta[name="theme-color"]')
        assert meta.get_attribute("content") == "#e89a1c"

    def test_manifest_link(self, page):
        link = page.locator('link[rel="manifest"]')
        assert link.get_attribute("href").endswith("/manifest.json")

    def test_csp_header(self, page):
        meta = page.locator('meta[http-equiv="Content-Security-Policy"]')
        assert meta.count() > 0
        content = meta.get_attribute("content") or ""
        assert "default-src 'self'" in content

    def test_html_lang_attribute(self, page):
        lang = page.locator("html").get_attribute("lang")
        assert lang == "en"

    def test_apple_touch_icon(self, page):
        link = page.locator('link[rel="apple-touch-icon"]')
        assert link.count() > 0

    def test_apple_webapp_capable(self, page):
        meta = page.locator('meta[name="apple-mobile-web-app-capable"]')
        assert meta.get_attribute("content") == "yes"


class TestHomePageInitialState:
    """Verify initial state of interactive features."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_initial_theme_is_light(self, page):
        from conftest import get_theme
        assert get_theme(page) == "light"

    def test_initial_offline_indicator_hidden(self, page):
        indicator = page.locator("#offline-indicator")
        style = indicator.get_attribute("style") or ""
        assert "display:none" in style.replace(" ", "")
