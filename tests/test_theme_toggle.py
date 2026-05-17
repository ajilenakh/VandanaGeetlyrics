"""Tests for theme toggle functionality — dark/light mode, localStorage persistence."""

import pytest
from conftest import go, get_theme, get_local_storage


class TestThemeToggle:
    """Verify theme toggling works correctly."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_initial_theme_is_light(self, page):
        assert get_theme(page) == "light"

    def test_theme_toggle_switches_to_dark(self, page):
        page.locator("#theme-toggle").click()
        assert get_theme(page) == "dark"

    def test_theme_toggle_switches_back_to_light(self, page):
        page.locator("#theme-toggle").click()  # → dark
        page.locator("#theme-toggle").click()  # → light
        assert get_theme(page) == "light"

    def test_theme_persists_in_local_storage(self, page):
        page.locator("#theme-toggle").click()
        stored = get_local_storage(page, "theme")
        assert stored == "dark"

    def test_light_theme_in_local_storage(self, page):
        # Start with dark
        page.locator("#theme-toggle").click()
        # Toggle back to light
        page.locator("#theme-toggle").click()
        stored = get_local_storage(page, "theme")
        assert stored == "light"

    def test_theme_color_meta_initial_light(self, page):
        """Theme-color meta starts at light-mode accent color."""
        meta = page.locator('meta[name="theme-color"]')
        assert meta.get_attribute("content") == "#e89a1c"

    def test_theme_color_meta_updates_on_dark_reload(self, page):
        """After setting dark mode, reload should show dark accent in meta."""
        from conftest import set_local_storage
        page.evaluate("localStorage.setItem('theme', 'dark')")
        page.reload(wait_until="networkidle")
        meta = page.locator('meta[name="theme-color"]')
        assert meta.get_attribute("content") == "#f0a020"


class TestThemePersistence:
    """Theme persists across page reloads via localStorage."""

    def test_dark_theme_persists_after_reload(self, page):
        go(page, "/")
        page.locator("#theme-toggle").click()
        assert get_theme(page) == "dark"

        page.reload(wait_until="networkidle")
        assert get_theme(page) == "dark"

    def test_dark_theme_persists_across_navigation(self, page):
        go(page, "/")
        page.locator("#theme-toggle").click()

        # Navigate to another page
        page.locator('a.lang-link[href$="/bengali/"]').click()
        page.wait_for_load_state("networkidle")
        assert get_theme(page) == "dark"

        # Navigate to a song
        song_card = page.locator(".song-card").first
        if song_card.count() > 0:
            song_card.click()
            page.wait_for_load_state("networkidle")
            assert get_theme(page) == "dark"

    def test_theme_persists_without_local_storage_default(self, page):
        """When localStorage has no theme set, default is light."""
        go(page, "/")  # fresh navigation with clean localStorage
        page.evaluate("localStorage.removeItem('theme')")
        go(page, "/")  # reload with theme removed
        assert get_theme(page) == "light"

    def test_theme_applied_before_page_renders(self, page):
        """Theme script runs synchronously before paint (inline <script>)."""
        # First navigate so localStorage is accessible
        go(page, "/")
        # Set dark theme in localStorage
        page.evaluate("localStorage.setItem('theme', 'dark')")
        # Navigate fresh — inline script should pick up the stored value
        # before any other JS runs
        go(page, "/")
        theme = page.evaluate(
            'document.documentElement.getAttribute("data-theme")'
        )
        assert theme == "dark"


class TestThemeIcons:
    """Verify sun/moon icon visibility based on theme."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_sun_icon_hidden_in_light_mode(self, page):
        """In light mode, sun icon is hidden, moon is visible."""
        sun = page.locator(".icon-sun")
        moon = page.locator(".icon-moon")
        assert not sun.is_visible()
        assert moon.is_visible()

    def test_moon_icon_hidden_in_dark_mode(self, page):
        page.locator("#theme-toggle").click()
        sun = page.locator(".icon-sun")
        moon = page.locator(".icon-moon")
        assert sun.is_visible()
        assert not moon.is_visible()


class TestThemeCSSVariables:
    """Verify CSS variables update when theme changes."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def get_css_var(self, page, var_name):
        return page.evaluate(
            f'getComputedStyle(document.documentElement)'
            f'.getPropertyValue("{var_name}").trim()'
        )

    def test_bg_color_changes(self, page):
        light_bg = self.get_css_var(page, "--bg-primary")
        page.locator("#theme-toggle").click()
        dark_bg = self.get_css_var(page, "--bg-primary")
        assert light_bg != dark_bg

    def test_accent_color_changes(self, page):
        light_accent = self.get_css_var(page, "--accent")
        page.locator("#theme-toggle").click()
        dark_accent = self.get_css_var(page, "--accent")
        assert light_accent != dark_accent
