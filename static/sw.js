const CACHE_NAME = 'accounting-app-v1';
const STATIC_CACHE = 'static-v2';
const DYNAMIC_CACHE = 'dynamic-v2';

const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/persian.js@0.4.0/persian.min.js',
    'https://cdn.jsdelivr.net/npm/jalaali-js@1.1.0/dist/jalaali.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;200;300;400;500;600;700;800;900&display=swap'
];

// Install Event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
    );
    self.skipWaiting();
});

// Activate Event
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
                    .map(key => caches.delete(key))
            );
        })
    );
    return self.clients.claim();
});

// Fetch Event
self.addEventListener('fetch', event => {
    // اگر درخواست برای CDN است، مستقیماً به شبکه برو
    if (event.request.url.includes('cdn.jsdelivr.net') || 
        event.request.url.includes('cdnjs.cloudflare.com') ||
        event.request.url.includes('fonts.googleapis.com')) {
        event.respondWith(fetch(event.request));
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(cacheRes => {
                return cacheRes || fetch(event.request).then(fetchRes => {
                    return caches.open(DYNAMIC_CACHE)
                        .then(cache => {
                            // فقط درخواست‌های موفق را کش کن
                            if (fetchRes.status === 200) {
                                cache.put(event.request.url, fetchRes.clone());
                            }
                            return fetchRes;
                        });
                });
            }).catch(() => {
                // اگر درخواست HTML بود و با خطا مواجه شد، صفحه اصلی را نمایش بده
                if (event.request.url.indexOf('.html') > -1 || 
                    event.request.mode === 'navigate') {
                    return caches.match('/');
                }
            })
    );
}); 