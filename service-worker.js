const CACHE_NAME = 'tony-fortune-v1';
const ASSETS = [
  new URL('index.html', self.location).toString(),
  new URL('style.css', self.location).toString(),
  new URL('script.js', self.location).toString(),
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => (k !== CACHE_NAME ? caches.delete(k) : null)))
    )
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then((res) => {
          try {
            const clone = res.clone();
            if (req.method === 'GET' && res.status === 200 && res.type === 'basic') {
              caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
            }
          } catch (_) {}
          return res;
        })
        .catch(() => {
          // Fallback สำหรับ navigation
          if (req.mode === 'navigate') {
            return caches.match(new URL('index.html', self.location).toString());
          }
        });
    })
  );
});