// ===== AI GENERATED: public_offline_worker =====
// Purpose: Provide a connection-help page without caching business records or authentication.
// Inputs: Production same-origin navigation requests only.
// Returns: Live navigation or the precached public offline page.
// Flow: Cache a fixed public allowlist; leave API calls, Clerk and all writes to the network.

const PUBLIC_CACHE = 'bm-public-offline-v1'
const PUBLIC_FILES = [
  '/offline.html',
  '/manifest.webmanifest',
  '/icons/bm-192.svg',
  '/icons/bm-512.svg',
]

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(PUBLIC_CACHE).then((cache) => cache.addAll(PUBLIC_FILES)))
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((names) =>
        Promise.all(
          names
            .filter((name) => name.startsWith('bm-public-offline-') && name !== PUBLIC_CACHE)
            .map((name) => caches.delete(name)),
        ),
      ),
  )
})

self.addEventListener('fetch', (event) => {
  const address = new URL(event.request.url)
  if (
    event.request.method !== 'GET' ||
    address.origin !== self.location.origin ||
    address.pathname.startsWith('/api/') ||
    event.request.mode !== 'navigate'
  )
    return
  event.respondWith(fetch(event.request).catch(() => caches.match('/offline.html')))
})
