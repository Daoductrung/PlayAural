const CACHE_NAME = 'playaural-v3.3-minimal';

// Minimal impact: only cache core files to ensure installability
// We do NOT preload large assets.
const PRECACHE_URLS = [
    '/',
    '/index.html',
    '/manifest.json',
    '/icon.png',
    '/style.css',
    '/lang-selector.css',
    '/game.js',
    '/locales.js'
];

// Install Event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// Activate Event: Clean up old caches
self.addEventListener('activate', event => {
    const currentCaches = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (!currentCaches.includes(cacheName)) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch Event: Network First Strategy for EVERYTHING
// We always try to get the latest version from the server.
// We only use the cache if the network fails (offline mode/installability check).
self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then(networkResponse => {
                // Check valid response
                if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                    return networkResponse;
                }

                // Update cache with the latest version we just fetched
                // This ensures if we go offline later, we have the most recent version
                const responseClone = networkResponse.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
                return networkResponse;
            })
            .catch(() => {
                // Network failed, try cache
                return caches.match(event.request);
            })
    );
});
