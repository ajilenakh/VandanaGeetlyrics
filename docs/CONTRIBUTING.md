# Contributor Reference

A complete technical reference for developers who want to run, modify, and contribute to VandanaGeetlyrics.

---

## 1. Project Overview

**VandanaGeetlyrics** is a multilingual church songbook containing Bengali, Hindi, and English songs. It is built as a static website optimized for:

- **Extreme performance** — Targets slow 2G/3G connections with a strict 50KB page weight budget
- **Offline access** — Full songbook works without internet after first visit via Service Worker
- **Accessibility** — Designed for users with limited smartphone experience; high contrast, large touch targets, no jargon

### Goals

1. Load instantly on slow connections (LCP ≤ 1.5s on slow 4G)
2. Work completely offline after initial visit
3. Provide an accessible, jargon-free interface for all users
4. Maintain a minimal, dependency-light codebase

---

## 2. Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Static Site Generator | Eleventy | 3.x |
| Template Engine | Nunjucks | (bundled with Eleventy) |
| Package Manager | pnpm | 10.x |
| CSS | Vanilla CSS | — |
| JavaScript | Vanilla JS (ES6+) | — |
| Offline | Service Worker API | — |

### Why These Choices

- **Eleventy** — Minimal, flexible, no client-side JavaScript required for rendering
- **pnpm** — Fast, disk-efficient package management
- **Vanilla CSS/JS** — No frameworks means smaller bundles, faster parsing, no version conflicts
- **Service Worker** — Native browser API for offline caching without external dependencies

---

## 3. Project Structure

```
VandanaGeetlyrics/
├── .eleventy.js           # Eleventy configuration
├── package.json           # Project dependencies and scripts
├── scripts/
│   └── rev-assets.js      # Post-build asset revisioning
├── src/
│   ├── _includes/
│   │   ├── layouts/
│   │   │   ├── base.njk   # Base HTML shell (theme, meta, CSP)
│   │   │   └── song.njk   # Song detail page layout
│   │   └── components/
│   │       ├── header.njk # Navigation, theme toggle, font controls
│   │       └── footer.njk # Footer with logo and scripture
│   ├── assets/
│   │   ├── icons/         # PWA icons (192px, 512px)
│   │   └── images/        # Logo images (light/dark variants)
│   ├── css/
│   │   └── styles.css     # All styles (792 lines, inlined critical CSS)
│   ├── js/
│   │   ├── app.js         # Theme toggle, font size, PWA install
│   │   ├── search.js      # Client-side song search
│   │   └── sw.js          # Service worker for offline caching
│   ├── manifest.json      # PWA manifest
│   ├── bengali/           # Bengali song Markdown files
│   ├── hindi/             # Hindi song Markdown files
│   ├── english/           # English song Markdown files
│   ├── index.njk          # Homepage (language selection)
│   ├── bengali.njk        # Bengali song list page
│   ├── hindi.njk          # Hindi song list page
│   ├── english.njk        # English song list page
│   └── songs.json.njk     # JSON endpoint for song URLs (for SW precaching)
└── _site/                 # Build output (generated, not in version control)
```

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/_includes/layouts/` | Page templates (base, song) |
| `src/_includes/components/` | Reusable UI components (header, footer) |
| `src/{bengali,hindi,english}/` | Song content as Markdown files |
| `src/css/` | Stylesheets |
| `src/js/` | JavaScript files |
| `scripts/` | Build-time scripts (asset revisioning) |

---

## 4. Development Setup

### Prerequisites

- Node.js (compatible with Eleventy 3.x)
- pnpm (install via `npm install -g pnpm` or corepack)

### Install Dependencies

```bash
pnpm install
```

### Available Commands

| Command | Description |
|---------|-------------|
| `pnpm start` | Start dev server with live reload at `http://localhost:8080` |
| `pnpm build` | Production build (outputs to `_site/`, runs asset revisioning) |
| `pnpm clean` | Delete `_site/` directory |

### Running Locally

```bash
pnpm start
```

Open `http://localhost:8080` in your browser. The dev server watches for file changes and rebuilds automatically.

### Building for Production

```bash
pnpm build
```

This generates the static site in `_site/` and runs the asset revisioning script to hash CSS/JS filenames.

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

## ১. এস হে করুণাময়

এস হে করুণাময়, বিরাজ হৃদ্যাসনে,  
পূজিতে তোমারে আজি, বাসনা সবার মনে।

### ১

তব দাস-দাসী যত, হইয়াছি সমবেত,  
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
| `src/js/app.js` | Theme toggle, font size controls, service worker registration, PWA install handling |
| `src/js/search.js` | Client-side search for song list pages |
| `src/js/sw.js` | Service worker for offline caching and navigation fallback |

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
2. **Passthrough copy** copies CSS, JS, assets, and manifest to `_site/`
3. **Asset revisioning** (`scripts/rev-assets.js`) runs:
   - Hashes CSS and JS files using MD5 (first 8 characters)
   - Renames files: `styles.css` → `styles.abc12345.css`
   - Updates all HTML references to use the new hashed filenames

### Asset Revisioning Details

The revisioning script:
- Skips `sw.js` (must stay at original path for service worker registration)
- Skips already-hashed files
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
│   └── sw.js                  # Unchanged (required for registration)
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
└── songs.json
```

---

## 8. Performance Guidelines

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

The following is inlined in `base.njk` (lines 17–45):
- CSS custom properties (variables)
- Reset styles
- Header layout
- Container base styles

This ensures the above-the-fold content renders before external stylesheets load.

### Testing Performance

Use Chrome DevTools Lighthouse:
1. Open DevTools → Lighthouse tab
2. Select "Mobile"
3. Select "Slow 4G" throttling
4. Run audit

Target: Performance score ≥ 95

---

## 9. PWA & Offline

### Service Worker (`src/js/sw.js`)

The service worker implements a **cache-first** strategy:

1. **Install** — Skips waiting, activates immediately
2. **Activate** — Cleans old caches, enforces 100-entry limit
3. **Fetch** — Returns cached response if available; otherwise fetches from network and caches new responses

### Precache Strategy

- **Base URLs** — Always precached: `/`, `/songs.json`, `/bengali/`, `/hindi/`, `/english/`
- **Dynamic precaching** — On app install, fetches `/songs.json` and precaches all song URLs
- **Navigation fallback** — Returns homepage for failed navigation requests when offline

### PWA Installability

The site includes:
- `src/manifest.json` — App name, icons, theme color, display mode
- Meta tags in `base.njk` — `mobile-web-app-capable`, `apple-mobile-web-app-capable`
- Install button in `header.njk` — Shows on Android when `beforeinstallprompt` fires
- iOS manual instructions — Shows "Share → Add to Home Screen" hint on iOS

### Updating the Service Worker

When you modify `sw.js`:
1. Increment `CACHE_NAME` in `sw.js` (e.g., `vandana-geet-v1` → `vandana-geet-v2`)
2. The new service worker will install and activate automatically
3. Old cache will be cleaned on next activation

---

## 10. Submitting Changes

### Git Workflow

1. **Create a branch** for your changes:

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** following the guidelines in this document

3. **Test locally**:

```bash
pnpm build
# Verify output in _site/
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
- Confirmation that offline functionality still works

### Testing Checklist

Before submitting a PR, verify:

- [ ] `pnpm build` completes without errors
- [ ] Site loads at `http://localhost:8080`
- [ ] New songs appear in the correct language list
- [ ] Theme toggle works (light/dark)
- [ ] Offline mode works (disconnect network, reload page)
- [ ] No console errors

---

## Quick Reference

| Task | Command |
|------|---------|
| Install | `pnpm install` |
| Dev server | `pnpm start` |
| Production build | `pnpm build` |
| Clean output | `pnpm clean` |
| Add song | Create `src/{lang}/N.md` with frontmatter |
| Modify styles | Edit `src/css/styles.css` |
| Modify layout | Edit `src/_includes/layouts/*.njk` |
| Modify JS | Edit `src/js/*.js` |

---

## Questions?

If you need clarification on any part of this reference, open an issue on the repository or ask in the pull request discussion.