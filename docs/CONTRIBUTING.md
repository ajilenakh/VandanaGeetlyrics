# Contributor Reference

A complete technical reference for developers who want to run, modify, test, and contribute to VandanaGeetlyrics.

---

## 1. Project Overview

**VandanaGeetlyrics** is a multilingual church songbook containing Bengali, Hindi, and English songs. It is built as a static website optimised for:

- **Extreme performance** — Targets slow 2G/3G connections with a strict 50 KB page weight budget
- **Offline access** — Full songbook works without internet after first visit via Service Worker
- **Accessibility** — Designed for users with limited smartphone experience; high contrast, large touch targets, no-jargon labels

### Goals

1. Load instantly on slow connections (LCP ≤ 1.5 s on slow 4G)
2. Work completely offline after initial visit
3. Provide an accessible, jargon-free interface for all users
4. Maintain a minimal, dependency-light codebase

---

## 2. Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Static Site Generator | [Eleventy](https://www.11ty.dev/) | 3.x |
| Template Engine | Nunjucks | (bundled with Eleventy) |
| Package Manager | [pnpm](https://pnpm.io/) | 10.x |
| CSS | Vanilla CSS | — |
| JavaScript | Vanilla JS (ES6+) | — |
| Offline | Service Worker API | — |
| Testing | Python + Playwright + pytest | — |

### Why These Choices

- **Eleventy** — Minimal, flexible, no client-side JavaScript required for rendering
- **pnpm** — Fast, disk-efficient package management
- **Vanilla CSS/JS** — No frameworks means smaller bundles, faster parsing, no version conflicts
- **Service Worker** — Native browser API for offline caching without external dependencies
- **Playwright** — Industry-standard browser automation; tests run against the real built site

---

## 3. Project Structure

```
VandanaGeetlyrics/
├── .eleventy.js             # Eleventy configuration
├── package.json             # Project dependencies and scripts
├── .github/
│   └── test_deploy.yml      # CI workflow: build + Playwright tests + deploy
├── scripts/
│   ├── rev-assets.js        # Post-build asset revisioning (hash CSS/JS)
│   ├── with_server.py       # Test helper: starts server, runs command, cleans up
│   └── test_server.py       # Prefix-aware HTTP server for Playwright tests
├── src/
│   ├── _includes/
│   │   ├── layouts/         # Page templates
│   │   │   ├── base.njk     # HTML shell (theme, meta, CSP, header, footer)
│   │   │   └── song.njk     # Song detail page layout
│   │   └── components/      # Reusable UI blocks
│   │       ├── header.njk   # Navigation, theme toggle, font controls, install button
│   │       └── footer.njk   # Footer with logo and scripture
│   ├── assets/
│   │   ├── icons/           # PWA icons (192 px, 512 px, maskable)
│   │   └── images/          # Logo images (light/dark AVIF variants)
│   ├── css/
│   │   └── styles.css       # All styles with CSS custom properties for theming
│   ├── js/
│   │   ├── app.js.njk       # Theme toggle, font size controls, SW registration, PWA install
│   │   ├── search.js.njk    # Client-side song search by number/title
│   │   └── sw.js.njk        # Service worker (cache-first, offline fallback)
│   ├── manifest.json.njk    # PWA web app manifest (template, dynamic BASE_URL)
│   ├── bengali/             # Bengali song content (Markdown, one file per song)
│   ├── hindi/               # Hindi song content
│   ├── english/             # English song content
│   ├── index.njk            # Home page (language selection cards)
│   ├── bengali.njk          # Bengali song listing page
│   ├── hindi.njk            # Hindi song listing page
│   ├── english.njk          # English song listing page
│   ├── songs.json.njk       # JSON endpoint with all song URLs (for SW precaching)
│   └── offline.njk          # Offline fallback page
├── tests/                   # Playwright test suite (see §8)
│   ├── conftest.py          # Shared fixtures, helpers, dynamic song discovery
│   ├── run.sh               # Test runner: starts server, runs pytest, cleans up
│   ├── test_home_page.py
│   ├── test_language_pages.py
│   ├── test_song_detail.py
│   ├── test_search.py
│   ├── test_theme_toggle.py
│   ├── test_font_size.py
│   ├── test_navigation.py
│   ├── test_pwa_offline.py
│   ├── test_accessibility.py
│   └── test_edge_cases.py
├── docs/
│   └── CONTRIBUTING.md      # This document
└── _site/                   # Build output (generated, not in version control)
```

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/_includes/layouts/` | Page templates (base, song) |
| `src/_includes/components/` | Reusable UI components (header, footer) |
| `src/{bengali,hindi,english}/` | Song content as Markdown files |
| `src/css/` | Stylesheets |
| `src/js/` | JavaScript files |
| `scripts/` | Build-time and test utility scripts |
| `tests/` | Playwright browser test suite |

---

## 4. Development Setup

### Prerequisites

- **Node.js** (compatible with Eleventy 3.x)
- **pnpm** — install via `npm install -g pnpm` or corepack
- **Python 3** — for running tests
- **Playwright + pytest** — for running tests (see §8)

### Install Dependencies

```bash
pnpm install
```

### Available Commands

| Command | Description |
|---------|-------------|
| `pnpm start` | Start dev server with live reload at `http://localhost:8080` |
| `pnpm build` | Production build (outputs to `_site/`, runs asset revisioning) |
| `pnpm build:gh` | Production build for GitHub Pages (`BASE_URL=/VandanaGeetlyrics`) |
| `pnpm clean` | Delete `_site/` directory |

### Running Locally

```bash
pnpm start
```

Open `http://localhost:8080` in your browser. The dev server watches for file changes and rebuilds automatically.

### Building for Production

```bash
# Local (paths use /)
pnpm build

# GitHub Pages (paths use /VandanaGeetlyrics/)
pnpm build:gh
```

Build generates the static site in `_site/` and runs the asset revisioning script to hash CSS/JS filenames. Use `build:gh` when deploying to GitHub Pages — it sets `BASE_URL=/VandanaGeetlyrics` so all paths are prefixed correctly.

---

## 5. Adding Content

### Adding a New Song

1. Create a new Markdown file in the appropriate language directory:
   - `src/bengali/N.md`
   - `src/hindi/N.md`
   - `src/english/N.md`

2. Add required frontmatter:

```yaml
---
layout: song.njk
title: "Song Title"
number: 1
language: bengali
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `layout` | Yes | Must be `song.njk` |
| `title` | Yes | Song title as displayed |
| `number` | Yes | Unique number within the language |
| `language` | Yes | One of: `bengali`, `hindi`, `english` |

3. Write the song lyrics in Markdown below the frontmatter.

4. Rebuild the site:

```bash
pnpm build
```

5. Run tests to verify nothing broke:

```bash
./tests/run.sh
```

### Song Numbering Rules

- Numbers must be unique within each language
- Numbers determine sort order in language list pages
- No gaps required (e.g., 1, 2, 5 is valid)

### Example Song File

```markdown
---
layout: song.njk
title: "তোমার নাম গান গাই"
number: 1
language: bengali
---

## ১. এস হে করুণাময়

এস হে করুণাময়, বিরাজ হৃদ্যাসনে,  
পূজিতে তোমারে আজি, বাসনা সবার মনে।

### ১

তব দাস-দাসী যত, হইয়াছি সমবেত,  
তৃপ্ত কর সবে পিতা, মনোমত আশিষদানে।

— ঈশানচন্দ্র দাস (১৮৯৪)
```

---

## 6. Making Changes

### Modifying Layouts

Layouts are Nunjucks templates in `src/_includes/layouts/`.

- **base.njk** — Contains the HTML `<head>`, critical CSS, theme detection script, header/footer includes
- **song.njk** — Wraps individual song content with song number and title

### Modifying Components

Components in `src/_includes/components/`:

- **header.njk** — Contains the home link, theme toggle, font size controls, language switcher, and PWA install button
- **footer.njk** — Contains the footer logo and scripture text

### Modifying Styles

All styles are in `src/css/styles.css`. The file uses CSS custom properties (variables) for theming:

```css
:root {
  --bg-primary: #f8f4ee;
  --text-primary: #1f1b16;
  --accent: #e89a1c;
  /* ... */
}

[data-theme="dark"] {
  --bg-primary: #080808;
  --text-primary: #f5f1ea;
  --accent: #f0a020;
  /* ... */
}
```

### Modifying JavaScript

| File | Purpose |
|------|---------|
| `src/js/app.js.njk` | Template: theme toggle, font size controls, service worker registration, PWA install |
| `src/js/search.js.njk` | Template: client-side search for song list pages |
| `src/sw.js.njk` | Template: service worker for offline caching and navigation fallback |

### Adding a New Language

To add a new language (e.g., Tamil):

1. Create `src/tamil/` directory
2. Add collection in `.eleventy.js`:

```javascript
eleventyConfig.addCollection("tamil", function (collection) {
  return collection
    .getFilteredByGlob("src/tamil/*.md")
    .sort(function (a, b) {
      return a.data.number - b.data.number;
    });
});
```

3. Create `src/tamil.njk` list page (copy from `bengali.njk`)
4. Add language to `src/songs.json.njk`
5. Add language link in `header.njk`

---

## 7. Build Process

### What Happens During `pnpm build`

1. **Eleventy compiles** all templates and Markdown files to HTML in `_site/`
   - If `BASE_URL` env var is set (e.g., `/VandanaGeetlyrics`), all paths get that prefix
2. **Passthrough copy** copies CSS and assets to `_site/`
3. **Asset revisioning** (`scripts/rev-assets.js`) runs:
   - Hashes CSS and JS files using MD5 (first 8 characters)
   - Renames files: `styles.css` → `styles.abc12345.css`
   - Updates all HTML references to use the new hashed filenames

### Asset Revisioning Details

The revisioning script:
- Skips already-hashed files
- Is prefix-aware: respects `BASE_URL` env var for GitHub Pages builds
- Updates `href` and `src` attributes in all HTML files
- Prints a summary of renamed assets

### Output Structure

```
_site/
├── css/
│   └── styles.abc12345.css    # Hashed filename
├── js/
│   ├── app.abc12345.js        # Hashed filename
│   ├── search.abc12345.js     # Hashed filename
│   └── sw.js                  # Service worker (generated from template)
├── assets/
│   ├── icons/
│   └── images/
├── bengali/
│   ├── 1/
│   │   └── index.html
│   └── index.html
├── hindi/
├── english/
├── index.html
├── offline.html
└── songs.json
```

---

## 8. Testing

The project includes a comprehensive Playwright test suite (283 tests, all data-driven) that runs against the built site served over HTTP.

### Test Categories

| File | Tests | What It Covers |
|------|-------|----------------|
| `test_home_page.py` | 31 | Title, subtitle, logo, language cards, header, footer, meta tags, CSP, PWA meta |
| `test_language_pages.py` | 57 | All language listing pages: song counts, card structure, data attributes, sorting, aria-current |
| `test_song_detail.py` | 48 | All song detail pages: number badge, title, lyrics content, app.js loading |
| `test_search.py` | 19 | Search by number/title (exact, partial, case-insensitive), no-results, cross-language |
| `test_theme_toggle.py` | 17 | Light→dark→light toggle, localStorage persistence, reload persistence, CSS variable switching |
| `test_font_size.py` | 17 | Increase/decrease/reset, bounds clamping (tiny↔extra_large), persistence |
| `test_navigation.py` | 18 | Home link, language switcher, song cards, browser back/forward |
| `test_pwa_offline.py` | 22 | manifest.json content, offline page, SW registration, CSP, PWA meta tags |
| `test_accessibility.py` | 18 | ARIA labels, aria-current, touch targets, semantic HTML landmarks, keyboard focus, colour contrast |
| `test_edge_cases.py` | 26 | 404 errors, empty searches, special characters/emoji, no-JS rendering, 7 viewport sizes, page weight budget |

### Prerequisites

```bash
pip install playwright pytest
playwright install chromium
```

### Running the Full Suite

```bash
./tests/run.sh
```

This starts a local HTTP server serving `_site/`, runs all tests, then stops the server.

### Running Specific Tests

```bash
# By test name (keyword match)
./tests/run.sh -k "search"

# By file
./tests/run.sh tests/test_theme_toggle.py

# By class
./tests/run.sh -k "TestThemePersistence"

# Stop on first failure
./tests/run.sh -x
```

### How the Test Runner Works

The runner (`tests/run.sh`) uses `scripts/with_server.py` to:

1. Launch `scripts/test_server.py` (a prefix-aware HTTP server) on port 8080, serving `_site/`
2. Wait for the server to be ready
3. Run `python -m pytest tests/` against `http://localhost:8080`
4. Stop the server after tests finish (even on failure)

The `test_server.py` server auto-detects the `pathPrefix` from the built site (e.g., `/VandanaGeetlyrics` for GitHub Pages) so tests pass against both local and prefixed builds.

This means tests run against the **real built HTML**, not against a dev server with hot-reload. Always run `pnpm build` before testing.

### Test Architecture

**Data-driven by design:** All song data is discovered dynamically from `_site/songs.json` and the source Markdown files. No song counts or titles are hardcoded — tests adapt as the song library grows.

```python
# conftest.py discovers songs automatically:
SONGS = discover_songs()           # ["/bengali/1/", ...]
SONGS_BY_LANG = discover_songs_by_language()  # {"bengali": [...], ...}
SONG_TITLES = get_song_titles_from_source()   # {"bengali": [("1", "Title"), ...], ...}
```

Tests use these global dictionaries to parametrize assertions:

```python
@pytest.mark.parametrize("lang,number,expected_title", get_all_song_params())
def test_song_number_badge(self, page, lang, number, expected_title):
    go(page, song_url_for(lang, number))
    badge = page.locator(".song-number")
    assert f"#{number}" == badge.text_content().strip()
```

**Shared browser context:** All tests share a single Playwright browser context (session-scoped) to avoid resource exhaustion. Each test function gets its own page within that context, with localStorage/sessionStorage cleared between tests.

**Key helpers** (from `tests/conftest.py`):

| Helper | Purpose |
|--------|---------|
| `go(page, path)` | Navigate to a path and wait for `networkidle` |
| `should_have_text(page, sel, text)` | Assert element contains text |
| `should_have_count(page, sel, n)` | Assert exactly N elements match |
| `should_exist(page, sel)` | Assert at least one element matches |
| `get_theme(page)` | Read `data-theme` attribute |
| `get_font_size(page)` | Read `--base-font-size` CSS variable |
| `get_local_storage(page, key)` | Read localStorage value |

### Writing New Tests

1. **Create a test file** in `tests/` named `test_<feature>.py`
2. **Use the shared fixtures** from `conftest.py`:
   - `page` — a Playwright page connected to the test server at `BASE_URL`
3. **Use `go()` to navigate**, then interact and assert
4. **Use data from conftest** (`SONGS`, `SONG_TITLES`, etc.) when testing song content
5. **Run `./tests/run.sh -k "your_test"`** to verify before submitting

**Patterns:**

```python
# Structural test
def test_header_has_home_link(self, page):
    go(page, "/")
    link = page.locator('a.home-link[aria-label="Home"]')
    assert link.is_visible()

# Interactive test
def test_toggle_switches_to_dark(self, page):
    go(page, "/")
    page.locator("#theme-toggle").click()
    assert get_theme(page) == "dark"

# Data-driven test (tests all songs automatically)
@pytest.mark.parametrize("lang,number,title", get_all_song_params())
def test_all_songs_load(self, page, lang, number, title):
    go(page, song_url_for(lang, number))
    assert page.locator(".song-detail").count() > 0
```

### Continuous Integration

A CI workflow (`.github/workflows/test_deploy.yml`) runs on every push to `dev` or `master` and on pull requests to `master`:

1. Checkout repository
2. Install Node.js + pnpm dependencies
3. Build the site with `pnpm build` (with `BASE_URL=/VandanaGeetlyrics`)
4. Install Playwright browsers
5. Run `./tests/run.sh`
6. Upload the built site as an artifact
7. If on `master` branch, deploy to GitHub Pages via `upload-pages-artifact` + `deploy-pages`

---

## 9. Performance Guidelines

These are non-negotiable requirements. Treat any violation as a bug.

### Asset Budget

| Metric | Target |
|--------|--------|
| Total page weight (HTML + CSS + JS) | ≤ 50 KB uncompressed |
| Total page weight (gzipped) | ≤ 15 KB gzipped |
| LCP (slow 4G) | ≤ 1.5 seconds |
| TBT (Total Blocking Time) | 0 ms |
| CLS (Cumulative Layout Shift) | 0 |

### Rules

- **No render-blocking scripts** — All `<script>` tags must use `defer` or `async`
- **No external web fonts** — Use system font stack: `font-family: system-ui, sans-serif`
- **No CSS frameworks** — Hand-write only the styles actually used
- **No JavaScript frameworks** — Vanilla JS only, and only when unavoidable
- **Lazy-load images** — Use `loading="lazy"`, provide `width` and `height` attributes
- **Inline critical CSS** — Critical styles are inlined directly in `base.njk` `<style>` block

### Critical CSS

The following is inlined in `base.njk`:
- CSS custom properties (variables)
- Reset styles
- Header layout
- Container base styles

This ensures above-the-fold content renders before external stylesheets load.

### Testing Performance

Use Chrome DevTools Lighthouse:
1. Open DevTools → Lighthouse tab
2. Select "Mobile"
3. Select "Slow 4G" throttling
4. Run audit

Target: Performance score ≥ 95

---

## 10. PWA & Offline

### Service Worker (`src/js/sw.js`)

The service worker implements a **cache-first** strategy:

1. **Install** — Skips waiting, activates immediately
2. **Activate** — Cleans old caches, enforces 100-entry limit
3. **Fetch** — Returns cached response if available; otherwise fetches from network and caches new responses

### Precache Strategy

- **Base URLs** — Always precached: `/`, `/songs.json`, `/bengali/`, `/hindi/`, `/english/`
- **Dynamic precaching** — On app install, fetches `/songs.json` and precaches all song URLs
- **Navigation fallback** — Returns offline page for failed navigation requests when offline

### PWA Installability

The site includes:
- `src/manifest.json` — App name, icons, theme color, display mode
- Meta tags in `base.njk` — `mobile-web-app-capable`, `apple-mobile-web-app-capable`
- Install button in `header.njk` — Shows on Android when `beforeinstallprompt` fires
- iOS manual instructions — Shows "Share → Add to Home Screen" hint on iOS (auto-hides after 8 s)

### Updating the Service Worker

When you modify `sw.js`:
1. Increment `CACHE_NAME` in `sw.js` (e.g., `vandana-geet-v1` → `vandana-geet-v2`)
2. The new service worker will install and activate automatically
3. Old cache will be cleaned on next activation

---

## 11. Submitting Changes

### Git Workflow

1. **Create a branch** for your changes:

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** following the guidelines in this document

3. **Build and test locally**:

```bash
pnpm build
./tests/run.sh
```

4. **Stage and commit**:

```bash
git add .
git commit -m "description of your changes"
```

5. **Push and create PR**:

```bash
git push origin feature/your-feature-name
# Then create a pull request via GitHub UI
```

### Commit Message Style

Use clear, concise messages that explain **why** the change was made:

```
Add new Bengali song #42

- Created src/bengali/42.md with song lyrics
- Added required frontmatter (layout, title, number, language)
```

### What to Include in PRs

- Description of what changed and why
- Screenshots for UI changes
- Confirmation that performance targets are still met
- Confirmation that tests pass

### Testing Checklist

Before submitting a PR, verify:

- [ ] `pnpm build` completes without errors
- [ ] `./tests/run.sh` passes (all 283 tests)
- [ ] Site loads at `http://localhost:8080`
- [ ] New songs appear in the correct language list
- [ ] Theme toggle works (light/dark)
- [ ] Offline mode works (disconnect network, reload page)
- [ ] No console errors
- [ ] Page weight ≤ 50 KB uncompressed (verified by tests)

---

## Quick Reference

| Task | Command |
|------|---------|
| Install dependencies | `pnpm install` |
| Dev server | `pnpm start` |
| Production build | `pnpm build` |
| GitHub Pages build | `pnpm build:gh` |
| Clean output | `pnpm clean` |
| Run all tests | `./tests/run.sh` |
| Run specific tests | `./tests/run.sh -k "search"` |
| Install test deps | `pip install playwright pytest && playwright install chromium` |
| Add song | Create `src/{lang}/N.md` with frontmatter |
| Modify styles | Edit `src/css/styles.css` |
| Modify layout | Edit `src/_includes/layouts/*.njk` |
| Modify JS | Edit `src/js/*.js.njk` |

---

## Questions?

If you need clarification on any part of this reference, open an issue on the repository or ask in the pull request discussion.
