const CACHE_NAME = "vandana-geet-v1";
const ASSETS_TO_CACHE = [
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
  "/css/styles.css",
  "/js/app.js",
  "/js/search.js",
  "/assets/favicon.ico",
  "/assets/images/home_logo_light.avif",
  "/assets/images/home_logo_dark.avif",
];

// Install: cache all assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    }),
  );
  // Activate immediately
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name)),
      );
    }),
  );
  // Take control of all pages
  self.clients.claim();
});

// Fetch: serve from cache, fall back to network
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  if (!event.request.url.startsWith(self.location.origin)) return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request)
        .then((response) => {
          // Cache successful navigation responses (HTML pages)
          if (
            response &&
            response.status === 200 &&
            response.type === "basic"
          ) {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return response;
        })
        .catch(() => {
          // If network fails and not in cache, return offline page
          return caches.match("/");
        });
    })
  );
});