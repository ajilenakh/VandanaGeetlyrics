# VandanaGeetlyrics

A multilingual church songbook (Bengali, Hindi, English) built with Eleventy. Optimized for offline use and extreme performance on slow connections.

---

## Overview

VandanaGeetlyrics is a static website that serves church songs in three languages. It is designed for:

- **Extreme performance** — Loads fast on 2G/3G connections (LCP ≤ 1.5s)
- **Offline access** — Full songbook works without internet after first visit
- **Accessibility** — High contrast, large touch targets, no jargon

## Tech Stack

| Layer | Technology |
|-------|-------------|
| Static Site Generator | Eleventy 3.x |
| Template Engine | Nunjucks |
| Package Manager | pnpm |
| CSS | Vanilla CSS |
| JavaScript | Vanilla JS |
| Offline | Service Worker API |

## Quick Start

```bash
# Install dependencies
pnpm install

# Start dev server
pnpm start

# Build for production
pnpm build
```

- Dev server: `http://localhost:8080`
- Build output: `_site/`

## Key Features

- **Offline-first** — Service worker caches all songs for offline access
- **PWA** — Installable on mobile devices
- **Dark/Light theme** — Toggle with persistent preference
- **Font size controls** — Adjustable for accessibility
- **Client-side search** — Filter songs by number or title
- **Asset revisioning** — Content-hashed filenames for long-term caching

## Project Structure

```
src/
├── _includes/
│   ├── layouts/      # base.njk, song.njk
│   └── components/  # header.njk, footer.njk
├── assets/          # Icons, images
├── css/             # styles.css
├── js/              # app.js, search.js, sw.js
├── bengali/         # Bengali song Markdown files
├── hindi/           # Hindi song Markdown files
├── english/         # English song Markdown files
└── *.njk            # Page templates
```

## Commands

| Command | Description |
|---------|-------------|
| `pnpm start` | Dev server with live reload |
| `pnpm build` | Production build |
| `pnpm clean` | Delete `_site/` |

## Documentation

For detailed contributor documentation — including how to add songs, modify layouts, and submit changes — see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License

ISC