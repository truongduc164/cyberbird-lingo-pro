const CACHE_NAME = 'cyberbird-lingo-v3.3-ai-cloud-ota';
const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './daily_timeline_data.js',
  './daily_timeline.json',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Build iOS Safari WebKit-compatible 206 Partial Content response when <audio> sends Range header
async function buildRangeOrFullResponse(request, fullResponse) {
  const rangeHeader = request.headers.get('range');
  if (!rangeHeader) return fullResponse;

  const buf = await fullResponse.clone().arrayBuffer();
  const total = buf.byteLength;
  const m = /bytes=(\d+)-(\d*)/.exec(rangeHeader);
  if (!m) return fullResponse;

  const start = parseInt(m[1], 10);
  const end = m[2] ? Math.min(parseInt(m[2], 10), total - 1) : total - 1;
  if (start >= total || start > end) {
    return new Response(null, {
      status: 416,
      headers: { 'Content-Range': `bytes */${total}` }
    });
  }

  const sliced = buf.slice(start, end + 1);
  return new Response(sliced, {
    status: 206,
    statusText: 'Partial Content',
    headers: {
      'Content-Type': fullResponse.headers.get('Content-Type') || 'audio/mpeg',
      'Content-Length': String(sliced.byteLength),
      'Content-Range': `bytes ${start}-${end}/${total}`,
      'Accept-Ranges': 'bytes'
    }
  });
}

async function serveAudioWithOfflineRange(request) {
  const cache = await caches.open(CACHE_NAME);
  const cleanUrl = request.url.split('?')[0];
  const cachedRes = await cache.match(cleanUrl, { ignoreSearch: true });
  if (cachedRes) {
    return buildRangeOrFullResponse(request, cachedRes);
  }

  try {
    const cleanReq = new Request(cleanUrl, { method: 'GET' });
    const netRes = await fetch(cleanReq);
    if (netRes && netRes.status === 200 && cleanUrl.startsWith('http')) {
      await cache.put(cleanReq, netRes.clone());
      return buildRangeOrFullResponse(request, netRes);
    }
    return netRes;
  } catch (err) {
    return new Response(null, { status: 503 });
  }
}

async function matchDynamicOfflineFallback(request, cleanUrl) {
  const exact = await caches.match(cleanUrl, { ignoreSearch: true });
  if (exact) return exact;
  if (request.mode === 'navigate' || cleanUrl.endsWith('/') || cleanUrl.includes('index.html')) {
    return (await caches.match('./index.html', { ignoreSearch: true })) ||
           (await caches.match('./', { ignoreSearch: true }));
  }
  return null;
}

self.addEventListener('fetch', (e) => {
  const url = e.request.url;

  // 1. iOS Safari + Android Offline Audio Handler (supports HTTP 206 Range requests)
  if (url.includes('.mp3')) {
    e.respondWith(serveAudioWithOfflineRange(e.request));
    return;
  }

  // 2. Network-First with Canonical Offline Cache Fallback (even if tunnel returns 502/530!)
  const isDynamicDoc =
    e.request.mode === 'navigate' ||
    url.includes('index.html') ||
    url.includes('daily_timeline');

  if (isDynamicDoc) {
    const cleanUrl = url.split('?')[0];
    e.respondWith(
      fetch(e.request)
        .then(async (netRes) => {
          if (netRes && netRes.status === 200 && cleanUrl.startsWith('http')) {
            const clone = netRes.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(new Request(cleanUrl), clone));
            return netRes;
          }
          const fallback = await matchDynamicOfflineFallback(e.request, cleanUrl);
          return fallback || netRes;
        })
        .catch(async () => {
          const fallback = await matchDynamicOfflineFallback(e.request, cleanUrl);
          return fallback || Response.error();
        })
    );
    return;
  }

  // 3. Cache-First for icons, manifest & static assets
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then((res) => {
      if (res) return res;
      return fetch(e.request).then((netRes) => {
        if (netRes && netRes.status === 200 && url.startsWith('http')) {
          const clone = netRes.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
        }
        return netRes;
      }).catch(() => res);
    })
  );
});
