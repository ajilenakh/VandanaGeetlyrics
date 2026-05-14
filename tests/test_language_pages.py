"""Tests for language listing pages — Bengali, Hindi, English song grids.

All counts and content are data-driven — they adapt as songs are added/removed.
"""

import pytest
from conftest import (
    go, should_have_text, should_have_count, should_exist,
    SONGS_BY_LANG, SONG_TITLES, lang_page_url
)

# Map language to page info for parametrized tests
LANGUAGE_PAGES = [
    ("/bengali/", "বাংলা গান", "bengali"),
    ("/hindi/", "हिंदी गीत", "hindi"),
    ("/english/", "English Songs", "english"),
]


class TestLanguagePageStructure:
    """Verify structure common to all language pages."""

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_page_title(self, page, path, title, lang):
        go(page, path)
        assert title in page.title()

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_page_heading(self, page, path, title, lang):
        go(page, path)
        should_have_text(page, ".page-title", title)

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_search_input_present(self, page, path, title, lang):
        go(page, path)
        search = page.locator("#song-search")
        assert search.is_visible()
        assert search.get_attribute("aria-label") == "Search songs"

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_song_grid_present(self, page, path, title, lang):
        go(page, path)
        should_exist(page, "#song-grid")

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_no_results_hidden_by_default(self, page, path, title, lang):
        go(page, path)
        no_results = page.locator("#no-results")
        style = no_results.get_attribute("style") or ""
        assert "display:none" in style.replace(" ", "")

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_search_has_placeholder(self, page, path, title, lang):
        go(page, path)
        placeholder = page.locator("#song-search").get_attribute("placeholder") or ""
        assert len(placeholder) > 0

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_has_lang_page_class(self, page, path, title, lang):
        go(page, path)
        should_exist(page, ".language-page")

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_search_script_loaded(self, page, path, title, lang):
        go(page, path)
        script = page.locator('script[src*="search"]')
        assert script.count() > 0

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_song_count_matches_source(self, page, path, title, lang):
        """Number of song cards = number of songs in the source for that language."""
        go(page, path)
        expected_count = len(SONG_TITLES.get(lang, []))
        actual_count = page.locator(".song-card").count()
        assert actual_count == expected_count, (
            f"{lang}: expected {expected_count} song cards, got {actual_count}"
        )


class TestSongCardsDataDriven:
    """Verify song cards have correct structure using dynamic data."""

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_all_song_cards_have_numbers_and_titles(self, page, path, title, lang):
        """Every song card has a number badge and a title."""
        go(page, path)
        cards = page.locator(".song-card")
        count = cards.count()
        assert count > 0, f"No song cards found for {lang}"
        for i in range(count):
            card = cards.nth(i)
            number = card.locator(".song-card-number")
            assert number.is_visible(), f"Card {i} in {lang} missing number"
            title_el = card.locator(".song-card-title")
            assert title_el.is_visible(), f"Card {i} in {lang} missing title"

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_all_song_cards_have_arrows(self, page, path, title, lang):
        """Every song card has an arrow icon."""
        go(page, path)
        cards = page.locator(".song-card")
        count = cards.count()
        for i in range(count):
            assert cards.nth(i).locator("svg.song-card-arrow").count() > 0, \
                f"Card {i} in {lang} missing arrow icon"

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_song_cards_link_to_detail(self, page, path, title, lang):
        """Each song card links to the correct detail page."""
        go(page, path)
        cards = page.locator(".song-card")
        count = cards.count()
        for lang_slug, songs in SONG_TITLES.items():
            if lang_slug == lang:
                for i, (number, _) in enumerate(songs):
                    if i < count:
                        href = cards.nth(i).get_attribute("href") or ""
                        assert f"/{lang}/{number}/" in href, \
                            f"Card {i} in {lang} should link to /{lang}/{number}/"

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_song_cards_data_attributes(self, page, path, title, lang):
        """Song cards have data-number and data-title attributes for search."""
        go(page, path)
        cards = page.locator(".song-card")
        count = cards.count()
        for i in range(count):
            card = cards.nth(i)
            data_number = card.get_attribute("data-number")
            data_title = card.get_attribute("data-title")
            assert data_number is not None, f"Card {i} in {lang} missing data-number"
            assert data_title is not None, f"Card {i} in {lang} missing data-title"
            assert data_number.isdigit(), f"data-number should be a digit, got '{data_number}'"

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_songs_sorted_by_number(self, page, path, title, lang):
        """Songs appear sorted by number ascending."""
        go(page, path)
        cards = page.locator(".song-card")
        count = cards.count()
        numbers = []
        for i in range(count):
            num = cards.nth(i).get_attribute("data-number") or "0"
            numbers.append(int(num))
        assert numbers == sorted(numbers), \
            f"Songs in {lang} not sorted by number: {numbers}"


class TestLanguageSpecific:
    """Language-specific content checks using dynamic data."""

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_current_lang_highlighted(self, page, path, title, lang):
        """Active language link has aria-current='page'."""
        go(page, path)
        lang_link = page.locator(f'a.lang-link[href="/{lang}/"]')
        assert lang_link.get_attribute("aria-current") == "page"

    @pytest.mark.parametrize("path,title,lang", LANGUAGE_PAGES)
    def test_known_song_titles_present(self, page, path, title, lang):
        """All song titles from source appear in the song cards."""
        go(page, path)
        card_titles = page.locator(".song-card-title")
        actual_titles = [card_titles.nth(i).text_content().strip()
                         for i in range(card_titles.count())]
        for number, expected_title in SONG_TITLES.get(lang, []):
            if expected_title:
                assert expected_title in actual_titles, (
                    f"'{expected_title}' not found in {lang} page song cards. "
                    f"Actual: {actual_titles}"
                )

    def test_bengali_search_placeholder(self, page):
        go(page, "/bengali/")
        placeholder = page.locator("#song-search").get_attribute("placeholder") or ""
        assert "নম্বর" in placeholder

    def test_hindi_search_placeholder(self, page):
        go(page, "/hindi/")
        placeholder = page.locator("#song-search").get_attribute("placeholder") or ""
        assert "नंबर" in placeholder

    def test_english_search_placeholder(self, page):
        go(page, "/english/")
        placeholder = page.locator("#song-search").get_attribute("placeholder") or ""
        assert "number or title" in placeholder.lower()
