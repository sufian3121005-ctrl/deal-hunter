import sys
s=open('deal-hunter-v2.html',encoding='utf-8').read()
def rep(old,new):
    global s
    if s.count(old)<1: sys.exit('NOT FOUND: '+old[:90])
    s=s.replace(old,new,1)

# หมวดยีนส์/เสื้อผ้าวินเทจ
rep("const CAT={'apparel.vintage':","const CAT={'apparel.football':{th:'เสื้อฟุตบอล',icon:'trophy',hrs:.5,liq:70,fee:5,transport:5,fake:65,repair:10,days:14,decay:.4,check:['รหัสสินค้า','ป้ายคอ','โลโก้/ตราสโมสร','jock tag']},'apparel.denim':{th:'ยีนส์/แจ็คเก็ตวินเทจ',icon:'scissors',hrs:.5,liq:60,fee:5,transport:15,fake:35,repair:15,days:18,decay:.3,check:['แท็บแดง','ป้ายหลังเอว','ป้ายวิธีซัก/รหัสวันที่','ผ้าริม/หมุด']},\n'apparel.vintage':")
rep("const CAT_CH={","const CAT_CH={'apparel.football':['fb','live','shopee','ebay','shop'],'apparel.denim':['live','fb','ebay','shopee','shop'],")
rep("const HAND={","const HAND={\n 'apparel.football':[{q:'ค้นรหัสสินค้าใน Google แล้วขึ้นเสื้อตัวนี้เป๊ะ (ทีม/ปี/เหย้า-เยือน)',t:'auth'},{q:'ด้านในหลังตรา/โลโก้ไม่มีวัสดุรองเกินมาก',t:'auth'},{q:'ผู้ขายไม่ได้เรียกว่า \"เกรดเอ/เกรดไทย/เกรดนักเตะ\"',t:'auth'},{q:'เบอร์/ชื่อ/สปอนเซอร์ไม่ร่อน ไม่ละลาย',t:'cond'},{q:'ไม่มีขุย ด้ายดึง หรือรู',t:'cond'}],\n 'apparel.denim':[{q:'ผ้าหนักแน่น ไม่บางย้วยแบบยีนส์ใหม่ราคาถูก',t:'auth'},{q:'ซีดตามการใช้งาน (หนวดแมว/รังผึ้ง) ไม่ใช่ซีดสม่ำเสมอแบบฟอก',t:'auth'},{q:'ป้าย/แท็บเก่าพอๆ กับตัวผ้า ไม่ใหม่เอี่ยม',t:'auth'},{q:'เป้า ก้น ขอบขา ไม่ขาด',t:'cond'},{q:'ซิป/กระดุมใช้ได้ครบ',t:'cond'}],")

# เก็บ kb ลงดีล
rep("lesson:scan?scan.lesson:'',","lesson:scan?scan.lesson:'',kb:scan?scan.kb_matches||[]:[],")

# การ์ดฐานความรู้ในผลสแกน
rep("function DefectCard(a){",r'''function KBCard(a){const K=a.kb||[];if(!K.length)return'';
 return Card(`${Section('📖 จากฐานความรู้ของระบบ')}<div class="space-y-2.5">${K.map(k=>`<div class="rounded-xl bg-black/[.03] p-2.5 text-[12px] dark:bg-white/[.03]">
 <div class="font-bold">${k.title}${k.era?` <span class="font-normal text-slate-500">· ${k.era}</span>`:''}${k.confidence==='general'?' <span class="text-[10px] font-normal text-amber-600">(ความรู้ทั่วไป)</span>':''}</div>
 <div class="mt-1 space-y-0.5 text-slate-600 dark:text-slate-300">${k.cues.map(c=>`<div>• ${c}</div>`).join('')}</div>
 ${k.red_flags&&k.red_flags.length?`<div class="mt-1 text-rose-500">${k.red_flags.map(r=>'⚠ '+r).join('<br>')}</div>`:''}
 ${k.value_notes?`<div class="mt-1 text-emerald-600">💰 ${k.value_notes}</div>`:''}
 ${k.source?`<a href="${k.source}" target="_blank" rel="noopener" class="mt-1 inline-block text-[10px] text-sky-600 underline">แหล่งอ้างอิง</a>`:''}</div>`).join('')}</div>
 <button onclick="go('/kb')" class="mt-2 text-[11px] text-slate-500 underline">เปิดคู่มือดูของทั้งหมด</button>`);}
function DefectCard(a){''')
rep("${AuthCard(a)}\n ${DefectCard(a)}","${AuthCard(a)}\n ${KBCard(a)}\n ${DefectCard(a)}")

# ลิงก์คู่มือที่หน้าสแกน
rep("${HuntChips()}","<button onclick=\"go('/kb')\" class=\"tapscale mx-auto -mt-2 block text-[11px] font-semibold text-sky-600 underline\">📖 คู่มือดูของวินเทจ (ป้ายแต่ละยุค, จุดจับของปลอม)</button>\n ${HuntChips()}")

# หน้า คู่มือ
block=r'''
/* ============ คู่มือดูของ (ฐานความรู้) ============ */
let KBD=null,kbQ='';
async function loadKB(){if(KBD)return;try{const c=localStorage.getItem('deal_kb');if(c)KBD=JSON.parse(c);}catch(e){}
 if(!API.url()){if(cur==='/kb')render();return;}
 try{const r=await fetch(API.url()+'/api/kb',{headers:{'x-app-key':API.key()}});const d=await r.json();if(d.entries){KBD=d.entries;try{localStorage.setItem('deal_kb',JSON.stringify(KBD))}catch(e){}}}catch(e){}
 if(cur==='/kb')render();}
function kbFilter(v){kbQ=v;const el=document.getElementById('kbList');if(el)el.innerHTML=KBList();}
const KBKIND={trend:'กระแสตอนนี้',market:'ตลาดในไทย',rule:'กฎทั่วไป',tag:'ป้ายเสื้อแต่ละยี่ห้อ',genre:'ประเภทที่ตลาดต้องการ',brand:'แบรนด์'};
function KBList(){if(!KBD)return'<div class="py-6 text-center text-xs text-slate-500">กำลังโหลด... (ต้องตั้งค่าเซิร์ฟเวอร์ก่อน)</div>';
 const q=kbQ.trim().toLowerCase();const L=KBD.filter(e=>!q||[e.title,e.brand,e.era,...e.keywords,...e.cues,...e.red_flags].join(' ').toLowerCase().includes(q));
 if(!L.length)return'<div class="py-6 text-center text-xs text-slate-500">ไม่พบ</div>';
 const cats=[['apparel.vintage','👕 เสื้อยืด/เสื้อวงวินเทจ'],['apparel.football','⚽ เสื้อฟุตบอล'],['apparel.denim','👖 ยีนส์/แจ็คเก็ต/เสื้อผ้าวินเทจ']];
 return cats.map(([c,lab])=>{const G=L.filter(e=>e.category===c);if(!G.length)return'';
  return`<div class="text-sm font-extrabold">${lab}</div>`+['trend','market','rule','genre','brand','tag'].map(k=>{const X=G.filter(e=>e.kind===k);if(!X.length)return'';
   return`<div class="mt-2 text-[11px] font-semibold uppercase tracking-wide text-slate-500">${KBKIND[k]}</div>`+X.map(e=>`<details class="rounded-2xl glass p-3 text-[12px]"><summary class="cursor-pointer font-bold">${e.title}${e.era?` <span class="font-normal text-slate-500">· ${e.era}</span>`:''}</summary>
   <div class="mt-2 space-y-0.5">${e.cues.map(c=>`<div>• ${c}</div>`).join('')}</div>
   ${e.red_flags.length?`<div class="mt-1.5 text-rose-500">${e.red_flags.map(r=>'⚠ '+r).join('<br>')}</div>`:''}
   ${e.value_notes?`<div class="mt-1.5 text-emerald-600">💰 ${e.value_notes}</div>`:''}
   <div class="mt-1.5 text-[10px] text-slate-400">${e.confidence==='general'?'ความรู้ทั่วไป ยังไม่ได้ยืนยันจากแหล่งอ้างอิง':''}${(e.sources||[]).map((u,i)=>` <a href="${u}" target="_blank" rel="noopener" class="text-sky-600 underline">แหล่ง ${i+1}</a>`).join('')}</div></details>`).join('<div class="h-1.5"></div>')}).join('')}).join('<div class="h-4"></div>');}
function KBPage(){loadKB();return`<div class="pagefade space-y-3"><button onclick="go('/find')" class="text-xs font-medium text-slate-500">← กลับหน้าสแกน</button>
 <h1 class="text-2xl font-extrabold tracking-tight">📖 คู่มือดูของวินเทจ</h1>
 <div class="text-[11px] text-slate-400">อัปเดตล่าสุด: ${(KBD&&KBD.length)?KBD.length+' หัวข้อ':''}</div>
 <div class="text-xs text-slate-500">ฐานความรู้เดียวกับที่ AI ใช้ตัดสิน เปิดดูหรือค้นได้ระหว่างเดินตลาด</div>
 <input oninput="kbFilter(this.value)" value="${kbQ}" placeholder="ค้น เช่น nirvana, แมนยู, รหัสสินค้า, big e, ป้ายปลอม" class="w-full rounded-xl border-0 bg-black/[.04] px-3.5 py-2.5 text-sm ring-1 ring-black/5 focus:ring-2 focus:ring-brand-500">
 <div id="kbList" class="space-y-1.5">${KBList()}</div></div>`;}
'''
rep("/* ============ router","%s\n/* ============ router" % block)
rep("cur==='/batch'?BatchPage():","cur==='/batch'?BatchPage():cur==='/kb'?KBPage():")

# ตั้งค่า: แสดงการ์ดเมื่อยังไม่มีลิงก์หรือรหัสแอป, เติมลิงก์ที่สคริปต์ติดตั้งใส่ไว้ให้
rep("${API.url()?'':Card(`<div class=\"text-left\"><div class=\"text-sm font-bold\">ตั้งค่าเซิร์ฟเวอร์ครั้งแรก","${API.url()&&API.key()?'':Card(`<div class=\"text-left\"><div class=\"text-sm font-bold\">ตั้งค่าเซิร์ฟเวอร์ครั้งแรก")
rep("${Inp('s_url','ลิงก์ Worker','https://deal-hunter.xxx.workers.dev')}${Inp('s_key','รหัสแอป (APP_KEY)','')}","${Inp('s_url','ลิงก์ Worker','https://deal-hunter.xxx.workers.dev',API.url())}${Inp('s_key','รหัสแอป (ดูในไฟล์ ข้อมูลเข้าระบบ.txt)','')}")
rep("onclick=\"localStorage.removeItem('deal_api_url');render()\"","onclick=\"localStorage.removeItem('deal_api_url');localStorage.removeItem('deal_app_key');render()\"")
rep("if(!API.url()){render();toast('ตั้งค่าเซิร์ฟเวอร์ก่อนครับ');return;}","if(!API.url()||!API.key()){render();toast('ใส่ลิงก์และรหัสแอปก่อนครับ');return;}")

open('deal-hunter-v2.html','w',encoding='utf-8').write(s)
print('ok',len(s))
