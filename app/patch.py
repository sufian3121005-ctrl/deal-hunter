import re,sys
s=open('orig.html',encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n<1: sys.exit('NOT FOUND: '+old[:80])
    s=s.replace(old,new,count)

# ---- title
rep('<title>AI Deal Hunter</title>','<title>Deal Hunter v2</title>')

# ---- new categories
rep("const CAT={'tools.power'","""const CAT={'apparel.vintage':{th:'เสื้อวินเทจ',icon:'shirt',hrs:.5,liq:65,fee:5,transport:5,fake:40,repair:10,days:14,decay:0.3,check:['ป้ายคอ','ตะเข็บเดี่ยวปลายแขน/ชาย','ปีลิขสิทธิ์ใต้ลาย','รู/คราบ/ขนาดจริง']},
'shoes.brand':{th:'รองเท้าแบรนด์',icon:'footprints',hrs:.5,liq:75,fee:6,transport:10,fake:70,repair:20,days:10,decay:0.8,check:['ป้ายในลิ้น/รหัสรุ่น','ตะเข็บ/กาว','พื้นสึก','กล่อง']},
'tools.power'""")

# ---- sell channels (inserted before CATALOG)
rep("const CATALOG=[","""/* ช่องทางขาย: fee = ค่าธรรมเนียมโดยประมาณ (%) ship = ค่าส่ง/แพ็กโดยประมาณ (บาท) mul = ราคาขายเทียบราคาตลาดไทย — ตัวเลขประมาณการ ปรับได้ตามจริง */
const CHANNELS={
 fb:{n:'กลุ่ม Facebook / Marketplace',fee:0,ship:0,mul:1,speed:'เร็ว',tip:'ลงกลุ่มเฉพาะทางของหมวดนี้ นัดรับในพื้นที่'},
 shopee:{n:'Shopee / Lazada',fee:10,ship:40,mul:1.05,speed:'กลาง',tip:'คนค้นเยอะ เหมาะของส่งพัสดุง่าย'},
 live:{n:'TikTok / IG Live',fee:5,ship:40,mul:1.15,speed:'เร็ว (ถ้ามีผู้ติดตาม)',tip:'ขายทีละหลายชิ้น เหมาะเสื้อผ้าวินเทจ'},
 ebay:{n:'eBay (ส่งต่างประเทศ)',fee:15,ship:450,mul:null,speed:'ช้า',tip:'คุ้มเฉพาะของหายากที่ราคา eBay สูงกว่าไทยมาก'},
 shop:{n:'ร้านรับซื้อ / ตลาดนัด',fee:0,ship:0,mul:.6,speed:'ได้เงินทันที',tip:'ใช้เมื่ออยากได้เงินสดเร็ว'}};
const CAT_CH={'apparel.vintage':['live','fb','ebay','shopee','shop'],'shoes.brand':['fb','shopee','live','shop'],'tools.power':['fb','shopee','shop'],'phone':['fb','shopee','shop'],generic:['fb','shopee','shop']};
function sellPlan(cat,mid,ebayMid){if(!mid&&!ebayMid)return[];const keys=CAT_CH[cat]||CAT_CH.generic;
 return keys.map(k=>{const c=CHANNELS[k];let sell=c.mul==null?(ebayMid||0):(mid||0)*c.mul;if(!sell)return null;
  const net=Math.round(sell*(1-c.fee/100)-c.ship);return{k,...c,sell:Math.round(sell),net};}).filter(Boolean).sort((a,b)=>b.net-a.net);}
const median=a=>{if(!a.length)return null;const s=[...a].sort((x,y)=>x-y);const m=Math.floor(s.length/2);return s.length%2?s[m]:(s[m-1]+s[m])/2;};

const CATALOG=[""")

# ---- replace upload + analyzeWithGemini
i=s.find('async function upload(el)'); i=i if i>=0 else s.find('function upload(el)'); j=s.find('function parseEv(){')
new_upload=r'''/* ============ Scan via backend (Cloudflare Worker) ============ */
let scan=null,thumbs=[];
const API={url(){try{return(localStorage.getItem('deal_api_url')||'').replace(/\/$/,'')}catch(e){return''}},key(){try{return localStorage.getItem('deal_app_key')||''}catch(e){return''}}};
function saveSetup(){localStorage.setItem('deal_api_url',V('s_url'));localStorage.setItem('deal_app_key',V('s_key'));toast('บันทึกการตั้งค่าแล้ว');render();}
function resizeImg(file,max,q){return new Promise(res=>{const r=new FileReader();r.onload=e=>{const i=new Image();i.onload=()=>{const c=document.createElement('canvas');const s=Math.min(1,max/Math.max(i.width,i.height));
 c.width=i.width*s;c.height=i.height*s;c.getContext('2d').drawImage(i,0,0,c.width,c.height);res(c.toDataURL('image/jpeg',q));};i.src=e.target.result};r.readAsDataURL(file)});}
async function upload(el,more){const files=[...el.files];if(!files.length)return;
 if(!more){imgs=[];thumbs=[];scan=null;ana=null;pending=[];}
 for(const f of files.slice(0,5-imgs.length)){imgs.push(await resizeImg(f,1280,.82));thumbs.push(await resizeImg(f,400,.7));}
 el.value='';renderDrop(true);await runScan();}
function renderDrop(loading,msg){const d=document.getElementById('drop');if(!d)return;
 d.innerHTML=(thumbs[0]?`<img src="${thumbs[0]}" class="absolute inset-0 h-full w-full object-cover ${loading?'opacity-50':''}">`:'')+
 (loading?`<div class="relative z-10 rounded-full bg-black/50 px-4 py-2 text-sm font-bold text-white animate-pulse">${msg||'AI กำลังดูรูป...'}</div>`:'')+
 (thumbs.length>1?`<div class="absolute bottom-3 left-3 z-10 flex gap-1">${thumbs.slice(1).map(t=>`<img src="${t}" class="h-10 w-10 rounded-lg object-cover ring-2 ring-white">`).join('')}</div>`:'');}
async function runScan(){
 if(!API.url()){render();toast('ตั้งค่าเซิร์ฟเวอร์ก่อนครับ');return;}
 renderDrop(true,imgs.length>1?`AI กำลังเช็ค ${imgs.length} รูป...`:'AI กำลังดูรูป...');
 try{
  const r=await fetch(API.url()+'/api/scan',{method:'POST',headers:{'content-type':'application/json','x-app-key':API.key()},body:JSON.stringify({images:imgs,hint:{name:V('f_name')}})});
  let d;try{d=await r.json()}catch(e){throw new Error('เซิร์ฟเวอร์ตอบกลับผิดรูปแบบ ('+r.status+')')}
  if(!r.ok||d.error)throw new Error(d.error||('HTTP '+r.status));
  scan=d;Store.trackAI(true);
  const it=d.item||{};
  [['f_name',it.name],['f_brand',it.brand],['f_model',it.model]].forEach(([k,v])=>{const e=document.getElementById(k);if(e&&v)e.value=v;});
  if(it.condition)setCond(it.condition);
  const ev=(d.market&&d.market.evidence)||[];const th=ev.filter(e=>e.market==='th');const eb=ev.filter(e=>e.market==='ebay');
  scan.ebayMid=median(eb.map(e=>e.price));
  const use=th.length>=2?th:ev;
  pending=use.map(e=>({id:uid(),price:e.price,type:e.type,note:(e.market==='ebay'?'eBay · ':'')+(e.title||''),use:true,url:e.url}));
  if(!pending.length&&d.ai_estimate&&d.ai_estimate.mid){const a=d.ai_estimate;pending=[a.low,a.mid,a.high].filter(Boolean).map(p=>({id:uid(),price:p,type:'estimate',note:'ประเมินโดย AI',use:true}));}
  const fe=document.getElementById('f_ev');if(fe)fe.value=pending.map(p=>`${p.type==='sold'?'ขายแล้ว ':''}${p.note.slice(0,50)} ${p.price}`).join('\n');
  rerenderEv();renderDrop(false);
  if(V('f_price')||V('q_price'))analyze();else askPrice();
 }catch(e){console.error(e);renderDrop(false);
  const R=document.getElementById('result');if(R)R.innerHTML=Card(`<div class="text-sm font-bold text-rose-500">สแกนไม่สำเร็จ</div><div class="mt-1 text-xs text-slate-500">${e.message}</div>
  <button onclick="runScan()" class="tapscale mt-3 w-full rounded-xl bg-black/5 py-2 text-xs font-semibold">ลองใหม่</button>`,'ring-1 ring-rose-500/30');}}
function askPrice(){const R=document.getElementById('result');const it=scan&&scan.item||{};
 R.innerHTML=Card(`<div class="text-xs text-slate-500">AI ระบุว่าเป็น</div><div class="text-base font-extrabold">${it.name||'สินค้า'}</div>
 <div class="text-xs text-slate-500">${[it.brand,it.model,it.era].filter(Boolean).join(' · ')}</div>
 <label class="mt-3 mb-1.5 block text-[12px] font-medium text-slate-500">แม่ค้าขายราคาเท่าไหร่ (บาท)</label>
 <div class="flex gap-2"><input id="ask_price" type="number" inputmode="numeric" class="flex-1 rounded-xl border-0 bg-black/[.04] px-3.5 py-2.5 text-lg font-bold ring-1 ring-black/5 focus:ring-2 focus:ring-brand-500">
 <button onclick="const v=V('ask_price');if(!v)return toast('กรอกราคาก่อน');document.getElementById('f_price').value=v;const q=document.getElementById('q_price');if(q)q.value=v;analyze()" class="tapscale rounded-xl bg-brand-500 px-5 text-sm font-bold text-white">ดูผล</button></div>`,'ring-2 ring-brand-500/30');
 setTimeout(()=>{const e=document.getElementById('ask_price');if(e)e.focus()},100);}
const AUTHM={pass:{l:'ผ่านการเช็คเบื้องต้น',c:'text-emerald-500',bg:'bg-emerald-500/10 ring-emerald-500/30',e:'🟢'},suspicious:{l:'ยังไม่แน่ใจ — ต้องเช็คเพิ่ม',c:'text-amber-500',bg:'bg-amber-500/10 ring-amber-500/30',e:'🟡'},high_risk:{l:'เสี่ยงของปลอม/ไม่ตรงปก',c:'text-rose-500',bg:'bg-rose-500/10 ring-rose-500/30',e:'🔴'}};
const CHK={pass:['✓','text-emerald-500'],fail:['✗','text-rose-500'],unclear:['?','text-amber-500'],not_photographed:['📷','text-slate-400']};
function AuthCard(a){const au=a.auth;if(!au)return'';const m=AUTHM[au.level]||AUTHM.suspicious;
 return Card(`${Section('เช็คของแท้ / ตรงปก')}<div class="text-base font-extrabold ${m.c}">${m.e} ${m.l}</div>
 ${au.summary?`<div class="mt-1 text-xs text-slate-500">${au.summary}</div>`:''}
 <div class="mt-3 space-y-1.5">${(au.checks||[]).map(c=>{const k=CHK[c.status]||CHK.unclear;return`<div class="flex gap-2 text-[12px]"><span class="w-4 shrink-0 text-center font-bold ${k[1]}">${k[0]}</span><div class="min-w-0"><div>${c.point}</div>${c.note?`<div class="text-[11px] text-slate-500">${c.note}</div>`:''}</div></div>`}).join('')}</div>
 ${(au.red_flags||[]).length?`<div class="mt-2 rounded-xl bg-rose-500/10 p-2.5 text-[11px] text-rose-500">${au.red_flags.map(f=>'🚩 '+f).join('<br>')}</div>`:''}
 ${(au.level!=='pass'||(au.checks||[]).some(c=>c.status==='not_photographed'))&&(a.needPhotos||[]).length?`<div class="mt-3 rounded-xl bg-black/[.03] p-2.5 text-[12px] dark:bg-white/[.03]"><b>ถ่ายเพิ่มเพื่อเช็คให้ชัด:</b><br>${a.needPhotos.map(p=>'• '+p).join('<br>')}</div>
 <button onclick="document.getElementById('f_img2').click()" class="tapscale mt-2 w-full rounded-xl bg-amber-500 py-2.5 text-sm font-bold text-white">📷 ถ่ายจุดเช็คเพิ่ม แล้วสแกนใหม่</button>`:''}
 <div class="mt-2 text-[10px] text-slate-400">ประเมินจากรูปเท่านั้น ไม่ใช่ใบรับรองของแท้ · ของราคาสูงควรให้ผู้เชี่ยวชาญเช็คก่อนซื้อ</div>`,`ring-1 ${m.bg}`);}
function MarketLinks(a){const L=a.links||[];if(!L.length)return'';
 return Card(`${Section('ตลาดขายกันที่ไหน (ประกาศที่ใกล้เคียง)')}<div class="space-y-1.5">${L.map(l=>`<a href="${l.url}" target="_blank" rel="noopener" class="flex items-center justify-between gap-2 rounded-xl bg-black/[.03] px-3 py-2 text-[12px] dark:bg-white/[.03]"><span class="min-w-0 flex-1 truncate">${l.title||l.url}<span class="block text-[10px] text-slate-500">${l.host||''}${l.type==='sold'?' · ขายแล้ว':''}</span></span>${l.price?`<b class="shrink-0">${money(l.price)}</b>`:''}</a>`).join('')}</div>`);}
function SellCard(a){const P=a.sellPlan||[];if(!P.length)return'';const best=P[0];
 return Card(`${Section('ขายที่ไหนดีที่สุด')}<div class="text-sm">แนะนำ <b class="text-brand-500">${best.n}</b> · ได้สุทธิประมาณ <b>${money(best.net)}</b></div>
 <div class="mt-2 space-y-1.5">${P.map((p,i)=>`<div class="rounded-xl ${i===0?'bg-brand-500/10 ring-1 ring-brand-500/30':'bg-black/[.03] dark:bg-white/[.03]'} px-3 py-2 text-[12px]"><div class="flex justify-between gap-2"><b>${p.n}</b><span>ตั้งขาย ${money(p.sell)} → สุทธิ <b>${money(p.net)}</b></span></div><div class="text-[11px] text-slate-500">${p.speed} · ${p.tip}</div></div>`).join('')}</div>
 <div class="mt-2 text-[10px] text-slate-400">ค่าธรรมเนียม/ค่าส่งเป็นค่าประมาณ ปรับได้ในโค้ด (CHANNELS)</div>`);}
'''
s=s[:i]+new_upload+s[j:]

# ---- FindDeal: setup card, multi-photo input, quick price
rep('''<input type="file" id="f_img" accept="image/*" capture="environment" class="hidden" onchange="upload(this)">''',
'''<input type="file" id="f_img" accept="image/*" capture="environment" class="hidden" onchange="upload(this)">
 <input type="file" id="f_img2" accept="image/*" capture="environment" multiple class="hidden" onchange="upload(this,true)">
 <div class="mx-auto max-w-sm text-left">${Inp('q_price','ราคาที่แม่ค้าบอก (฿) — กรอกก่อนหรือหลังถ่ายก็ได้','เช่น 300','','number').replace('<input ','<input inputmode="numeric" oninput="const f=document.getElementById(\\'f_price\\');if(f)f.value=this.value" ')}</div>
 ${API.url()?'':Card(`<div class="text-left"><div class="text-sm font-bold">ตั้งค่าเซิร์ฟเวอร์ครั้งแรก</div><div class="mt-1 text-xs text-slate-500">ใส่ลิงก์ Worker ที่ติดตั้งตามคู่มือ (ครั้งเดียว)</div>
 <div class="mt-3 space-y-2">${Inp('s_url','ลิงก์ Worker','https://deal-hunter.xxx.workers.dev')}${Inp('s_key','รหัสแอป (APP_KEY)','')}</div>
 <button onclick="saveSetup()" class="tapscale mt-3 w-full rounded-xl bg-brand-500 py-2.5 text-sm font-bold text-white">บันทึก</button></div>`,'ring-2 ring-amber-500/40')}''')
rep('''${imgs.length?imgs.map(s=>`<img src="${s}" class="absolute inset-0 h-full w-full object-cover">`).join(''):`''',
'''${thumbs.length?`<img src="${thumbs[0]}" class="absolute inset-0 h-full w-full object-cover">`:`''')
rep('AI จะประเมินราคาให้เอง','AI บอกราคา · เช็คของแท้ · ที่ขาย')
# settings link at end of FindDeal
rep(''' <button onclick="analyze()" class="tapscale w-full rounded-2xl bg-slate-800 py-3 text-sm font-bold text-white dark:bg-white dark:text-slate-900">วิเคราะห์ใหม่ด้วยข้อมูลที่แก้</button>
 </div></details>''',''' <button onclick="analyze()" class="tapscale w-full rounded-2xl bg-slate-800 py-3 text-sm font-bold text-white dark:bg-white dark:text-slate-900">วิเคราะห์ใหม่ด้วยข้อมูลที่แก้</button>
 </div></details>
 ${API.url()?`<button onclick="localStorage.removeItem('deal_api_url');render()" class="mt-2 text-[11px] text-slate-400 underline">⚙ เปลี่ยนการตั้งค่าเซิร์ฟเวอร์</button>`:''}''')

# ---- analyze: price, category from scan, auth effect, extra fields
rep("price:+V('f_price'),km:","price:+V('f_price')||+V('q_price'),km:")
rep("const id=AI.identify({name:raw.name,brand:raw.brand,model:raw.model});",
"""const id=AI.identify({name:raw.name,brand:raw.brand,model:raw.model});
 if(scan&&scan.item){const it=scan.item;if(CAT[it.category])id.cat=it.category;if(!id.seed){id.name=it.name||id.name;id.brand=it.brand||id.brand;id.model=it.model||id.model;id.conf=it.id_confidence||id.conf;}}""")
rep("const sim=Learn.similar(id.brand,id.model);const usedAI=sim.exact.length<3;Store.trackAI(usedAI);",
    "const sim=Learn.similar(id.brand,id.model);const usedAI=!!scan;")
rep("let dec2=Engine.decide(","""const auth=scan&&scan.auth;
 if(auth&&auth.level==='high_risk'){scoreFinal=Math.min(scoreFinal,35);sc.caps.push('เช็คของแท้: เสี่ยงสูง → จำกัดคะแนนที่ 35');}
 let dec2=Engine.decide(""")
rep("const annualized=","""if(auth){if(auth.level==='high_risk'){dec2.decision='PASS';dec2.why.unshift('🔴 เช็คของแท้: เสี่ยงของปลอม/ไม่ตรงปก'+(auth.summary?' — '+auth.summary:''));}
 else if(auth.level==='suspicious'&&dec2.decision==='BUY'){dec2.decision='NEGOTIATE';dec2.why.unshift('🟡 เช็คของแท้ยังไม่ครบ — ถ่ายจุดเช็คเพิ่มก่อนจ่ายเงิน');}}
 const annualized=""")
rep("img:imgs[0]||null,","img:thumbs[0]||null,auth:auth||null,needPhotos:scan?scan.need_photos:[],links:scan&&scan.market?scan.market.links:[],sellPlan:sellPlan(id.cat,val.target||val.mid,scan?scan.ebayMid:null),era:scan&&scan.item?scan.item.era:'',")

rep("hours:V('f_hours')||2,","hours:V('f_hours'),")
rep(",hours:raw.hours,rate:raw.rate,",",hours:raw.hours||(CAT[id.cat].hrs??2),rate:raw.rate,")
rep("${Inp('f_hours','ชม.ที่ใช้','2','2','number')}","${Inp('f_hours','ชม.ที่ใช้','อัตโนมัติ','','number')}")
s=s.replace('${b.e}',"${ic(b.e,'w-5 h-5 inline-block align-[-3px]')}")
rep("R.innerHTML=Result(ana);","R.innerHTML=Result(ana);if(window.lucide)lucide.createIcons();")
rep("why:[...dec2.why,...dec.why.slice(4)]","why:[...dec2.why,...dec.why.slice(5)]")
rep("const provenanceFlag=val.mid&&raw.price<val.mid*0.4&&!hasReceipt;","const provenanceFlag=val.mid&&raw.price>=1000&&raw.price<val.mid*0.4&&!hasReceipt;")
# ---- Result: insert cards
rep("${Card(`${Section('STEP 1 — ระบุสินค้า')}","${AuthCard(a)}\n ${Card(`${Section('STEP 1 — ระบุสินค้า')}")
rep("${Card(`${Section('STEP 3–4","${MarketLinks(a)}\n ${Card(`${Section('STEP 3–4")
rep("${Card(`${Section('📝 สคริปต์ต่อราคา'","${SellCard(a)}\n ${Card(`${Section('📝 สคริปต์ต่อราคา'")
rep("${Row('หมวด',CAT[a.cat].icon+' '+CAT[a.cat].th)}","${Row('หมวด',CAT[a.cat].th)}${a.era?Row('ยุค',a.era):''}")
# reset helpers
rep("ana=null;imgs=[];pending=[];toast('บันทึกดีลแล้ว')","ana=null;imgs=[];thumbs=[];scan=null;pending=[];toast('บันทึกดีลแล้ว')")
rep('''<button onclick="ana=null;render()"''','''<button onclick="ana=null;imgs=[];thumbs=[];scan=null;pending=[];render()"''')
# detail page category icon text
s=s.replace("CAT[d.cat].icon+' '+CAT[d.cat].th","CAT[d.cat].th")
# guard lucide latest -> pinned
s=s.replace('https://unpkg.com/lucide@latest/dist/umd/lucide.min.js','https://unpkg.com/lucide@0.460.0/dist/umd/lucide.min.js')
open('deal-hunter-v2.html','w',encoding='utf-8').write(s)
print('ok',len(s))
