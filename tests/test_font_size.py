"""Tests for font size controls — increase, decrease, reset, persistence, bounds."""

import pytest
from conftest import go, get_font_size, get_local_storage


FONT_SIZES_MAP = {
    "tiny": "14px",
    "small": "16px",
    "medium": "18px",
    "large": "20px",
    "extra_large": "22px",
}


class TestFontSizeInitial:
    """Verify default font size state."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_default_font_size(self, page):
        assert get_font_size(page) == "18px"  # medium

    def test_default_font_size_in_local_storage(self, page):
        stored = get_local_storage(page, "fontSize")
        assert stored is None  # no preference saved until user clicks a button


class TestFontSizeIncrease:
    """Font size increase button."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_increase_once(self, page):
        page.locator("#font-increase").click()
        page.wait_for_timeout(100)
        assert get_font_size(page) == "20px"  # medium → large

    def test_increase_twice(self, page):
        page.locator("#font-increase").click()
        page.locator("#font-increase").click()
        page.wait_for_timeout(100)
        assert get_font_size(page) == "22px"  # medium → large → extra_large

    def test_increase_beyond_max_stays_at_max(self, page):
        """Can't increase beyond extra_large."""
        for _ in range(5):
            page.locator("#font-increase").click()
        page.wait_for_timeout(100)
        assert get_font_size(page) == "22px"  # extra_large is max

    def test_increase_persists_in_storage(self, page):
        page.locator("#font-increase").click()
        stored = get_local_storage(page, "fontSize")
        assert stored == "large"


class TestFontSizeDecrease:
    """Font size decrease button."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_decrease_once(self, page):
        page.locator("#font-decrease").click()
        page.wait_for_timeout(100)
        assert get_font_size(page) == "16px"  # medium → small

    def test_decrease_twice(self, page):
        page.locator("#font-decrease").click()
        page.locator("#font-decrease").click()
        page.wait_for_timeout(100)
        assert get_font_size(page) == "14px"  # medium → small → tiny

    def test_decrease_beyond_min_stays_at_min(self, page):
        """Can't decrease below tiny."""
        for _ in range(5):
            page.locator("#font-decrease").click()
        page.wait_for_timeout(100)
        assert get_font_size(page) == "14px"  # tiny is min

    def test_decrease_persists_in_storage(self, page):
        page.locator("#font-decrease").click()
        stored = get_local_storage(page, "fontSize")
        assert stored == "small"


class TestFontSizeReset:
    """Font size reset button."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_reset_after_increase(self, page):
        page.locator("#font-increase").click()
        page.locator("#font-increase").click()
        page.locator("#font-reset").click()
        page.wait_for_timeout(100)
        assert get_font_size(page) == "18px"  # back to medium

    def test_reset_after_decrease(self, page):
        page.locator("#font-decrease").click()
        page.locator("#font-decrease").click()
        page.locator("#font-reset").click()
        page.wait_for_timeout(100)
        assert get_font_size(page) == "18px"  # back to medium

    def test_reset_clears_storage_to_medium(self, page):
        page.locator("#font-increase").click()
        page.locator("#font-reset").click()
        stored = get_local_storage(page, "fontSize")
        assert stored == "medium"


class TestFontSizePersistence:
    """Font size persists across page reloads."""

    def test_size_persists_after_reload(self, page):
        go(page, "/")
        page.locator("#font-increase").click()
        page.locator("#font-increase").click()
        assert get_font_size(page) == "22px"

        page.reload(wait_until="networkidle")
        page.wait_for_timeout(100)
        assert get_font_size(page) == "22px"

    def test_size_persists_across_navigation(self, page):
        go(page, "/")
        page.locator("#font-increase").click()

        page.locator('a.lang-link[href="/bengali/"]').click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(100)
        assert get_font_size(page) == "20px"

    def test_size_persists_on_song_detail(self, page):
        go(page, "/")
        page.locator("#font-decrease").click()

        page.locator('a.lang-link[href="/english/"]').click()
        page.wait_for_load_state("networkidle")

        song_card = page.locator(".song-card").first
        if song_card.count() > 0:
            song_card.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(100)
            assert get_font_size(page) == "16px"


class TestFontSizeAccessibility:
    """Font control accessibility."""

    @pytest.fixture(autouse=True)
    def load_page(self, page):
        go(page, "/")

    def test_increase_button_aria_label(self, page):
        btn = page.locator("#font-increase")
        assert btn.get_attribute("aria-label") == "Increase font size"

    def test_decrease_button_aria_label(self, page):
        btn = page.locator("#font-decrease")
        assert btn.get_attribute("aria-label") == "Decrease font size"

    def test_reset_button_aria_label(self, page):
        btn = page.locator("#font-reset")
        assert btn.get_attribute("aria-label") == "Reset font size"

    def test_increase_and_decrease_directions(self, page):
        """Increase then decrease should return to original size."""
        page.locator("#font-increase").click()
        page.locator("#font-decrease").click()
        page.wait_for_timeout(100)
        assert get_font_size(page) == "18px"  # medium
