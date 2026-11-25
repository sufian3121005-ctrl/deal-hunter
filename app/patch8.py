# patch8: ติดตั้งเป็นแอป (PWA) — manifest, ไอคอน, service worker, ปุ่มติดตั้ง
import sys
s=open('deal-hunter-v2.html',encoding='utf-8').read()
def rep(old,new):
    global s
    if old not in s: sys.exit('NOT FOUND: '+old[:90])
    s=s.replace(old,new,1)
rep("<title>Deal Hunter</title>","""<title>Deal Hunter</title>
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#10b981">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Deal Hunter">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png">""")
rep("""   <button onclick="Store.reset()" class="tapscale rounded-full bg-black/5 px-2.5 py-1.5 text-[11px] text-slate-500">รีเซ็ต</button>""",
"""   <button id="installBtn" onclick="installApp()" class="tapscale hidden rounded-full bg-brand-500 px-3 py-1.5 text-[11px] font-bold text-white">📲 ติดตั้งแอป</button>
   <button onclick="Store.reset()" class="tapscale rounded-full bg-black/5 px-2.5 py-1.5 text-[11px] text-slate-500">รีเซ็ต</button>""")
rep("render();Batch.load();Sync.start();","""/* ============ ติดตั้งเป็นแอป (PWA) ============ */
let installEvt=null;
const isStandalone=()=>matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;
const isIOS=()=>/iphone|ipad|ipod/i.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
function showInstall(on){const b=document.getElementById('installBtn');if(b)b.classList.toggle('hidden',!on||isStandalone());}
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installEvt=e;showInstall(true);});
window.addEventListener('appinstalled',()=>{installEvt=null;showInstall(false);toast('ติดตั้งแอปแล้ว เปิดจากไอคอนบนหน้าจอได้เลย');});
async function installApp(){
 if(installEvt){installEvt.prompt();const r=await installEvt.userChoice;installEvt=null;if(r.outcome!=='accepted')showInstall(true);return;}
 const ios=isIOS();const m=document.createElement('div');m.className='fixed inset-0 z-[60] grid place-items-end bg-black/40 p-3 sm:place-items-center';m.onclick=e=>{if(e.target===m)m.remove()};
 m.innerHTML=`<div class="w-full max-w-sm rounded-3xl bg-white p-5 text-slate-800 shadow-card dark:bg-ink-900 dark:text-slate-100">
  <div class="flex items-center gap-3"><img src="/icons/icon-192.png" class="h-12 w-12 rounded-2xl"><div><div class="font-extrabold">ติดตั้ง Deal Hunter</div><div class="text-xs text-slate-500">ใช้เหมือนแอป เปิดจากหน้าจอโฮม</div></div></div>
  <ol class="mt-4 list-decimal space-y-2 pl-5 text-sm">${ios?`<li>เปิดหน้านี้ใน <b>Safari</b></li><li>กดปุ่ม <b>แชร์</b> (สี่เหลี่ยมมีลูกศรชี้ขึ้น) ด้านล่าง</li><li>เลื่อนลงแล้วกด <b>เพิ่มไปยังหน้าจอโฮม</b></li><li>กด <b>เพิ่ม</b> มุมขวาบน</li>`
   :`<li>กดปุ่ม <b>⋮</b> มุมขวาบนของ Chrome</li><li>เลือก <b>ติดตั้งแอป</b> หรือ <b>เพิ่มลงในหน้าจอหลัก</b></li><li>กด <b>ติดตั้ง</b></li>`}</ol>
  <button onclick="this.closest('.fixed').remove()" class="tapscale mt-5 w-full rounded-2xl bg-brand-500 py-3 text-sm font-bold text-white">เข้าใจแล้ว</button></div>`;
 document.body.appendChild(m);}
if(!isStandalone()&&isIOS())showInstall(true);
if('serviceWorker' in navigator&&(location.protocol==='https:'||location.hostname==='localhost'))window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(e=>console.warn('sw',e)));
if(new URLSearchParams(location.search).get('go')==='deals')cur='/deals';
render();Batch.load();Sync.start();""")
open('deal-hunter-v2.html','w',encoding='utf-8').write(s)
print('patch8 ok')
