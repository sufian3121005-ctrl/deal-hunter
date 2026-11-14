# patch6: ถ่ายได้หลายรูปก่อน (ภาพรวม ป้าย โลโก้ ตำหนิ ฯลฯ) แล้วค่อยกดให้ AI วิเคราะห์
import sys
s=open('deal-hunter-v2.html',encoding='utf-8').read()
def rep(old,new):
    global s
    if old not in s: sys.exit('NOT FOUND: '+old[:90])
    s=s.replace(old,new,1)

# 1) อัปโหลด: ยังไม่มีผลวิเคราะห์ = เก็บเข้าถาดรูป ไม่สแกนทันที
rep("""async function upload(el,more){const files=[...el.files];if(!files.length)return;
 if(!more){imgs=[];thumbs=[];labels=[];scan=null;ana=null;pending=[];hand={};}
 const bad=[];
 for(const f of files.slice(0,6-imgs.length)){const big=await resizeImg(f,1280,.82);const q=await photoCheck(big);
  imgs.push(big);thumbs.push(await resizeImg(f,400,.7));labels.push(more?(nextLabel||'มุมเพิ่มเติม'):'ตัวสินค้าเต็มชิ้น');if(!q.ok)bad.push({i:imgs.length-1,problem:q.problem});}
 el.value='';nextLabel='';""",
"""async function upload(el,more){const files=[...el.files];if(!files.length)return;
 if(!more&&ana){imgs=[];thumbs=[];labels=[];photoWarn=[];scan=null;ana=null;pending=[];hand={};}
 const tray=!ana;
 if(imgs.length>=MAX_PHOTOS){el.value='';toast('ครบ '+MAX_PHOTOS+' รูปแล้ว ลบรูปที่ไม่จำเป็นก่อน');return;}
 if(tray)renderDrop(true,'กำลังเตรียมรูป...');
 const bad=[];
 for(const f of files.slice(0,MAX_PHOTOS-imgs.length)){const big=await resizeImg(f,1280,.82);const q=await photoCheck(big);
  const lab=nextLabel||(tray?(nextShot()||'มุมเพิ่มเติม'):'มุมเพิ่มเติม');
  nextLabel=tray&&nextLabel?'':nextLabel;
  if(tray&&replaceIdx!==null&&replaceIdx<imgs.length){imgs[replaceIdx]=big;thumbs[replaceIdx]=await resizeImg(f,400,.7);photoWarn[replaceIdx]=q.ok?'':q.problem;replaceIdx=null;continue;}
  imgs.push(big);thumbs.push(await resizeImg(f,400,.7));labels.push(lab);photoWarn.push(q.ok?'':q.problem);if(!q.ok)bad.push({i:imgs.length-1,problem:q.problem});}
 el.value='';nextLabel='';replaceIdx=null;
 if(tray){renderDrop(false);renderTray();return;}""")

# 2) ตัวแปร + ถาดรูป
rep("let scan=null,thumbs=[],labels=[],hand={},nextLabel='',refsCache={},confirmRef=false;",
"""let scan=null,thumbs=[],labels=[],hand={},nextLabel='',refsCache={},confirmRef=false,photoWarn=[],replaceIdx=null;
const MAX_PHOTOS=10;
/* รายการรูปที่ควรถ่าย แยกตามประเภทสินค้า (ถ่ายตามลำดับ แล้วค่อยให้ AI วิเคราะห์) */
const SHOTS={
 'apparel.vintage':['ภาพรวมด้านหน้า (เห็นลายทั้งตัว)','ป้ายคอ (ให้อ่านตัวหนังสือได้)','ป้ายวิธีซัก/เลข RN','ตะเข็บปลายแขนหรือชายเสื้อ (ด้านใน)','ปีลิขสิทธิ์ © ใต้ลายสกรีน','ด้านหลัง'],
 'apparel.denim':['ภาพรวมด้านหน้า','แท็บแดง/ป้ายหลังเอว','ป้ายวิธีซัก (รหัสวันที่)','ตะเข็บข้างขาด้านใน (ผ้าริม)','หลังกระดุมเม็ดบน/หมุด'],
 'apparel.football':['ภาพรวมด้านหน้า','ป้ายรหัสสินค้าด้านใน','ป้ายคอด้านใน','โลโก้แบรนด์และตราสโมสรใกล้ๆ','ด้านหลัง (ชื่อ/เบอร์)'],
 'shoes.brand':['ภาพรวมด้านข้าง','ป้ายในลิ้น (รหัสรุ่น)','พื้นรองเท้า','ส้นด้านหลัง','ป้ายกล่อง (ถ้ามี)'],
 'luxury':['ภาพรวม','โลโก้ใกล้ๆ','รหัสผลิต/serial/date code','อะไหล่โลหะ/ซิป','ด้านใน/ฝาหลัง'],
 'tools.power':['ภาพรวมตัวเครื่อง','เพลทรุ่น/serial','แบตเตอรี่ (ด้านบนและด้านใต้)','ช่องระบายลม/หัวจับดอก','สายไฟ/ปลั๊ก'],
 'phone':['ด้านหน้า (เปิดจอ)','ด้านหลัง','หน้าเกี่ยวกับเครื่อง/IMEI','สุขภาพแบตเตอรี่','ประวัติชิ้นส่วนและการซ่อม (iPhone)'],
 'generic':['ภาพรวม','ป้าย/โลโก้','รุ่น/serial (ถ้ามี)','ด้านหลัง/ด้านใน']};
const SHOT_CATS=[['apparel.vintage','👕 เสื้อวินเทจ'],['apparel.denim','👖 ยีนส์/แจ็คเก็ต'],['apparel.football','⚽ เสื้อบอล'],['shoes.brand','👟 รองเท้า'],
 ['luxury','👜 แบรนด์เนม/นาฬิกา'],['tools.power','🔧 เครื่องมือช่าง'],['phone','📱 มือถือ'],['generic','❓ อื่นๆ/ไม่แน่ใจ']];
const DEFECT='ตำหนิ (รู/คราบ/ขาด/สึก)';
let shotCat=(()=>{try{return localStorage.getItem('deal_shotcat')||'apparel.vintage'}catch(e){return'apparel.vintage'}})();
const shotList=()=>SHOTS[shotCat]||SHOTS.generic;
const nextShot=()=>shotList().find(k=>!labels.includes(k))||'';
function setShotCat(c){shotCat=c;try{localStorage.setItem('deal_shotcat',c)}catch(e){}renderDrop(false);renderTray();}
function shootKind(k){if(imgs.length>=MAX_PHOTOS)return toast('ครบ '+MAX_PHOTOS+' รูปแล้ว ลบรูปที่ไม่จำเป็นก่อน');
 const i=labels.indexOf(k);if(i>=0&&k!==DEFECT){replaceIdx=i;nextLabel='';}else{nextLabel=k;replaceIdx=null;}document.getElementById('f_img').click();}
function shootNext(){shootKind(nextShot()||DEFECT);}
function pickGallery(){if(imgs.length>=MAX_PHOTOS)return toast('ครบ '+MAX_PHOTOS+' รูปแล้ว');nextLabel=nextShot()||'มุมเพิ่มเติม';replaceIdx=null;document.getElementById('f_gal').click();}
function trayRemove(i){imgs.splice(i,1);thumbs.splice(i,1);labels.splice(i,1);photoWarn.splice(i,1);renderDrop(false);renderTray();}
function trayClear(){imgs=[];thumbs=[];labels=[];photoWarn=[];renderDrop(false);renderTray();}
function Tray(){
 const list=shotList();const done=list.filter(k=>labels.includes(k)).length;const nx=nextShot();
 const row=(k,n)=>{const i=labels.indexOf(k);const ok=i>=0;const isNext=k===nx;
  return`<div class="flex items-center gap-3 rounded-2xl p-2 ${isNext?'bg-brand-500/10 ring-2 ring-brand-500/40':''}">
  ${ok?`<img src="${thumbs[i]}" class="h-14 w-14 flex-none rounded-xl object-cover ${photoWarn[i]?'ring-2 ring-amber-500':''}">`
     :`<div class="grid h-14 w-14 flex-none place-items-center rounded-xl bg-black/5 text-lg font-extrabold text-slate-400 dark:bg-white/10">${n}</div>`}
  <div class="min-w-0 flex-1"><div class="text-sm font-semibold ${ok?'':'text-slate-600 dark:text-slate-300'}">${ok?'✅ ':''}${k}</div>
  ${ok&&photoWarn[i]?`<div class="text-[11px] text-amber-600">รูป${photoWarn[i]} — แตะถ่ายใหม่</div>`:isNext?`<div class="text-[11px] font-semibold text-brand-600">← ถ่ายรูปนี้ต่อ</div>`:''}</div>
  <button onclick="shootKind('${k}')" class="tapscale flex-none rounded-full ${ok?'bg-black/5 dark:bg-white/10':'bg-brand-500 text-white'} px-3 py-1.5 text-xs font-bold">${ok?'ถ่ายใหม่':'📷 ถ่าย'}</button>
  ${ok?`<button onclick="trayRemove(${i})" class="flex-none px-1 text-slate-400" aria-label="ลบ">✕</button>`:''}</div>`;};
 const extras=labels.map((l,i)=>[l,i]).filter(([l])=>!list.includes(l));
 return Card(`<div class="text-sm font-bold">1. ของชิ้นนี้คืออะไร</div>
 <div class="mt-2 flex flex-wrap gap-1.5">${SHOT_CATS.map(([c,t])=>`<button onclick="setShotCat('${c}')" class="tapscale rounded-full px-3 py-1.5 text-xs font-semibold ${c===shotCat?'bg-brand-500 text-white':'bg-black/5 dark:bg-white/10'}">${t}</button>`).join('')}</div>
 <div class="mt-4 flex items-center justify-between"><div class="text-sm font-bold">2. ถ่ายตามรายการ (${done}/${list.length})</div>
 ${imgs.length?`<button onclick="trayClear()" class="text-[11px] text-slate-400 underline">เริ่มใหม่</button>`:''}</div>
 <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-black/5 dark:bg-white/10"><div class="h-full rounded-full bg-brand-500" style="width:${Math.round(done/list.length*100)}%"></div></div>
 <div class="mt-2 space-y-1">${list.map((k,n)=>row(k,n+1)).join('')}</div>
 <div class="mt-4 text-sm font-bold">3. ตำหนิ / มุมอื่น (ถ้ามี)</div>
 <div class="mt-1 text-[11px] text-slate-500">ถ่ายตำหนิทุกจุด AI จะหักราคาให้ตามสภาพจริง</div>
 ${extras.length?`<div class="mt-2 flex flex-wrap gap-2">${extras.map(([l,i])=>`<div class="relative"><img src="${thumbs[i]}" class="h-16 w-16 rounded-xl object-cover ${photoWarn[i]?'ring-2 ring-amber-500':''}"><button onclick="trayRemove(${i})" class="absolute -right-1 -top-1 grid h-5 w-5 place-items-center rounded-full bg-black/70 text-[10px] text-white">✕</button><div class="mt-0.5 w-16 truncate text-[10px] text-slate-500">${l.split(' ')[0]}</div></div>`).join('')}</div>`:''}
 <div class="mt-2 flex flex-wrap gap-1.5"><button onclick="shootKind('${DEFECT}')" class="tapscale rounded-full bg-amber-500/15 px-3 py-1.5 text-xs font-bold text-amber-700 dark:text-amber-400">⚠️ ถ่ายตำหนิ</button>
 <button onclick="shootKind('มุมเพิ่มเติม')" class="tapscale rounded-full bg-black/5 px-3 py-1.5 text-xs font-semibold dark:bg-white/10">📷 มุมอื่น</button>
 <button onclick="pickGallery()" class="tapscale rounded-full bg-black/5 px-3 py-1.5 text-xs font-semibold dark:bg-white/10">🗂️ จากอัลบั้ม</button></div>
 <div class="mt-1 text-[10px] text-slate-400">${imgs.length}/${MAX_PHOTOS} รูป</div>
 ${imgs.length?`<button onclick="analyzeTray()" class="tapscale mt-4 w-full rounded-2xl bg-gradient-to-br from-brand-400 to-teal-600 py-3.5 text-base font-extrabold text-white shadow-glow">🔍 ให้ AI วิเคราะห์ (${imgs.length} รูป)</button>
 ${done<list.length?`<div class="mt-1.5 text-center text-[11px] text-amber-600">ยังขาด ${list.length-done} รูปในรายการ — วิเคราะห์ได้เลย แต่ผลเช็คของแท้จะมั่นใจน้อยลง</div>`:''}`:''}`);}
function renderTray(){const R=document.getElementById('result');if(!R)return;R.innerHTML=Tray();if(window.lucide)lucide.createIcons();}
function analyzeTray(){if(!imgs.length)return toast('ถ่ายรูปก่อน');
 const order=[...shotList(),DEFECT];const idx=imgs.map((_,i)=>i).sort((a,b)=>{const A=order.indexOf(labels[a]),B=order.indexOf(labels[b]);return (A<0?99:A)-(B<0?99:B)||a-b;});
 imgs=idx.map(i=>imgs[i]);thumbs=idx.map(i=>thumbs[i]);labels=idx.map(i=>labels[i]);photoWarn=idx.map(i=>photoWarn[i]);
 const R=document.getElementById('result');if(R)R.innerHTML='';renderDrop(true);window.scrollTo({top:0,behavior:'smooth'});runScan();}
""")

# 3) ช่องเลือกจากอัลบั้ม + ถ่ายได้หลายรูปต่อครั้ง
rep("""<input type="file" id="f_img" accept="image/*" capture="environment" class="hidden" onchange="upload(this)">""",
"""<input type="file" id="f_img" accept="image/*" capture="environment" class="hidden" onchange="upload(this)">
 <input type="file" id="f_gal" accept="image/*" multiple class="hidden" onchange="upload(this)">""")
# 4) วาดถาดรูปเมื่อกลับมาที่หน้าสแกน
rep("""<div id="result" class="space-y-3 mt-6 text-left">${ana?Result(ana):''}</div>""",
    """<div id="result" class="space-y-3 mt-6 text-left">${ana?Result(ana):Tray()}</div>""")
# 5) ข้อความบนปุ่มกล้อง
rep("""<div class="font-bold text-base">แตะเพื่อถ่ายรูป</div>""",
    """<div class="font-bold text-base">แตะเพื่อถ่ายรูปแรก</div>
  <div class="text-[11px] font-medium opacity-90">${(SHOTS[shotCat]||SHOTS.generic)[0]} — แล้วถ่ายตามรายการด้านล่าง</div>""")
# 6) ปุ่มกล้องใหญ่ = ถ่ายรูปถัดไปในรายการ
rep('''<div onclick="document.getElementById('f_img').click()" ''','''<div onclick="ana?document.getElementById('f_img').click():shootNext()" ''')
# 6b) ถาดว่าง: แตะปุ่มกล้องใหญ่ = ถ่ายเพิ่ม (มีรูปบนปุ่มแล้ว)
rep("""function renderDrop(loading,msg){const d=document.getElementById('drop');if(!d)return;""",
"""function renderDrop(loading,msg){const d=document.getElementById('drop');if(!d)return;
 if(!ana&&imgs.length&&!loading){d.innerHTML=`<img src="${thumbs[thumbs.length-1]}" class="absolute inset-0 h-full w-full object-cover opacity-50"><div class="relative z-10 mx-4 rounded-2xl bg-black/60 px-4 py-2 text-center text-sm font-bold text-white">📷 แตะเพื่อถ่าย<br><span class="text-base">${nextShot()||'ตำหนิ/มุมอื่น'}</span></div>`;return;}""")
open('deal-hunter-v2.html','w',encoding='utf-8').write(s)
print('patch6 ok')
