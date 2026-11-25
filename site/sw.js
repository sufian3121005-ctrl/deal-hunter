// Deal Hunter service worker: เปิดแอปได้แม้เน็ตไม่ดี (ไม่แคชการเรียก API/Supabase)
const VERSION = 'dh-2026-11-25';
const SHELL = ['/', '/manifest.webmanifest', '/icons/icon-192.png', '/icons/icon-512.png', '/icons/apple-touch-icon.png'];
const CDN = ['cdn.tailwindcss.com', 'unpkg.com', 'fonts.googleapis.com', 'fonts.gstatic.com'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // หน้าแอป: เอาเวอร์ชันล่าสุดจากเน็ตก่อน ถ้าเน็ตไม่มีใช้ของที่เก็บไว้
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => { const cp = r.clone(); caches.open(VERSION).then(c => c.put('/', cp)); return r; })
      .catch(() => caches.match('/')));
    return;
  }
  // ไฟล์ในเว็บเดียวกัน (ไอคอน ฯลฯ): ใช้ของที่เก็บไว้ก่อน
  if (url.origin === self.location.origin) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => { if (r.ok) { const cp = r.clone(); caches.open(VERSION).then(c => c.put(req, cp)); } return r; })));
    return;
  }
  // สคริปต์/ฟอนต์จาก CDN: ใช้ของที่เก็บไว้ แล้วอัปเดตเบื้องหลัง
  if (CDN.includes(url.hostname)) {
    e.respondWith(caches.open(VERSION).then(async c => {
      const hit = await c.match(req);
      const net = fetch(req).then(r => { if (r.ok || r.type === 'opaque') c.put(req, r.clone()); return r; }).catch(() => hit);
      return hit || net;
    }));
  }
  // อย่างอื่น (Supabase/AI) ส่งผ่านตามปกติ
});
