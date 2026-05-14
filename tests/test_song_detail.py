"""Tests for song detail pages — number badge, title, lyrics rendering.

All known songs are discovered dynamically from source files.
Tests adapt as the song library grows.
"""

import os
import pytest
from conftest import (
    go, should_exist, SONG_TITLES, SRC_DIR, lang_page_url, song_url_for
)


def get_all_song_params():
    """Build parametrize list: [(lang, number, title), ...] from dynamic data."""
    params = []
    for lang, songs in SONG_TITLES.items():
        for number_str, title in songs:
            params.append((lang, number_str, title))
    return params


SONG_PARAMS = get_all_song_params()


class TestSongDetailDataDriven:
    """Parametrized across all discovered songs."""

    @pytest.mark.parametrize("lang,number,expected_title", SONG_PARAMS)
    def test_song_detail_page_loads(self, page, lang, number, expected_title):
        """Every known song's detail page loads successfully."""
        url = song_url_for(lang, number)
        go(page, url)
        # HTTP status is OK (no error in navigation)
        assert page.locator(".song-detail").count() > 0, \
            f"Song detail container not found for {url}"

    @pytest.mark.parametrize("lang,number,expected_title", SONG_PARAMS)
    def test_song_number_badge(self, page, lang, number, expected_title):
        """Song number is displayed in a badge."""
        url = song_url_for(lang, number)
        go(page, url)
        badge = page.locator(".song-number")
        assert badge.is_visible(), f"Song number badge not visible for {url}"
        badge_text = badge.text_content().strip()
        assert f"#{number}" == badge_text, \
            f"Expected #{number}, got '{badge_text}' for {url}"

    @pytest.mark.parametrize("lang,number,expected_title", SONG_PARAMS)
    def test_song_title_displayed(self, page, lang, number, expected_title):
        """Song title from frontmatter is rendered."""
        url = song_url_for(lang, number)
        go(page, url)
        title_el = page.locator(".song-title")
        assert title_el.is_visible(), f"Song title not visible for {url}"
        actual = title_el.text_content().strip()
        if expected_title:
            assert expected_title == actual, \
                f"Title mismatch for {url}: expected '{expected_title}', got '{actual}'"

    @pytest.mark.parametrize("lang,number,expected_title", SONG_PARAMS)
    def test_song_lyrics_have_content(self, page, lang, number, expected_title):
        """Lyrics section exists and has meaningful content."""
        url = song_url_for(lang, number)
        go(page, url)
        lyrics = page.locator(".song-lyrics")
        assert lyrics.is_visible(), f"Lyrics section not visible for {url}"
        text = lyrics.text_content() or ""
        assert len(text.strip()) > 20, \
            f"Lyrics too short ({len(text.strip())} chars) for {url}: '{text[:50]}...'"

    @pytest.mark.parametrize("lang,number,expected_title", SONG_PARAMS)
    def test_song_info_section(self, page, lang, number, expected_title):
        """Song info section exists (contains number + title)."""
        url = song_url_for(lang, number)
        go(page, url)
        should_exist(page, ".song-info")

    @pytest.mark.parametrize("lang,number,expected_title", SONG_PARAMS)
    def test_body_has_song_page_class(self, page, lang, number, expected_title):
        """Body has correct CSS class for song pages."""
        url = song_url_for(lang, number)
        go(page, url)
        body_class = page.locator("body").get_attribute("class") or ""
        assert "song-page" in body_class, \
            f"Body missing 'song-page' class for {url}"

    @pytest.mark.parametrize("lang,number,expected_title", SONG_PARAMS)
    def no_search_input_on_detail(self, page, lang, number, expected_title):
        """Song detail pages should not have the search input."""
        url = song_url_for(lang, number)
        go(page, url)
        assert page.locator("#song-search").count() == 0, \
            f"Search input found on song detail page {url}"

    @pytest.mark.parametrize("lang,number,expected_title", SONG_PARAMS)
    def test_app_js_loaded(self, page, lang, number, expected_title):
        """Song detail page loads app.js."""
        url = song_url_for(lang, number)
        go(page, url)
        script = page.locator('script[src*="app"]')
        assert script.count() > 0, f"app.js not loaded on {url}"

    @pytest.mark.parametrize("lang,number,expected_title", SONG_PARAMS)
    def test_page_title_includes_church_songbook(self, page, lang, number, expected_title):
        """HTML title includes the site name."""
        url = song_url_for(lang, number)
        go(page, url)
        assert "Church Songbook" in page.title(), \
            f"Page title missing 'Church Songbook' on {url}"


class TestSongDetailNavigation:
    """Navigation from listing to detail and back."""

    def test_click_song_card_goes_to_detail(self, page):
        """Clicking a song card navigates to its detail page."""
        go(page, "/english/")
        first_card = page.locator(".song-card").first
        expected_href = first_card.get_attribute("href") or ""
        first_card.click()
        page.wait_for_load_state("networkidle")
        assert page.url.rstrip("/").endswith(expected_href.rstrip("/"))

    def test_detail_has_header_nav(self, page):
        """Song detail pages still have the header navigation."""
        go(page, "/english/1/")
        assert page.locator(".header").is_visible()
        assert page.locator(".lang-link").count() == 3
