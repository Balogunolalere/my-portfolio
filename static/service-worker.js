// static/service-worker.js

const CACHE = "cache-name";

self.addEventListener("install", (event) => {
  // cache static assets
  event.waitUntil(
    caches.open(CACHE).then((cache) => {
      return cache.addAll([
        "/",
        "/static/main.70a66962.js",
        "/static/main.3f6952e4.css",
        "/static/assets/apple-icon-180x180.png" 
      ])
    })
  )
})

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request) 
    })
  )
})