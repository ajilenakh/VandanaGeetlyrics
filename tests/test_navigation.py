"""Tests for navigation — home link, language switcher, song cards, browser nav."""

import pytest
from conftest import go, should_exist, SONG_TITLES, BASE_URL, PATH_PREFIX


class TestHomeLink:
    """Home link navigation."""

    def test_home_link_navigates_to_home(self, page):
        go(page, "/bengali/")
        page.locator('a.home-link[aria-label="Home"]').click()
        page.wait_for_load_state("networkidle")
        # Should end up at the root URL (with any path prefix)
        expected = f"{BASE_URL}{PATH_PREFIX}/".rstrip("/")
        assert page.url.rstrip("/") == expected, \
            f"Expected to be at root ({expected}), got {page.url}"
        # Home page has the language cards
        assert page.locator(".language-card").count() == 3

    def test_home_link_from_song_detail(self, page):
        go(page, "/english/1/")
        page.locator('a.home-link[aria-label="Home"]').click()
        page.wait_for_load_state("networkidle")
        assert page.locator(".language-card").count() == 3

    def test_home_link_from_all_languages(self, page):
        for lang in ["bengali", "hindi", "english"]:
            go(page, f"/{lang}/")
            page.locator('a.home-link[aria-label="Home"]').click()
            page.wait_for_load_state("networkidle")
            assert page.locator(".language-card").count() == 3, \
                f"Home link broken from {lang} page"


class TestLanguageSwitcher:
    """Language switcher navigation."""

    def test_switcher_from_home_to_bengali(self, page):
        go(page, "/")
        page.locator('a.lang-link[href$="/bengali/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/bengali/" in page.url
        assert page.locator(".page-title").text_content().strip() == "বাংলা গান"

    def test_switcher_from_home_to_hindi(self, page):
        go(page, "/")
        page.locator('a.lang-link[href$="/hindi/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/hindi/" in page.url
        assert page.locator(".page-title").text_content().strip() == "हिंदी गीत"

    def test_switcher_from_home_to_english(self, page):
        go(page, "/")
        page.locator('a.lang-link[href$="/english/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/english/" in page.url
        assert page.locator(".page-title").text_content().strip() == "English Songs"

    def test_switcher_between_languages(self, page):
        """Navigate between all three languages."""
        go(page, "/bengali/")
        page.locator('a.lang-link[href$="/hindi/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/hindi/" in page.url

        page.locator('a.lang-link[href$="/english/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/english/" in page.url

        page.locator('a.lang-link[href$="/bengali/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/bengali/" in page.url

    def test_switcher_from_song_detail(self, page):
        go(page, "/english/1/")
        page.locator('a.lang-link[href$="/bengali/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/bengali/" in page.url
        should_exist(page, "#song-grid")


class TestLanguageCardNavigation:
    """Language cards on home page navigate correctly."""

    def test_bengali_card_navigates(self, page):
        go(page, "/")
        page.locator('a.language-card[href$="/bengali/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/bengali/" in page.url

    def test_hindi_card_navigates(self, page):
        go(page, "/")
        page.locator('a.language-card[href$="/hindi/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/hindi/" in page.url

    def test_english_card_navigates(self, page):
        go(page, "/")
        page.locator('a.language-card[href$="/english/"]').click()
        page.wait_for_load_state("networkidle")
        assert "/english/" in page.url


class TestSongCardNavigation:
    """Song card navigation to detail page."""

    def test_english_song_card_navigates_to_detail(self, page):
        go(page, "/english/")
        first_card = page.locator(".song-card").first
        href = first_card.get_attribute("href") or ""
        first_card.click()
        page.wait_for_load_state("networkidle")
        assert page.url.rstrip("/").endswith(href.rstrip("/"))
        should_exist(page, ".song-detail")

    def test_bengali_song_card_navigates_to_detail(self, page):
        go(page, "/bengali/")
        first_card = page.locator(".song-card").first
        href = first_card.get_attribute("href") or ""
        first_card.click()
        page.wait_for_load_state("networkidle")
        assert page.url.rstrip("/").endswith(href.rstrip("/"))
        should_exist(page, ".song-detail")

    def test_hindi_song_card_navigates_to_detail(self, page):
        go(page, "/hindi/")
        first_card = page.locator(".song-card").first
        href = first_card.get_attribute("href") or ""
        first_card.click()
        page.wait_for_load_state("networkidle")
        assert page.url.rstrip("/").endswith(href.rstrip("/"))
        should_exist(page, ".song-detail")


class TestBrowserNavigation:
    """Browser back/forward buttons."""

    def test_browser_back_from_detail(self, page):
        go(page, "/english/")
        first_card = page.locator(".song-card").first
        first_card.click()
        page.wait_for_load_state("networkidle")

        page.go_back()
        page.wait_for_load_state("networkidle")
        assert "/english/" in page.url
        should_exist(page, "#song-grid")

    def test_browser_forward_to_detail(self, page):
        go(page, "/english/")
        first_card = page.locator(".song-card").first
        href = first_card.get_attribute("href") or ""
        first_card.click()
        page.wait_for_load_state("networkidle")

        page.go_back()
        page.wait_for_load_state("networkidle")

        page.go_forward()
        page.wait_for_load_state("networkidle")
        assert page.url.rstrip("/").endswith(href.rstrip("/"))
        should_exist(page, ".song-detail")

    def test_browser_back_from_language_to_home(self, page):
        go(page, "/")
        page.locator('a.lang-link[href$="/bengali/"]').click()
        page.wait_for_load_state("networkidle")

        page.go_back()
        page.wait_for_load_state("networkidle")
        assert page.locator(".language-card").count() == 3


class TestHomeCardNavigation:
    """Clicking language cards from home page."""

    def test_all_cards_clickable_from_home(self, page):
        """Every language card on the home page is clickable."""
        go(page, "/")
        cards = page.locator(".language-card")
        for i in range(cards.count()):
            cards.nth(i).click()
            page.wait_for_load_state("networkidle")
            assert page.locator(".language-page").count() > 0 or \
                   page.locator(".song-detail").count() > 0 or \
                   page.locator(".home-logo-wrapper").count() > 0
            go(page, "/")  # back to home for next click
