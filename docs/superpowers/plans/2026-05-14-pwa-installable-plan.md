# PWA Installable App - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Vandana Geet installable as a PWA with full offline support via on-install precaching.

**Architecture:** Web App Manifest + Install Detection + Install UI + On-Install Precaching. Browser-only users remain unaffected (install button hidden).

**Tech Stack:** Vanilla JS service worker, Eleventy static site, ImageMagick for icon generation.

---

## File Structure

### To Create
| File | Purpose |
|------|---------|
| `src/manifest.json` | PWA manifest with app metadata |
| `src/assets/icons/icon-192.png` | App icon 192x192 |
| `src/assets/icons/icon-512.png` | App icon 512x512 |
| `src/assets/icons/icon-512-maskable.png` | Maskable icon variant |

### To Modify
| File | Changes |
|------|---------|
| `src/_includes/layouts/base.njk` | Add manifest link, theme_color meta |
| `src/_includes/components/header.njk` | Add install button |
| `src/js/app.js` | Install detection, deferred prompt, precache trigger |
| `src/js/sw.js` | Add precacheAllSongs() function |

---

## Task 1: Generate App Icons

**Files:**
- Create: `src/assets/icons/icon-192.png`
- Create: `src/assets/icons/icon-512.png`
- Create: `src/assets/icons/icon-512-maskable.png`

- [ ] **Step 1: Create icons directory**

```bash
mkdir -p src/assets/icons
```

- [ ] **Step 2: Extract and convert favicon to PNG at 192x192**

```bash
convert src/assets/favicon.ico[0] -resize 192x192 src/assets/icons/icon-192.png
```

- [ ] **Step 3: Create 512x512 icon**

```bash
convert src/assets/favicon.ico[0] -resize 512x512 src/assets/icons/icon-512.png
```

- [ ] **Step 4: Create maskable icon (add padding for safe zone)**

Maskable icons need a safe zone of 80% in the center. Create with padding:

```bash
convert src/assets/favicon.ico[0] -resize 384x384 -background transparent -gravity center -extent 512x512 src/assets/icons/icon-512-maskable.png
```

- [ ] **Step 5: Verify icons created**

```bash
ls -la src/assets/icons/
file src/assets/icons/*.png
```

- [ ] **Step 6: Commit**

```bash
git add src/assets/icons/ && git commit -m "feat: generate PWA app icons"
```

---

## Task 2: Create Web App Manifest

**Files:**
- Create: `src/manifest.json`

- [ ] **Step 1: Write manifest.json**

```json
{
  "name": "Vandana Geet",
  "short_name": "Vandana Geet",
  "description": "A multilingual church songbook with Bengali, Hindi, and English songs. Optimized for offline use.",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait-primary",
  "background_color": "#f8f4ee",
  "theme_color": "#e89a1c",
  "dir": "ltr",
  "lang": "en",
  "categories": ["music", "entertainment"],
  "icons": [
    {
      "src": "/assets/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/assets/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    },
    {
      "src": "/assets/icons/icon-512-maskable.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
```

- [ ] **Step 2: Verify manifest is valid JSON**

```bash
cat src/manifest.json | node -e "JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf-8')); console.log('Valid JSON')"
```

- [ ] **Step 3: Commit**

```bash
git add src/manifest.json && git commit -m "feat: add PWA manifest"
```

---

## Task 3: Update Base Layout

**Files:**
- Modify: `src/_includes/layouts/base.njk`

- [ ] **Step 1: Read current base.njk**

Read the file to verify current content.

- [ ] **Step 2: Add manifest link and theme_color meta**

Find the `<head>` section and add manifest link and theme_color meta:

Add after `<link rel="icon" href="/assets/favicon.ico">`:
```html
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#e89a1c">
```

Add dark mode theme-color in the existing theme script:
```html
<script>
  (function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.querySelector('meta[name="theme-color"]').content = savedTheme === 'dark' ? '#f0a020' : '#e89a1c';
  })();
</script>
```

- [ ] **Step 3: Rebuild and verify**

```bash
pnpm build && grep -E "(manifest|theme-color)" _site/index.html
```

Expected output should show both manifest link and theme-color meta.

- [ ] **Step 4: Commit**

```bash
git add src/_includes/layouts/base.njk && git commit -m "feat: add manifest link and theme-color meta"
```

---

## Task 4: Add Install Button to Header

**Files:**
- Modify: `src/_includes/components/header.njk`

- [ ] **Step 1: Read current header.njk**

```bash
cat src/_includes/components/header.njk
```

- [ ] **Step 2: Add install button after theme toggle**

Add this button after the theme toggle button (with display:none by default):

```html
<button id="install-btn" style="display:none;" aria-label="Install app">Install App</button>
```

Add CSS for the button (inline in header or in a style tag):

```html
<style>
  #install-btn {
    background: var(--accent);
    color: var(--bg-primary);
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.875rem;
    cursor: pointer;
  }
  #install-btn:hover {
    background: var(--accent-hover);
  }
</style>
```

- [ ] **Step 3: Commit**

```bash
git add src/_includes/components/header.njk && git commit -m "feat: add install button to header"
```

---

## Task 5: Update app.js with Install Detection

**Files:**
- Modify: `src/js/app.js`

- [ ] **Step 1: Read current app.js**

```bash
cat src/js/app.js
```

- [ ] **Step 2: Add install detection code**

Add at the end of the DOMContentLoaded event, before the closing `});`:

```javascript
// PWA Install Detection
let deferredPrompt = null;

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const installBtn = document.getElementById("install-btn");
  if (installBtn) {
    installBtn.style.display = "block";
  }
});

window.addEventListener("appinstalled", async () => {
  deferredPrompt = null;
  const installBtn = document.getElementById("install-btn");
  if (installBtn) {
    installBtn.style.display = "none";
  }
  // Trigger precaching of all songs
  if ("serviceWorker" in navigator) {
    const registration = await navigator.serviceWorker.ready;
    registration.active.postMessage({ type: "PRECACHE_ALL_SONGS" });
  }
});

// Install button click handler
const installBtn = document.getElementById("install-btn");
if (installBtn) {
  installBtn.addEventListener("click", async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      deferredPrompt = null;
      installBtn.style.display = "none";
      // Trigger precaching
      if ("serviceWorker" in navigator) {
        const registration = await navigator.serviceWorker.ready;
        registration.active.postMessage({ type: "PRECACHE_ALL_SONGS" });
      }
    }
  });
}
```

- [ ] **Step 3: Verify syntax**

```bash
node --check src/js/app.js
```

- [ ] **Step 4: Commit**

```bash
git add src/js/app.js && git commit -m "feat: add PWA install detection and install button handler"
```

---

## Task 6: Update Service Worker for Precaching

**Files:**
- Modify: `src/js/sw.js`

- [ ] **Step 1: Read current sw.js**

```bash
cat src/js/sw.js
```

- [ ] **Step 2: Add all song URLs and precache function**

Add this code after the `const CACHE_NAME` line:

```javascript
// All song URLs for precaching on install
const ALL_SONG_URLS = [
  "/",
  "/bengali/",
  "/bengali/1/",
  "/bengali/3/",
  "/hindi/",
  "/hindi/1/",
  "/hindi/3/",
  "/english/",
  "/english/1/",
  "/english/3/",
];

// Precache all songs (called on app installation)
async function precacheAllSongs() {
  console.log("[SW] Starting full precache...");
  const cache = await caches.open(CACHE_NAME);
  const results = await Promise.allSettled(
    ALL_SONG_URLS.map((url) =>
      fetch(url).then((response) => {
        if (response.ok) {
          return cache.put(url, response);
        }
      }).catch((err) => {
        console.log("[SW] Failed to precache:", url, err);
      })
    )
  );
  const successCount = results.filter((r) => r.status === "fulfilled").length;
  console.log(`[SW] Precached ${successCount}/${ALL_SONG_URLS.length} pages`);
}
```

- [ ] **Step 3: Add message listener for precache trigger**

Add in the install event handler or after it:

```javascript
// Listen for messages from app.js to trigger precaching
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "PRECACHE_ALL_SONGS") {
    console.log("[SW] Received precache request");
    precacheAllSongs();
  }
});
```

- [ ] **Step 4: Verify syntax**

```bash
node --check src/js/sw.js
```

- [ ] **Step 5: Commit**

```bash
git add src/js/sw.js && git commit -m "feat: add on-install precaching to service worker"
```

---

## Task 7: Build and Test

- [ ] **Step 1: Clean rebuild**

```bash
pnpm clean && pnpm build
```

- [ ] **Step 2: Verify manifest in output**

```bash
ls _site/manifest.json && cat _site/manifest.json | head -10
```

- [ ] **Step 3: Verify icons in output**

```bash
ls _site/assets/icons/
```

- [ ] **Step 4: Test with Lighthouse or browser DevTools**

Manual test:
1. Open site in Chrome
2. DevTools → Application → Manifest → verify manifest loads
3. Application → Service Workers → verify sw.js registered
4. Click "Install App" button → accept → verify all songs cached
5. Go to Application → Cache Storage → verify all song pages present

- [ ] **Step 5: Final commit**

```bash
git add -A && git commit -m "feat: PWA installable app with on-install precaching"
```

---

## Self-Review Checklist

- [ ] All 6 tasks completed
- [ ] Icons generated and in correct format
- [ ] Manifest is valid JSON with all required fields
- [ ] Install button appears when beforeinstallprompt fires
- [ ] Service worker precaches all song URLs on installation
- [ ] Build completes without errors
- [ ] All files committed