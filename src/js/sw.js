const CACHE_NAME = "vandana-geet-v1";

// Base URLs to always precache
const BASE_URLS = ["/", "/songs.json", "/bengali/", "/hindi/", "/english/"];

// Precache all songs (called on app installation)
async function precacheAllSongs() {
  const cache = await caches.open(CACHE_NAME);
  
  // Always precache base URLs
  let urlsToPrecache = [...BASE_URLS];
  
  // Fetch dynamic song list from JSON endpoint
  try {
    const response = await fetch("/songs.json");
    if (response.ok) {
      const songUrls = await response.json();
      urlsToPrecache = urlsToPrecache.concat(songUrls);
    }
  } catch (err) {
    // Could not fetch songs.json, using base URLs only
  }
  
  const results = await Promise.allSettled(
    urlsToPrecache.map((url) =>
      fetch(url).then((response) => {
        if (response.ok) {
          return cache.put(url, response);
        }
      }).catch((err) => {
        // Failed to precache: url
      })
    )
  );
  const successCount = results.filter((r) => r.status === "fulfilled").length;
}

// Install: activate immediately (runtime caching handles everything)
self.addEventListener("install", (event) => {
  self.skipWaiting();
});

// Activate: clean old caches and enforce size limits
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name)),
      );
    }).then(() => {
      // Enforce cache size limit
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.keys().then((requests) => {
          const MAX_CACHE_ENTRIES = 100;
          if (requests.length > MAX_CACHE_ENTRIES) {
            // Delete oldest entries (first 20%)
            const toDelete = Math.floor(requests.length * 0.2);
            return Promise.all(
              requests.slice(0, toDelete).map((req) => cache.delete(req))
            );
          }
        });
      });
    })
  );
  self.clients.claim();
});

// Listen for messages from app.js to trigger precaching
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "PRECACHE_ALL_SONGS") {
    precacheAllSongs();
  }
});

// Fetch: cache first, then network, cache new responses
self.addEventListener("fetch", (event) => {
  const url = event.request.url;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request)
        .then((response) => {
          // Don't cache non-basic responses (cross-origin, errors, etc.)
          if (!response || response.status !== 200 || response.type !== "basic") {
            return response;
          }

          // Only cache requests to known-safe paths
          const safePaths = ['/css/', '/js/', '/assets/', '/bengali/', '/hindi/', '/english/'];
          const isSafePath = safePaths.some(p => url.includes(p));
          if (!isSafePath) {
            return response;
          }

          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });

          return response;
        }).catch(() => {
          // If network fails, return the homepage for navigation requests
          if (event.request.mode === "navigate") {
            return caches.match("/");
          }
          return new Response("Offline", { status: 503 });
        });
    })
  );
});