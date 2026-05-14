# Offline PWA — Service Worker

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task.

**Goal:** Add a Service Worker (`src/js/sw.js`) that pre-caches all song HTML pages and CSS at install time so the full songbook works completely offline after the first visit.

---

## Task 1: Create service worker

**Files:**
- Create: `src/js/sw.js`

- [ ] **Step 1: Write the service worker**

```js
const CACHE_NAME = 'vandana-geet-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/bengali/',
  '/hindi/',
  '/english/',
  '/css/styles.css',
  '/js/app.js',
  '/js/search.js',
  '/assets/favicon.ico'
];

// Install: cache all assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  // Activate immediately
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  // Take control of all pages
  self.clients.claim();
});

// Fetch: serve from cache, fall back to network
self.addEventListener('fetch', (event) => {
  // Only cache GET requests to our domain
  if (event.request.method !== 'GET') return;
  if (!event.request.url.startsWith(self.location.origin)) return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((response) => {
        // Don't cache non-OK responses
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }
        // Clone and cache the response
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return response;
      });
    })
  );
});
```

- [ ] **Step 2: Register the service worker from app.js**

Add to `src/js/app.js`:

```js
// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/js/sw.js').catch((err) => {
      console.log('ServiceWorker registration failed:', err);
    });
  });
}
```

- [ ] **Step 3: Commit**

```bash
git add src/js/sw.js src/js/app.js && git commit -m "feat: add service worker for offline support"
```

---

## Task 2: Cache all song pages at install

**Files:**
- Modify: `src/js/sw.js`

- [ ] **Step 1: Pre-cache all song pages dynamically**

The current static list only caches the index pages. We need to cache all individual song pages too. Since we can't list them statically, we'll use a build-time approach.

**Option A: Static list (easiest)** — hardcode all known song URLs in the array.

Given this is a small songbook, list all song URLs:

```js
const ASSETS_TO_CACHE = [
  '/',
  '/bengali/',
  '/bengali/1/',
  '/bengali/3/',
  '/hindi/',
  '/hindi/1/',
  '/hindi/3/',
  '/english/',
  '/english/1/',
  '/english/3/',
  '/css/styles.css',
  '/js/app.js',
  '/js/search.js',
  '/assets/favicon.ico',
  '/assets/images/home_logo_light.png',
  '/assets/images/home_logo_dark.png'
];
```

- [ ] **Step 2: Commit**

```bash
git add src/js/sw.js && git commit -m "feat: cache all song pages for offline access"
```

---

## Task 3: Handle navigation requests for offline song pages

**Files:**
- Modify: `src/js/sw.js`

- [ ] **Step 1: Update fetch handler for navigation requests**

Song pages are navigation requests (HTML). Cache them and serve offline.

```js
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  if (!event.request.url.startsWith(self.location.origin)) return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request).then((response) => {
        // Cache successful navigation responses (HTML pages)
        if (response && response.status === 200 && response.type === 'basic') {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      }).catch(() => {
        // If network fails and not in cache, return offline page
        return caches.match('/');
      });
    })
  );
});
```

- [ ] **Step 2: Commit**

```bash
git add src/js/sw.js && git commit -m "feat: handle offline navigation gracefully"
```

---

## Task 4: Verify offline functionality

- [ ] **Step 1: Run build**

```bash
pnpm build
```

- [ ] **Step 2: Verify service worker file exists in output**

```bash
ls _site/js/sw.js
```

- [ ] **Step 3: Test offline capability**

Open the built site in a browser with DevTools:
1. Go to `/bengali/1/`
2. Open Application tab → Service Workers → verify sw.js is registered
3. Go to Network tab → check "Offline" checkbox
4. Reload — song page should still load
5. Navigate to other song pages — should cache and load

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "verify: service worker enables offline songbook access"
```

---

## Self-Review

- [ ] `src/js/sw.js` created
- [ ] Service worker registered in `app.js`
- [ ] All song pages cached at install time
- [ ] CSS and JS cached
- [ ] Offline navigation works (shows cached page or home)
- [ ] Build completes without errors
- [ ] Service worker file appears in `_site/js/`