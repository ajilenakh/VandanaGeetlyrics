"""Tests for song search functionality — number, title, partial, no-results.

Uses the known songs from conftest to build data-driven search tests.
"""

import pytest
from conftest import go, SONG_TITLES, lang_page_url


# A minimal, reliable set of song data for search tests
KNOWN_SONG = ("english", "1", "Amazing Grace")


@pytest.fixture
def english_page(page):
    go(page, "/english/")
    return page


class TestSearchByNumber:
    """Searching by song number."""

    def test_search_by_exact_number_shows_match(self, english_page):
        page = english_page
        search = page.locator("#song-search")
        search.fill("1")
        page.wait_for_timeout(200)

        # All visible cards must have "1" in their data-number
        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1
        for i in range(visible.count()):
            num = visible.nth(i).get_attribute("data-number") or ""
            assert "1" in num, f"Card {i} data-number does not contain '1': {num}"

        # Cards without "1" in number must be hidden
        all_cards = page.locator(".song-card")
        for i in range(all_cards.count()):
            num = all_cards.nth(i).get_attribute("data-number") or ""
            if "1" not in num:
                assert not all_cards.nth(i).is_visible(), \
                    f"Card {i} (number={num}) should be hidden when searching '1'"

    def test_search_by_exact_number_hides_non_match(self, english_page):
        page = english_page
        search = page.locator("#song-search")
        search.fill("1")
        page.wait_for_timeout(200)

        # Cards with data-number != "1" should be hidden
        card_3 = page.locator('.song-card[data-number="3"]')
        if card_3.count() > 0:
            assert not card_3.is_visible()

    def test_search_by_non_existent_number_shows_no_results(self, english_page):
        page = english_page
        search = page.locator("#song-search")
        search.fill("999")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() == 0
        no_results = page.locator("#no-results")
        assert no_results.is_visible()
        text = no_results.text_content().lower()
        assert "couldn't find" in text
        assert "different number" in text

    def test_search_by_partial_number(self, english_page):
        """Partial number match works."""
        page = english_page
        search = page.locator("#song-search")
        search.fill("1")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() > 0


class TestSearchByTitle:
    """Searching by song title."""

    def test_search_by_full_title(self, english_page):
        page = english_page
        search = page.locator("#song-search")
        search.fill("Amazing Grace")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1
        title_text = visible.first.locator(".song-card-title").text_content()
        assert "Amazing Grace" in title_text

    def test_search_by_partial_title(self, english_page):
        page = english_page
        search = page.locator("#song-search")
        search.fill("Amazing")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1

    def test_search_case_insensitive(self, english_page):
        page = english_page
        search = page.locator("#song-search")
        search.fill("amazing grace")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1

    def test_search_mixed_case(self, english_page):
        page = english_page
        search = page.locator("#song-search")
        search.fill("AMAZING Grace")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1


class TestSearchBehavior:
    """Search edge cases and behavior."""

    def test_empty_search_shows_all_songs(self, english_page):
        page = english_page
        all_count = page.locator(".song-card").count()

        search = page.locator("#song-search")
        search.fill("1")
        page.wait_for_timeout(200)

        search.fill("")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() == all_count
        assert not page.locator("#no-results").is_visible()

    def test_search_with_special_characters(self, english_page):
        """Special chars shouldn't break the search."""
        page = english_page
        search = page.locator("#song-search")
        search.fill("@#$%^&*()")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() == 0
        assert page.locator("#no-results").is_visible()

    def test_no_results_hides_when_results_found(self, english_page):
        page = english_page
        search = page.locator("#song-search")

        search.fill("999")
        page.wait_for_timeout(200)
        assert page.locator("#no-results").is_visible()

        search.fill("1")
        page.wait_for_timeout(200)
        assert not page.locator("#no-results").is_visible()

    def test_search_clears_between_languages(self, page):
        """Navigating between languages resets search state."""
        go(page, "/bengali/")
        search = page.locator("#song-search")
        search.fill("যিশু")
        page.wait_for_timeout(200)

        page.locator('a.lang-link[href$="/english/"]').click()
        page.wait_for_load_state("networkidle")

        # English page should show all songs (fresh state)
        # Wait for at least one song card to be visible (search debounce may still be running)
        page.locator(".song-card:visible").first.wait_for(state="visible", timeout=5000)
        total = page.locator(".song-card").count()
        visible = page.locator(".song-card:visible")
        assert visible.count() == total, \
            f"Expected {total} visible cards, got {visible.count()}"


class TestSearchByTitleNonEnglish:
    """Search on Bengali and Hindi pages."""

    def test_hindi_search_by_title(self, page):
        go(page, "/hindi/")
        search = page.locator("#song-search")
        search.fill("हर समय")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1
        title = visible.first.locator(".song-card-title").text_content()
        assert "हर समय" in title

    def test_hindi_search_by_number(self, page):
        go(page, "/hindi/")
        search = page.locator("#song-search")
        search.fill("1")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1

    def test_hindi_no_results(self, page):
        go(page, "/hindi/")
        search = page.locator("#song-search")
        search.fill("xxxxxx")
        page.wait_for_timeout(200)
        assert page.locator("#no-results").is_visible()

    def test_bengali_search_by_title_partial(self, page):
        go(page, "/bengali/")
        search = page.locator("#song-search")
        search.fill("যিশু")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1

    def test_bengali_search_by_number(self, page):
        go(page, "/bengali/")
        search = page.locator("#song-search")
        search.fill("3")
        page.wait_for_timeout(200)

        visible = page.locator(".song-card:visible")
        assert visible.count() >= 1

    def test_bengali_no_results(self, page):
        go(page, "/bengali/")
        search = page.locator("#song-search")
        search.fill("zzzz")
        page.wait_for_timeout(200)
        assert page.locator("#no-results").is_visible()

    def test_no_results_message_text(self, english_page):
        page = english_page
        search = page.locator("#song-search")
        search.fill("zzzzzzz")
        page.wait_for_timeout(200)

        text = page.locator("#no-results").text_content().lower()
        assert "couldn't find" in text
