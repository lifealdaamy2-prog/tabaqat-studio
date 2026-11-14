const C='duyun-v2';
const CORE=['duyun.html','duyun.webmanifest','duyun-icon-180.png','duyun-icon-192.png','duyun-icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(CORE)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('duyun-')&&k!==C).map(k=>caches.delete(k)))));self.clients.claim()});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  const mine=(u.origin===location.origin&&/\/duyun[^/]*$/.test(u.pathname))||u.host.endsWith('fonts.googleapis.com')||u.host.endsWith('fonts.gstatic.com');
  if(!mine||e.request.method!=='GET')return;
  e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r}).catch(()=>caches.match(e.request,{ignoreSearch:true})));
});
