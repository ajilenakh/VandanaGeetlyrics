# PWA Installable App with On-Install Precaching

**Date:** 2026-05-14
**Status:** Approved

---

## Goal

Make the Vandana Geet songbook installable as an Android/Desktop PWA. When users install the app, all song pages are precached immediately for full offline capability. Browser-only users remain unaffected.

---

## Architecture

1. **Web App Manifest** - JSON file describing app metadata, icons, theme colors
2. **Install Detection** - Listen for `beforeinstallprompt`, store deferred prompt
3. **Install UI** - Subtle install button in header (appears when PWA installable)
4. **On-Install Precaching** - When user accepts installation, fetch and cache all song URLs
5. **Icon Generation** - Extract from existing favicon.ico → PNG at 192x192 and 512x512

---

## Components

### 1. manifest.json
- Location: `src/manifest.json`
- Contains: name, short_name, start_url, display, theme_color, background_color, icons array
- App name: "Vandana Geet"

### 2. Icon Files
- Location: `src/assets/icons/`
- Generate from favicon.ico: icon-192.png, icon-512.png
- Maskable icon variant: icon-512-maskable.png

### 3. Base Layout Update
- Add `<link rel="manifest" href="/manifest.json">` to base.njk
- Add meta tags for theme_color

### 4. Install Detection (app.js)
- Listen for `beforeinstallprompt` event
- Store `deferredPrompt` globally
- Show install button in header when prompt is available
- On button click: call `deferredPrompt.prompt()`, then precache all songs

### 5. Service Worker Update (sw.js)
- Add `precacheAllSongs()` function that fetches all song URLs and caches them
- Called when user accepts installation (via `appinstalled` event or after `prompt()`)
- Returns all song URLs for the three languages

---

## Files to Create

| File | Purpose |
|------|---------|
| `src/manifest.json` | PWA manifest |
| `src/assets/icons/icon-192.png` | App icon 192x192 |
| `src/assets/icons/icon-512.png` | App icon 512x512 |
| `src/assets/icons/icon-512-maskable.png` | Maskable icon |

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/_includes/layouts/base.njk` | Add manifest link, theme_color meta |
| `src/_includes/components/header.njk` | Add install button (conditional) |
| `src/js/app.js` | Install detection, deferred prompt, precache trigger |
| `src/js/sw.js` | Add precacheAllSongs() function |

---

## Data Flow

1. User visits site → `beforeinstallprompt` fires → install button appears in header
2. User clicks "Install" button → `prompt()` shown → user accepts → app installs
3. `appinstalled` event fires → call `precacheAllSongs()` in SW
4. Service worker fetches all song pages → caches them → full offline ready

---

## Success Criteria

- [ ] PWA installable on Chrome Android/Desktop (shows "Add to Home Screen")
- [ ] Install button visible in header when PWA installable
- [ ] On installation acceptance, all song pages cached immediately
- [ ] Installed app works fully offline
- [ ] Browser-only users see no extra UI (install button hidden if not applicable)
- [ ] Lighthouse PWA audit passes