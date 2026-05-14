const CACHE_NAME = "vandana-geet-v1";

// Base URLs to always precache
const BASE_URLS = ["/", "/bengali/", "/hindi/", "/english/"];

// Precache all songs (called on app installation)
async function precacheAllSongs() {
  console.log("[SW] Starting full precache...");
  const cache = await caches.open(CACHE_NAME);
  
  // Always precache base URLs
  let urlsToPrecache = [...BASE_URLS];
  
  // Fetch dynamic song list from JSON endpoint
  try {
    const response = await fetch("/songs.json");
    if (response.ok) {
      const songUrls = await response.json();
      urlsToPrecache = urlsToPrecache.concat(songUrls);
      console.log("[SW] Found", songUrls.length, "songs from songs.json");
    }
  } catch (err) {
    console.log("[SW] Could not fetch songs.json, using base URLs only:", err);
  }
  
  const results = await Promise.allSettled(
    urlsToPrecache.map((url) =>
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
  console.log(`[SW] Precached ${successCount}/${urlsToPrecache.length} pages`);
}

console.log("[SW] Service worker loaded");

// Install: activate immediately (runtime caching handles everything)
self.addEventListener("install", (event) => {
  console.log("[SW] Installing");
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener("activate", (event) => {
  console.log("[SW] Activating, cleaning old caches");
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      console.log("[SW] Found caches:", cacheNames);
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name)),
      );
    }),
  );
  self.clients.claim();
});

// Listen for messages from app.js to trigger precaching
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "PRECACHE_ALL_SONGS") {
    console.log("[SW] Received precache request");
    precacheAllSongs();
  }
});

// Fetch: cache first, then network, cache new responses
self.addEventListener("fetch", (event) => {
  const url = event.request.url;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      console.log("[SW] Fetch:", url, cachedResponse ? "CACHE HIT" : "MISS");

      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request)
        .then((response) => {
          // Don't cache non-basic responses (cross-origin, errors, etc.)
          if (!response || response.status !== 200 || response.type !== "basic") {
            console.log("[SW] Not caching:", url, response ? response.status : "no response");
            return response;
          }

          console.log("[SW] Caching:", url);
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });

          return response;
        }).catch(() => {
          console.log("[SW] OFFLINE fallback for:", url);
          // If network fails, return the homepage for navigation requests
          if (event.request.mode === "navigate") {
            return caches.match("/");
          }
          return new Response("Offline", { status: 503 });
        });
    })
  );
});