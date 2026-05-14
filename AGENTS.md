# VandanaGeetlyrics

Static site generator for a multilingual church songbook using Eleventy 3.x.

## Build commands

- `pnpm build` — production build (outputs to `_site/`)
- `pnpm start` — dev server with live reload
- `pnpm clean` — delete `_site/`

## Architecture

- **Input**: `src/` → **Output**: `_site/`
- **Content**: `src/{bengali,hindi,english}/*.md` — each song file has frontmatter `layout`, `title`, `number`, `language`
- **Layouts**: `src/_includes/layouts/` — `base.njk` (HTML shell), `song.njk` (song detail)
- **Components**: `src/_includes/components/` — header, footer, song-header
- **Collections**: Eleventy auto-creates `bengali`, `hindi`, `english` collections sorted by `number`
- **Passthrough**: `src/css/`, `src/js/`, `src/assets/` are copied as-is to `_site/`
- **Entry pages**: `src/{bengali,hindi,english}.njk` list songs for that language; `src/index.njk` is the homepage

## Adding a new song

1. Create `src/{lang}/N.md` with frontmatter `layout: song.njk`, `title`, `number`, `language`
2. Number must be unique within the language
3. Run `pnpm build` to regenerate the site

## Theme system

Dark/light mode is controlled by a `data-theme` attribute on `<html>`. The base layout reads `localStorage.getItem('theme')` on page load. Do not hardcode `data-theme` — use the JS in `base.njk` or the toggle in `app.js`.

## Performance — non-negotiable

This site must be **extremely fast**, including on 2G/slow-3G connections. Every decision must optimise for speed first. Treat a slow page load as a bug.

### Asset budget

- Total page weight (HTML + CSS + JS) for any page: **≤ 50 KB uncompressed, ≤ 15 KB gzipped**
- Zero render-blocking scripts — all `<script>` tags must be `defer` or `async`
- No web fonts from external CDNs (Google Fonts etc.). Use the system font stack only: `font-family: system-ui, sans-serif`
- No CSS frameworks (Bootstrap, Tailwind CDN build, etc.). Hand-write only the styles actually used
- No JavaScript libraries/frameworks (React, Alpine, etc.) — vanilla JS only, and only when unavoidable
- Images: always use `loading="lazy"`, provide `width`/`height` attributes, prefer SVG for icons, and compress PNGs/JPEGs to the bone (use `sharp` or `squoosh` at build time if images are needed)

### Caching & offline

- Add a **Service Worker** (`src/js/sw.js`) that pre-caches all song HTML pages and CSS at install time so the full songbook works **completely offline** after the first visit
- Set long-lived cache headers for all versioned assets (add a content hash to filenames at build time via Eleventy transforms or a plugin)
- The homepage and song-list pages must render useful content with **zero JS** (pure HTML+CSS). JS is progressive enhancement only

### Critical rendering path

- Inline all critical CSS (above-the-fold styles) directly in `<head>` via an Eleventy shortcode or transform; load the rest with `<link rel="preload">`
- `<html>` must include `lang` attribute; `<meta charset>` and `<meta name="viewport">` must appear before any other tags
- Avoid any layout shifts (no elements that resize after load). All interactive elements must have explicit dimensions

### Targets (measure with Lighthouse in mobile/slow-4G throttle)

- **LCP ≤ 1.5 s** on slow 4G
- **TBT = 0 ms** (no long tasks)
- **CLS = 0**
- Lighthouse Performance score **≥ 95** on mobile

## UI/UX — designed for tech-illiterate users

The primary audience has **little to no smartphone/web experience**. The interface must be obvious without any instructions.

### Core principles

- **One action per screen.** Never show two competing calls-to-action at the same time
- **No jargon.** Labels must be plain language (e.g. "Hindi Songs", not "Hindi Collection"). Avoid icons without text labels
- **Touch targets ≥ 48 × 48 px** for every tappable element (buttons, links, toggles). Add `padding` rather than relying on small text links
- **High contrast always.** Minimum WCAG AA (4.5:1) for all body text, even in dark mode. Never use placeholder text as the only label
- **Font size ≥ 18 px** for body/lyric text, ≥ 16 px for UI labels. Never go smaller to fit more on screen — let content scroll
- **No hover-only interactions.** Everything must work with a single tap/click
- **Visible, persistent navigation.** The language switcher and home link must be visible on every page without scrolling. Do not hide them behind hamburger menus
- **Search is prominent.** A song-number or title search box should appear at the top of every language list page — users often come with a number in hand
- **Dark/light toggle must be labelled** ("Dark" / "Light"), not just a sun/moon icon
- **Error states are human.** If a song is not found, say "We couldn't find that song. Try a different number." — not "404" or "No results"
- **No animations or transitions** that delay seeing content (no fade-ins on page load, no skeleton loaders)
- **Test on a sub-$100 Android phone** at 1× CPU throttle before shipping any UI change
