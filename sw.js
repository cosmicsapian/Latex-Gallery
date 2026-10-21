// Galley offline cache. The page itself is fetched fresh when the network answers quickly,
// so updates show up straight away; otherwise it opens from the device. Libraries are cached for good.
const SHELL = 'galley-shell-v2';
const LIBS = 'galley-libs-v1';
const SHELL_FILES = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png'];

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(SHELL);
    await Promise.all(SHELL_FILES.map(f => cache.add(new Request(f, { cache: 'reload' })).catch(() => {})));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) if (key !== SHELL && key !== LIBS) await caches.delete(key);
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;            // compile requests always go to the network
  const url = new URL(req.url);

  // Versioned library files never change: serve from cache, fetch once.
  if (url.origin === 'https://cdnjs.cloudflare.com') {
    event.respondWith((async () => {
      const cache = await caches.open(LIBS);
      const hit = await cache.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok || res.type === 'opaque') cache.put(req, res.clone());
      return res;
    })());
    return;
  }
  if (url.origin !== self.location.origin) return;

  event.respondWith((async () => {
    const cache = await caches.open(SHELL);
    const hit = await cache.match(req, { ignoreSearch: true });
    const fresh = fetch(req).then(res => { if (res.ok) cache.put(req, res.clone()); return res; });
    fresh.catch(() => {});
    // The page: prefer the network for 1.5 s so a new version shows at once; fall back to the copy on the device.
    if (req.mode === 'navigate' && hit) {
      const timeout = new Promise(r => setTimeout(() => r(null), 1500));
      const first = await Promise.race([fresh.catch(() => null), timeout]);
      if (first) return first;
      event.waitUntil(fresh.catch(() => {}));
      return hit;
    }
    if (hit) { event.waitUntil(fresh.catch(() => {})); return hit; }
    return fresh;
  })());
});
