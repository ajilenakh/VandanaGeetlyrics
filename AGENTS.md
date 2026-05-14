# VandanaGeetlyrics

Static site generator for a multilingual church songbook using Eleventy 3.x.

## Build commands

- `pnpm build` — production build (outputs to `_site/`)
- `pnpm start` — dev server with live reload
- `pnpm clean` — delete `_site/`
- `./tests/run.sh` — run 277 Playwright tests against `_site/`

## Architecture

- **Input**: `src/` → **Output**: `_site/`
- **Content**: `src/{bengali,hindi,english}/*.md` — each song file has frontmatter `layout`, `title`, `number`, `language`
- **Layouts**: `src/_includes/layouts/` — `base.njk` (HTML shell), `song.njk` (song detail)
- **Components**: `src/_includes/components/` — header, footer
- **Collections**: Eleventy auto-creates `bengali`, `hindi`, `english` collections sorted by `number`
- **Passthrough**: `src/css/`, `src/js/`, `src/assets/` are copied as-is to `_site/`
- **Asset revisioning**: `scripts/rev-assets.js` post-build script hashes CSS/JS files (e.g., `styles.css` → `styles.abc12345.css`) and updates HTML references
- **Entry pages**: `src/{bengali,hindi,english}.njk` list songs for that language; `src/index.njk` is the homepage
- **Offline page**: `src/offline.njk` rendered at `/offline.html` for failed network requests
- **Song index**: `src/songs.json.njk` generates `/songs.json` — all song URLs for SW precaching

## Adding a new song

1. Create `src/{lang}/N.md` with frontmatter `layout: song.njk`, `title`, `number`, `language`
2. Number must be unique within the language
3. Run `pnpm build` to regenerate the site
4. Run `./tests/run.sh` to verify nothing broke

## Theme system

Dark/light mode is controlled by a `data-theme` attribute on `<html>`. The base layout reads `localStorage.getItem('theme')` on page load. Do not hardcode `data-theme` — use the JS in `base.njk` or the toggle in `app.js`. The inline `<script>` in `base.njk` applies the theme synchronously before paint to prevent a flash of unstyled content.

## Search

Each language page (`bengali.njk`, `hindi.njk`, `english.njk`) has a search input (`#song-search`) backed by `src/js/search.js`. It filters `.song-card` elements by their `data-number` and `data-title` attributes. Matching is case-insensitive, trimmed, and partial. When no results match, a `#no-results` message appears with human-friendly text ("We couldn't find that song. Try a different number.").

## Testing

The `tests/` directory contains 277 Playwright tests covering all features. Test runner (`tests/run.sh`) uses `scripts/with_server.py` to start an HTTP server serving `_site/`, run pytest, then clean up.

Key test categories:
- **Home page**: structure, language cards, header, footer, meta tags, CSP
- **Language pages**: song grid, card structure, data attributes, sorting, aria-current (all data-driven)
- **Song detail**: number badge, title, lyrics content for every song (all data-driven)
- **Search**: by number/title, exact/partial, case-insensitive, no-results, all 3 languages
- **Theme toggle**: dark/light, localStorage persistence, CSS variable switching
- **Font size**: increase/decrease/reset, bounds clamping, persistence
- **Navigation**: home link, language switcher, song cards, browser back/forward
- **PWA/Offline**: manifest.json, offline page, SW registration, CSP
- **Accessibility**: ARIA labels, aria-current, touch targets, landmarks, contrast
- **Edge cases**: 404, empty states, special chars, 7 viewport sizes, page weight budget, no-JS rendering

All song data is discovered dynamically from `_site/songs.json` — no hardcoded counts or titles.

### Test prerequisites
```bash
pip install playwright pytest
playwright install chromium
```

## CI/CD

Two GitHub Actions workflows in `.github/workflows/`:
- **test.yml** — Builds site, installs Playwright, runs all 277 tests on every push/PR
- **codeql.yml** — Scans JS for security vulnerabilities (XSS, DOM injection, prototype pollution) on push/PR + weekly

Branch protection on `main` requires Playwright Tests to pass before merge. Vercel auto-deploys from `main`.

## Performance — non-negotiable

This site must be **extremely fast**, including on 2G/slow-3G connections. Every decision must optimise for speed first. Treat a slow page load as a bug. Page weight is enforced by tests (test_edge_cases.py).

### Asset budget

- Total page weight (HTML + CSS + JS) for any page: **≤ 50 KB uncompressed, ≤ 15 KB gzipped**
- Zero render-blocking scripts — all `<script>` tags must be `defer` or `async`
- No web fonts from external CDNs (Google Fonts etc.). Use the system font stack only: `font-family: system-ui, sans-serif`
- No CSS frameworks (Bootstrap, Tailwind CDN build, etc.). Hand-write only the styles actually used
- No JavaScript libraries/frameworks (React, Alpine, etc.) — vanilla JS only, and only when unavoidable
- Images: always use `loading="lazy"`, provide `width`/`height` attributes, prefer SVG for icons, and compress PNGs/JPEGs to the bone (use `sharp` or `squoosh` at build time if images are needed)

### Caching & offline

- **Service Worker** (`src/sw.js` — copied as passthrough) implements cache-first strategy:
  - Always precached: `/`, `/songs.json`, `/bengali/`, `/hindi/`, `/english/`
  - On app install, fetches `/songs.json` and precaches all song URLs dynamically
  - Navigation fallback returns `/offline.html` when offline
- Set long-lived cache headers for all versioned assets — CSS/JS files are content-hashed at build time via `scripts/rev-assets.js`
- The homepage and song-list pages must render useful content with **zero JS** (pure HTML+CSS). JS is progressive enhancement only

### Critical rendering path

- Inline critical CSS directly in `base.njk` `<style>` block (CSS variables, reset, header, container)
- Theme is applied via synchronous inline `<script>` before any external resources load
- `<html>` must include `lang` attribute; `<meta charset>` and `<meta name="viewport">` must appear before any other tags
- Avoid any layout shifts (no elements that resize after load). All interactive elements must have explicit dimensions

### Targets (measure with Lighthouse in mobile/slow-4G throttle)

- **LCP ≤ 1.5 s** on slow 4G
- **TBT = 0 ms** (no long tasks)
- **CLS = 0**
- Lighthouse Performance score **≥ 95** on mobile

## Security

A CSP meta tag is inlined in `base.njk`:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self';
style-src 'self' 'unsafe-inline'; script-src 'self' '{hash}'; img-src 'self' data:; font-src 'self';">
```

CodeQL scans JS on every push for DOM XSS, unsafe eval, regex DoS, and prototype pollution.

## UI/UX — designed for tech-illiterate users

The primary audience has **little to no smartphone/web experience**. The interface must be obvious without any instructions.

### Core principles

- **One action per screen.** Never show two competing calls-to-action at the same time
- **No jargon.** Labels must be plain language (e.g. "Hindi Songs", not "Hindi Collection"). Avoid icons without text labels
- **Touch targets ≥ 32 px** (minimum dimension) for every tappable element. Current CSS uses `min-width: 32px; min-height: 32px` for compact header controls. Language cards and song cards are larger
- **High contrast always.** Minimum WCAG AA (4.5:1) for all body text, even in dark mode. Never use placeholder text as the only label
- **Font size ≥ 18 px** for body/lyric text, ≥ 16 px for UI labels. Never go smaller to fit more on screen — let content scroll
- **No hover-only interactions.** Everything must work with a single tap/click
- **Visible, persistent navigation.** The language switcher and home link must be visible on every page without scrolling. Do not hide them behind hamburger menus
- **Search is prominent.** A song-number or title search box appears at the top of every language list page — users often come with a number in hand
- **Dark/light toggle must be labelled** ("Toggle theme" ARIA label), not just a sun/moon icon
- **Error states are human.** If a song is not found, say "We couldn't find that song. Try a different number." — not "404" or "No results"
- **No animations or transitions** that delay seeing content (no fade-ins on page load, no skeleton loaders)
- **Test on a sub-$100 Android phone** at 1× CPU throttle before shipping any UI change

## Known issues

- **bodyClass not propagating**: `song.njk` uses `{% set bodyClass = 'song-page' %}` but Nunjucks layout chaining renders content independently from the parent layout. The fix is to move `bodyClass` into the frontmatter of `song.njk`. Caught by `test_body_has_song_page_class` (6 failing tests).
