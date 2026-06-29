const CACHE_NAME = "playaural-web-v1.0.4.7-shell-2";

const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon.png",
  "./style.css",
  "./game.js",
  "./app.js",
  "./a11y.js",
  "./audio.js",
  "./keybinds.js",
  "./network.js",
  "./store.js",
  "./locales/index.js",
  "./locales/en.js",
  "./locales/vi.js",
  "./ui/history.js",
  "./ui/menus.js",
  "./vendor/livekit-client.umd.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((names) => Promise.all(names.map((name) => (
        name === CACHE_NAME ? null : caches.delete(name)
      ))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }
  const url = new URL(event.request.url);
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    return;
  }
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      })
      .catch(() => caches.match(event.request)),
  );
});
