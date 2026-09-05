const CACHE_NAME = "amin-ai-shell-v1";

const SHELL_FILES = [
  "/static/manifest.json",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png"
];

self.addEventListener("install", function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(SHELL_FILES);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function(event) {
  event.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(
        names
          .filter(function(name) { return name !== CACHE_NAME; })
          .map(function(name) { return caches.delete(name); })
      );
    })
  );
  self.clients.claim();
});

// Network-first for pages/API, falling back to cache only for the
// static shell files above — chat data should always be fresh.
self.addEventListener("fetch", function(event) {

  const url = new URL(event.request.url);

  if (SHELL_FILES.includes(url.pathname)) {
    event.respondWith(
      caches.match(event.request).then(function(cached) {
        return cached || fetch(event.request);
      })
    );
  }

});
