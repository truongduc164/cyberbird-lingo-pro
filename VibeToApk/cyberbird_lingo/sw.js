const CACHE_NAME = 'cyberbird-lingo-v2-dean';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png',
  './audio/toukui.mp3',
  './audio/kuike.mp3',
  './audio/huanchongceng.mp3',
  './audio/fengjing.mp3',
  './audio/xiabadai.mp3',
  './audio/kakou.mp3',
  './audio/neichen.mp3',
  './audio/tongfengkong.mp3',
  './audio/liushuixian.mp3',
  './audio/zhusuji.mp3',
  './audio/muju.mp3',
  './audio/penqi.mp3',
  './audio/zuzhuang.mp3',
  './audio/zhuangxiang.mp3',
  './audio/pinjian.mp3',
  './audio/hege.mp3',
  './audio/cipin.mp3',
  './audio/huashang.mp3',
  './audio/zhuangjiceshi.mp3',
  './audio/jintianjiaban.mp3',
  './audio/kaizaohui.mp3',
  './audio/huibaojindu.mp3',
  './audio/changzhang.mp3',
  './audio/zuzhang.mp3',
  './audio/gandingdan.mp3',
  './audio/anquandiyi.mp3',
  './audio/anshijiaohuo.mp3',
  './audio/praise_taibangle.mp3',
  './audio/praise_zhengque.mp3',
  './audio/praise_lihai.mp3'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting())
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

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((res) => {
      if (res) return res;
      return fetch(e.request).then((netRes) => {
        if (netRes && netRes.status === 200 && e.request.url.startsWith('http')) {
          const clone = netRes.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
        }
        return netRes;
      }).catch(() => res);
    })
  );
});
