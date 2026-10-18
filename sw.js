// Offline support for the Toy Box Arena website: keep a copy of every game file so it opens without internet.
// Bump VERSION whenever the game changes (tools/publish-site.sh does this automatically).
const VERSION = "tba-20261018095244";
const FILES = ["./", "index.html", "three.min.js", "GLTFLoader.js", "OrbitControls.js", "pieces-data.js",
  "lilitaone-latin.woff2", "baloo2-latin.woff2", "app-icon.png", "app-icon-512.png", "manifest.json"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
// Network first (so updates show up right away), falling back to the saved copy when offline.
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open(VERSION).then(c => c.put(e.request, copy)); return r; })
    .catch(() => caches.match(e.request, { ignoreSearch: true })));
});
