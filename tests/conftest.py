"""Shared fixtures and helpers for VandanaGeetlyrics tests.

All song data is discovered dynamically — no hardcoded counts or titles.
Tests adapt as the song library grows.
"""

import os
import json
import re
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8080")
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(PROJECT_DIR, "_site")
SRC_DIR = os.path.join(PROJECT_DIR, "src")


# ─── Dynamic Song Data Discovery ─────────────────────────────


def discover_songs():
    """Read _site/songs.json to discover all song URLs dynamically."""
    songs_path = os.path.join(SITE_DIR, "songs.json")
    if not os.path.exists(songs_path):
        return []
    with open(songs_path) as f:
        return json.load(f)


def discover_songs_by_language():
    """Group song URLs by language: {'bengali': [...], 'hindi': [...], 'english': [...]}."""
    songs = discover_songs()
    grouped = {}
    for url in songs:
        parts = url.strip("/").split("/")
        lang = parts[0]
        if lang not in grouped:
            grouped[lang] = []
        grouped[lang].append(url)
    return grouped


def get_song_titles_from_source():
    """Extract song titles from source frontmatter for all languages.
    
    Returns: { 'bengali': [(1, 'Title'), ...], 'hindi': [...], 'english': [...] }
    """
    titles = {}
    for lang in ["bengali", "hindi", "english"]:
        lang_dir = os.path.join(SRC_DIR, lang)
        lang_songs = []
        if os.path.isdir(lang_dir):
            for fname in sorted(os.listdir(lang_dir)):
                if fname.endswith(".md"):
                    fpath = os.path.join(lang_dir, fname)
                    number = os.path.splitext(fname)[0]
                    title = extract_frontmatter_title(fpath)
                    lang_songs.append((number, title))
        titles[lang] = lang_songs
    return titles


def extract_frontmatter_title(filepath):
    """Extract 'title' field from YAML frontmatter of a markdown file."""
    title_pattern = re.compile(r"^title:\s*\"?(.+?)\"?\s*$", re.MULTILINE)
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        match = title_pattern.search(content)
        if match:
            return match.group(1).strip().strip('"')
    except (IOError, OSError):
        pass
    return None


# ── Shared test data ──────────────────────────────────────────

SONGS = discover_songs()
SONGS_BY_LANG = discover_songs_by_language()
SONG_TITLES = get_song_titles_from_source()


# ── Pytest Fixtures ───────────────────────────────────────────


@pytest.fixture(scope="session")
def browser():
    """Launch chromium headless browser session."""
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture(scope="session")
def browser_context(browser):
    """Create a shared browser context for all tests.

    Using a session-scoped context avoids resource exhaustion from
    creating hundreds of contexts. Each test gets its own page within
    this context.
    """
    context = browser.new_context(
        viewport={"width": 375, "height": 812},
        user_agent=(
            "Mozilla/5.0 (Linux; Android 12; Pixel 6) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Mobile Safari/537.36"
        ),
        # No init scripts — let tests set their own localStorage state
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(browser_context):
    """Create a new page in the shared context.

    Before each test, we close any leftover pages and open a fresh one,
    then clear storage so tests start with a clean slate.
    """
    # Close any pages left open by previous tests
    for p in browser_context.pages:
        p.close()

    new_page = browser_context.new_page()
    # Clear storage so each test starts clean
    new_page.goto(f"{BASE_URL}/", wait_until="domcontentloaded")
    new_page.evaluate("localStorage.clear(); sessionStorage.clear()")
    yield new_page
    if not new_page.is_closed():
        new_page.close()


# ── Navigation Helpers ────────────────────────────────────────


def go(page, path=""):
    """Navigate to a path relative to BASE_URL and wait for network idle."""
    url = f"{BASE_URL}{path}"
    page.goto(url, wait_until="networkidle")


# ── Assertion Helpers ─────────────────────────────────────────


def should_have_text(page, selector, expected_text):
    """Assert that element has expected text."""
    el = page.locator(selector)
    assert el.is_visible(), f"Element '{selector}' not visible"
    actual = el.text_content() or ""
    assert expected_text in actual, (
        f"Expected '{expected_text}' in '{selector}', "
        f"got: '{actual[:100]}'"
    )


def should_have_count(page, selector, expected_count):
    """Assert that exactly N elements match the selector."""
    count = page.locator(selector).count()
    assert count == expected_count, (
        f"Expected {expected_count} elements for '{selector}', got {count}"
    )


def should_exist(page, selector):
    """Assert that at least one element matches the selector."""
    el = page.locator(selector)
    assert el.count() > 0, f"Expected element '{selector}' to exist, not found"


def should_not_exist(page, selector):
    """Assert that no element matches the selector."""
    count = page.locator(selector).count()
    assert count == 0, (
        f"Expected no element '{selector}', but found {count}"
    )


def get_theme(page):
    """Get current theme from data-theme attribute."""
    return page.evaluate(
        'document.documentElement.getAttribute("data-theme")'
    )


def get_font_size(page):
    """Get current base font size from CSS variable."""
    return page.evaluate(
        'getComputedStyle(document.documentElement)'
        '.getPropertyValue("--base-font-size").trim()'
    )


def get_local_storage(page, key):
    """Get a value from localStorage."""
    return page.evaluate(f"localStorage.getItem('{key}')")


def set_local_storage(page, key, value):
    """Set a value in localStorage."""
    page.evaluate(f"localStorage.setItem('{key}', '{value}')")


def song_url_for(lang, number):
    """Build a song detail URL for the given language and number."""
    return f"/{lang}/{number}/"


def lang_page_url(lang):
    """Build a language listing page URL."""
    return f"/{lang}/"
