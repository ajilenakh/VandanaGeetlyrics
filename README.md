# VandanaGeetlyrics

A multilingual church songbook (Bengali, Hindi, English) built with Eleventy.
Optimised for offline use and extreme performance on slow connections.

```bash
pnpm install     # Install dependencies
pnpm start       # Dev server at http://localhost:8080
pnpm build       # Production build → _site/
pnpm clean       # Delete _site/
```

---

## Features

- **Offline-first** — Service worker caches all songs; full songbook works without internet after first visit
- **PWA** — Installable on mobile devices via manifest + service worker
- **Dark/Light theme** — Toggle with persistent preference (localStorage)
- **Font size controls** — Adjustable for accessibility (5 levels, persisted)
- **Client-side search** — Filter songs by number or title across all languages
- **Asset revisioning** — Content-hashed CSS/JS filenames for long-term caching
- **Accessible** — High contrast, ≥32 px touch targets, ARIA labels, no-JS content rendering

## Project Structure

```
src/              # Source: templates, styles, scripts, song content
scripts/          # Build-time scripts (asset revisioning, test server helper)
tests/            # Playwright test suite (283 tests, data-driven)
docs/             # Contributor reference
_site/            # Build output (generated, not tracked)
```

## Quick Start

1. **Install dependencies:** `pnpm install`
2. **Start dev server:** `pnpm start` — opens at `http://localhost:8080`
3. **Build for production:** `pnpm build` — outputs to `_site/`

## Running Tests

```bash
# Prerequisites: Python 3, Playwright (pip install playwright),
# Chromium (playwright install chromium), pytest
./tests/run.sh
```

Run specific tests: `./tests/run.sh -k "search"` or `./tests/run.sh tests/test_home_page.py`

## Documentation

For detailed contributor documentation — adding songs, modifying layouts,
understanding the build process, and writing tests — see
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License

The code (templates, styles, scripts, build configuration, tests) is licensed under
the [GNU General Public License v3](LICENSE).

The song lyrics are sourced from various hymnals. Some are public domain; others
may be subject to copyright held by their respective owners. This project does not
claim ownership of or grant any license to the song lyrics.
