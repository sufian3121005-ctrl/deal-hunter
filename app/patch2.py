import sys
s=open('deal-hunter-v2.html',encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    if s.count(old)<1: sys.exit('NOT FOUND: '+old[:90])
    s=s.replace(old,new,count)

# ---------- categories: luxury ----------
rep("'tools.power':{th:'เครื่องมือช่าง'","'luxury':{th:'กระเป๋า/นาฬิกาแบรนด์เนม',icon:'gem',hrs:.5,liq:60,fee:8,transport:10,fake:90,repair:20,days:20,decay:.5,check:['รหัสผลิต','ฟอนต์/โลโก้','อะไหล่โลหะ','ใบรับประกัน']},\n'tools.power':{th:'เครื่องมือช่าง'")
rep("const CAT_CH={","const CAT_CH={luxury:['fb','shop'],")

# ---------- icons shown as text (old bug) ----------
s=s.replace("${CAT[s.cat].icon}","${ic(CAT[s.cat].icon,'w-5 h-5')}")
s=s.replace("${CAT[d.cat].icon}","${ic(CAT[d.cat].icon,'w-10 h-10')}")
s=s.replace("${CAT[p.cat].icon}","${ic(CAT[p.cat].icon,'w-4 h-4')}")

# ---------- state ----------
rep("let scan=null,thumbs=[];","let scan=null,thumbs=[],labels=[],hand={},nextLabel='',refsCache={},confirmRef=false;")

# ---------- upload: labels + photo quality ----------
i=s.find('async function upload(el,more)'); j=s.find('function renderDrop(')
s=s[:i]+r'''async function upload(el,more){const files=[...el.files];if(!files.length)return;
 if(!more){imgs=[];thumbs=[];labels=[];scan=null;ana=null;pending=[];hand={};}
 const bad=[];
 for(const f of files.slice(0,6-imgs.length)){const big=await resizeImg(f,1280,.82);const q=await photoCheck(big);
  imgs.push(big);thumbs.push(await resizeImg(f,400,.7));labels.push(more?(nextLabel||'มุมเพิ่มเติม'):'ตัวสินค้าเต็มชิ้น');if(!q.ok)bad.push({i:imgs.length-1,problem:q.problem});}
 el.value='';nextLabel='';
 if(bad.length){renderDrop(false);showBadPhoto(bad,more);return;}
 if(more){renderDrop(false);if(ana){ana.extraPending=(ana.extraPending||0)+1;}const R=document.getElementById('result');if(R&&ana){R.innerHTML=Result(ana);if(window.lucide)lucide.createIcons();}toast('เพิ่มรูปแล้ว — ถ่ายจุดอื่นต่อ หรือกดสแกนใหม่');return;}
 renderDrop(true);await runScan();}
/* เช็ครูปเบื้องต้นในเครื่อง: มืด / เบลอ (ไม่ใช้โควตา AI) */
function photoCheck(dataUrl){return new Promise(res=>{const im=new Image();im.onload=()=>{const W=200,H=Math.max(1,Math.round(im.height*200/im.width));
 const c=document.createElement('canvas');c.width=W;c.height=H;const x=c.getContext('2d');x.drawImage(im,0,0,W,H);const p=x.getImageData(0,0,W,H).data;
 const g=new Float32Array(W*H);let sum=0;for(let k=0;k<W*H;k++){g[k]=.299*p[k*4]+.587*p[k*4+1]+.114*p[k*4+2];sum+=g[k];}
 const mean=sum/(W*H);let m=0,m2=0,n=0;for(let yy=1;yy<H-1;yy++)for(let xx=1;xx<W-1;xx++){const k=yy*W+xx;const L=4*g[k]-g[k-1]-g[k+1]-g[k-W]-g[k+W];m+=L;m2+=L*L;n++;}
 const v=n?m2/n-(m/n)**2:999;
 res(mean<35?{ok:false,problem:'มืดเกินไป'}:v<18?{ok:false,problem:'เบลอหรือไม่ชัด'}:{ok:true,v,mean});};im.onerror=()=>res({ok:true});im.src=dataUrl;});}
function showBadPhoto(bad,more){const R=document.getElementById('result');if(!R)return;
 R.innerHTML=Card(`<div class="text-sm font-bold text-amber-500">📷 รูป${bad.map(b=>' '+(b.i+1)).join(',')} ${bad[0].problem}</div>
 <div class="mt-1 text-xs text-slate-500">AI อ่านป้ายหรือตะเข็บจากรูปแบบนี้ได้ไม่แม่น ถ่ายใหม่ให้ใกล้และสว่างขึ้นจะได้ผลดีกว่า</div>
 <div class="mt-3 flex gap-2"><button onclick="retakeBad(${JSON.stringify(bad.map(b=>b.i))},${more?'true':'false'})" class="tapscale flex-1 rounded-xl bg-amber-500 py-2.5 text-sm font-bold text-white">ถ่ายใหม่</button>
 <button onclick="${more?'renderAfterAdd()':'renderDrop(true);runScan()'}" class="tapscale flex-1 rounded-xl bg-black/5 py-2.5 text-sm font-semibold">ใช้รูปนี้ต่อ</button></div>`,'ring-2 ring-amber-500/40');}
function retakeBad(idx,more){const lab=labels[idx[0]];[...idx].sort((a,b)=>b-a).forEach(i=>{imgs.splice(i,1);thumbs.splice(i,1);labels.splice(i,1);});
 renderDrop(false);if(more||imgs.length){nextLabel=lab;document.getElementById('f_img2').click();}else document.getElementById('f_img').click();}
function renderAfterAdd(){renderDrop(false);const R=document.getElementById('result');if(R&&ana){R.innerHTML=Result(ana);if(window.lucide)lucide.createIcons();}}
function shootCheckpoint(cp){nextLabel=cp;document.getElementById('f_img2').click();}
function rescanAll(){if(ana)ana.extraPending=0;renderDrop(true);runScan();window.scrollTo({top:0,behavior:'smooth'});}
'''+s[j:]

# ---------- runScan: labels + hand, applyScan refactor, offline queue ----------
i=s.find('async function runScan(){'); j=s.find('function askPrice(')
s=s[:i]+r'''async function callScan(images,lbls,hintObj){
 const r=await fetch(API.url()+'/api/scan',{method:'POST',headers:{'content-type':'application/json','x-app-key':API.key()},body:JSON.stringify({images,labels:lbls,hint:hintObj||{}})});
 let d;try{d=await r.json()}catch(e){throw new Error('เซิร์ฟเวอร์ตอบกลับผิดรูปแบบ ('+r.status+')')}
 if(!r.ok||d.error)throw new Error(d.error||('HTTP '+r.status));Store.trackAI(true);return d;}
const handList=()=>Object.entries(hand).map(([q,ok])=>({q,ok}));
function scanEvidence(d){const ev=(d.market&&d.market.evidence)||[];const th=ev.filter(e=>e.market==='th');const eb=ev.filter(e=>e.market==='ebay');
 d.ebayMid=median(eb.map(e=>e.price));const use=th.length>=2?th:ev;
 let p=use.map(e=>({id:uid(),price:e.price,type:e.type,note:(e.market==='ebay'?'eBay · ':'')+(e.title||''),use:true,url:e.url}));
 if(!p.length&&d.ai_estimate&&d.ai_estimate.mid){const a=d.ai_estimate;p=[a.low,a.mid,a.high].filter(Boolean).map(x=>({id:uid(),price:x,type:'estimate',note:'ประเมินโดย AI',use:true}));}
 return p;}
function applyScan(d){scan=d;const it=d.item||{};
 [['f_name',it.name],['f_brand',it.brand],['f_model',it.model]].forEach(([k,v])=>{const e=document.getElementById(k);if(e&&v)e.value=v;});
 if(it.condition)setCond(it.condition);pending=scanEvidence(d);
 const fe=document.getElementById('f_ev');if(fe)fe.value=pending.map(p=>`${p.type==='sold'?'ขายแล้ว ':''}${p.note.slice(0,50)} ${p.price}`).join('\n');
 if(document.getElementById('evList'))rerenderEv();
 Store.d.lessons=Store.d.lessons||[];if(d.lesson&&!Store.d.lessons.includes(d.lesson)){Store.d.lessons.unshift(d.lesson);Store.d.lessons=Store.d.lessons.slice(0,100);try{localStorage.setItem(Store.k,JSON.stringify(Store.d))}catch(e){}}
 loadRefs(it.category);}
async function runScan(){
 if(!API.url()){render();toast('ตั้งค่าเซิร์ฟเวอร์ก่อนครับ');return;}
 renderDrop(true,imgs.length>1?`AI กำลังเช็ค ${imgs.length} รูป...`:'AI กำลังดูรูป...');
 try{
  const d=await callScan(imgs,labels,{name:V('f_name'),hand:handList()});
  applyScan(d);renderDrop(false);
  if(V('f_price')||V('q_price')||(ana&&ana.price))analyze(ana&&ana.price&&!V('f_price')&&!V('q_price')?ana.price:undefined);else askPrice();
 }catch(e){console.error(e);renderDrop(false);
  const offline=!navigator.onLine||/Failed to fetch|NetworkError|Load failed/i.test(e.message);
  const R=document.getElementById('result');
  if(offline){await Batch.add(imgs[0],thumbs[0],+V('q_price')||null);
   if(R)R.innerHTML=Card(`<div class="text-sm font-bold text-amber-500">📶 ไม่มีสัญญาณเน็ต</div><div class="mt-1 text-xs text-slate-500">เก็บรูปไว้ในคิวสแกนรัวแล้ว ระบบจะสแกนให้อัตโนมัติเมื่อมีเน็ต</div>
   <button onclick="go('/batch')" class="tapscale mt-3 w-full rounded-xl bg-black/5 py-2 text-xs font-semibold">ดูคิว</button>`,'ring-1 ring-amber-500/30');return;}
  if(R)R.innerHTML=Card(`<div class="text-sm font-bold text-rose-500">สแกนไม่สำเร็จ</div><div class="mt-1 text-xs text-slate-500">${e.message}</div>
  <button onclick="runScan()" class="tapscale mt-3 w-full rounded-xl bg-black/5 py-2 text-xs font-semibold">ลองใหม่</button>`,'ring-1 ring-rose-500/30');}}
'''+s[j:]

# ---------- analyze: price override, defects, hand checks, category rules, fast mode ----------
rep("function analyze(){\n const raw={","function analyze(priceOverride){\n const raw={")
rep("price:+V('f_price')||+V('q_price'),km:","price:+priceOverride||+V('f_price')||+V('q_price'),km:")
rep("""const d0={cat:id.cat,""","""// ตำหนิ + เช็คด้วยมือ (สภาพ) → หักราคา
 const H=HAND[id.cat]||HAND.generic;const condFails=H.filter(h=>h.t==='cond'&&hand[h.q]===false).map(h=>h.q);const authFails=H.filter(h=>h.t==='auth'&&hand[h.q]===false).map(h=>h.q);
 const defects=[...((scan&&scan.defects)||[]),...condFails.map(q=>({what:'เช็คด้วยมือไม่ผ่าน: '+q,severity:'major',price_impact_pct:15}))];
 const condPenalty=(1-({new:1.15,like_new:1.08,good:1,fair:.85,poor:.6,unknown:.9}[cond]||1))*100;
 const aiDef=E.tier==='ai_only'?0:Math.max(0,((scan&&scan.defects)||[]).reduce((a,x)=>a+(+x.price_impact_pct||0),0)-Math.max(0,condPenalty));
 const defectPct=Math.min(50,aiDef+condFails.length*15);
 if(defectPct>0&&val.mid){const f=1-defectPct/100;['low','mid','high','fairBuy','maxBuy','target'].forEach(k=>{if(val[k])val[k]*=f;});}
 const d0={cat:id.cat,""")
rep("""const auth=scan&&scan.auth;""","""let auth=scan&&scan.auth?{...scan.auth}:null;
 if(auth&&authFails.length){auth.level='high_risk';auth.handFail=authFails;}
 const expertOk=H.some(h=>h.expert&&hand[h.q]===true);""")
rep("""const annualized=sc.roi""","""if(id.cat==='luxury'&&!expertOk&&dec2.decision!=='PASS'){dec2.decision='PASS';dec2.why.unshift('💎 แบรนด์เนม: มือใหม่ห้ามซื้อจากผลรูปอย่างเดียว ให้ผู้เชี่ยวชาญตรวจก่อน แล้วติ๊กในเช็คด้วยมือ');}
 if(id.cat==='phone'&&hand['เช็ค IMEI แล้ว ไม่ติดล็อก/ไม่ติดบัญชี']!==true&&dec2.decision==='BUY'){dec2.decision='NEGOTIATE';dec2.why.unshift('📱 ยังไม่ได้เช็ค IMEI/สถานะล็อก — เช็คก่อนจ่ายเงิน');}
 if(authFails.length)dec2.why.unshift('🔴 เช็คด้วยมือไม่ผ่าน: '+authFails.join(', '));
 if(defectPct>0)dec2.why.push(`🧵 ตำหนิ/สภาพ หักราคา ${defectPct.toFixed(0)}%`);
 const annualized=sc.roi""")
rep("era:scan&&scan.item?scan.item.era:'',","era:scan&&scan.item?scan.item.era:'',size:scan&&scan.item?scan.item.size:'',defects,defectPct,lesson:scan?scan.lesson:'',photoQuality:scan?scan.photo_quality:[],checkpoints:scan?scan.checkpoints:[],labels:[...labels],")
rep("const R=document.getElementById('result');\n const steps=","const R=document.getElementById('result');if(!R)return ana;\n const steps=")
rep("const tick=()=>{if(i<steps.length){","const tick=()=>{if(!window._fast&&i<steps.length){")
rep("R.innerHTML=Result(ana);if(window.lucide)lucide.createIcons();R.scrollIntoView({behavior:'smooth',block:'start'});}};tick();}",
    "R.innerHTML=Result(ana);if(window.lucide)lucide.createIcons();if(!window._fast)R.scrollIntoView({behavior:'smooth',block:'start'});}};tick();return ana;}")

# ---------- AuthCard: guided checkpoints, server photo quality, ref compare, hand checks ----------
i=s.find('function AuthCard(a){'); j=s.find('function MarketLinks(a)')
s=s[:i]+r'''function AuthCard(a){const au=a.auth;if(!au)return'';const m=AUTHM[au.level]||AUTHM.suspicious;
 const shot=new Set(a.labels||[]);const cps=a.checkpoints||[];const refs=refsCache[a.cat]||[];
 const badQ=(a.photoQuality||[]).filter(p=>p.ok===false);
 return Card(`${Section('เช็คของแท้ / ตรงปก')}<div class="text-base font-extrabold ${m.c}">${m.e} ${m.l}</div>
 ${au.summary?`<div class="mt-1 text-xs text-slate-500">${au.summary}</div>`:''}
 ${au.ref_compare?`<div class="mt-2 rounded-xl bg-sky-500/10 p-2 text-[11px] text-sky-600">🔎 เทียบกับรูปของแท้ในคลัง ${au.refs_used} รูป: ${au.ref_compare.summary||''}</div>`:''}
 ${au.disagree?`<div class="mt-2 rounded-xl bg-amber-500/10 p-2 text-[11px] text-amber-600">⚖️ AI ตรวจสองรอบได้ผลไม่ตรงกัน จึงให้เป็นสีเหลือง</div>`:''}
 ${(au.notes||[]).filter(n=>!/สองรอบ/.test(n)).map(n=>`<div class="mt-1 text-[11px] text-amber-600">• ${n}</div>`).join('')}
 <div class="mt-3 space-y-1.5">${(au.checks||[]).map(c=>{const k=CHK[c.status]||CHK.unclear;return`<div class="flex gap-2 text-[12px]"><span class="w-4 shrink-0 text-center font-bold ${k[1]}">${k[0]}</span><div class="min-w-0"><div>${c.point}</div>${c.note?`<div class="text-[11px] text-slate-500">${c.note}</div>`:''}</div></div>`}).join('')}</div>
 ${(au.red_flags||[]).length||(au.handFail||[]).length?`<div class="mt-2 rounded-xl bg-rose-500/10 p-2.5 text-[11px] text-rose-500">${[...(au.red_flags||[]),...(au.handFail||[]).map(h=>'เช็คด้วยมือไม่ผ่าน: '+h)].map(f=>'🚩 '+f).join('<br>')}</div>`:''}
 ${badQ.length?`<div class="mt-2 rounded-xl bg-amber-500/10 p-2 text-[11px] text-amber-600">📷 AI บอกว่ารูป${badQ.map(p=>' '+p.index).join(',')} ใช้ไม่ได้: ${badQ.map(p=>p.problem).filter(Boolean).join(' / ')}</div>`:''}
 ${cps.length?`<div class="mt-3 text-[12px] font-bold">ถ่ายทีละจุด (${cps.filter(c=>shot.has(c)).length}/${cps.length})</div>
 <div class="mt-1.5 space-y-1.5">${cps.map(cp=>{const r=refs.find(x=>x.checkpoint===cp);const done=shot.has(cp)||labels.includes(cp);
  return`<div class="flex items-center gap-2 rounded-xl bg-black/[.03] p-2 text-[12px] dark:bg-white/[.03]">
  ${r?`<img src="${API.url()}/api/refs/img?key=${encodeURIComponent(r.key)}&k=${encodeURIComponent(API.key())}" class="h-10 w-10 shrink-0 rounded-lg object-cover" title="ตัวอย่างของแท้">`:`<span class="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-black/5 text-base">📷</span>`}
  <span class="min-w-0 flex-1">${cp}${r?'<span class="block text-[10px] text-sky-600">ภาพซ้าย = ตัวอย่างของแท้</span>':''}</span>
  ${done?'<span class="text-emerald-500 text-[11px] font-bold">✓ ถ่ายแล้ว</span>':`<button onclick="shootCheckpoint(${JSON.stringify(cp).replace(/"/g,'&quot;')})" class="tapscale shrink-0 rounded-full bg-amber-500 px-3 py-1 text-[11px] font-bold text-white">ถ่าย</button>`}</div>`}).join('')}</div>
 ${imgs.length>(a.labels||[]).length?`<button onclick="rescanAll()" class="tapscale mt-2 w-full rounded-xl bg-brand-500 py-2.5 text-sm font-bold text-white">🔄 สแกนใหม่ด้วยรูปทั้งหมด (${imgs.length} รูป)</button>`:''}`:''}
 <div class="mt-2 text-[10px] text-slate-400">ประเมินจากรูปเท่านั้น ไม่ใช่ใบรับรองของแท้ · ของราคาสูงควรให้ผู้เชี่ยวชาญเช็คก่อนซื้อ</div>`,`ring-1 ${m.bg}`)+HandCard(a)+RefCard(a);}
/* เช็คด้วยมือ: t='auth' ไม่ผ่าน = เสี่ยงปลอม, t='cond' ไม่ผ่าน = หักราคา */
const HAND={
 'apparel.vintage':[{q:'ป้ายคอเก่าและนุ่มพอๆ กับตัวเสื้อ',t:'auth'},{q:'ลายสกรีนแตก/ซีดเข้ากับเนื้อผ้า ไม่มันวาวใหม่',t:'auth'},{q:'ผ้าบางนุ่มตามอายุ ไม่แข็งแบบเสื้อใหม่',t:'auth'},{q:'ไม่มีรู คราบ หรือคอยืดที่รูปไม่เห็น',t:'cond'},{q:'ไม่มีกลิ่นอับ/ราที่ซักไม่ออก',t:'cond'}],
 'tools.power':[{q:'น้ำหนักแน่น ไม่เบาผิดปกติเมื่อเทียบสเปก',t:'auth'},{q:'แบตใส่เครื่องแล้วล็อกแน่น ไม่หลวม',t:'auth'},{q:'ลองเปิดเครื่องแล้วทำงานปกติ',t:'cond'},{q:'เสียงมอเตอร์เรียบ ไม่มีเสียงขูด',t:'cond'},{q:'ไม่มีประกายไฟที่แปรงถ่านมากผิดปกติ',t:'cond'}],
 'shoes.brand':[{q:'ไม่มีกลิ่นกาวฉุนผิดปกติ',t:'auth'},{q:'ป้ายในลิ้นกับกล่องรหัสตรงกัน',t:'auth'},{q:'พื้นและซับในไม่ยุบ/ลอก',t:'cond'}],
 'luxury':[{q:'ผู้เชี่ยวชาญ/ร้านรับตรวจยืนยันว่าแท้แล้ว',t:'auth',expert:true},{q:'มีใบรับประกัน/ใบเสร็จตรงกับสินค้า',t:'auth'}],
 'phone':[{q:'เช็ค IMEI แล้ว ไม่ติดล็อก/ไม่ติดบัญชี',t:'auth'},{q:'จอ แบต กล้อง ลำโพงทำงานปกติ',t:'cond'}],
 generic:[{q:'ลองใช้งานจริงแล้วปกติ',t:'cond'},{q:'ของครบชุด',t:'cond'}]};
function HandCard(a){const H=HAND[a.cat]||HAND.generic;
 return Card(`${Section('เช็คด้วยมือ (กล้องเห็นไม่ได้)')}<div class="space-y-1.5">${H.map((h,i)=>{const v=hand[h.q];
  const b=(val,lab,on)=>`<button onclick="setHand(${i},${val})" class="tapscale rounded-full px-2.5 py-1 text-[11px] font-bold ${on?(val?'bg-emerald-500 text-white':'bg-rose-500 text-white'):'bg-black/5 text-slate-500 dark:bg-white/5'}">${lab}</button>`;
  return`<div class="flex items-center gap-2 text-[12px]"><span class="min-w-0 flex-1">${h.q}${h.t==='auth'?' <span class="text-[10px] text-slate-400">(ของแท้)</span>':''}</span>${b(true,'✓ ผ่าน',v===true)}${b(false,'✗ ไม่ผ่าน',v===false)}</div>`}).join('')}</div>
 <div class="mt-2 text-[10px] text-slate-400">ไม่ผ่านข้อ "(ของแท้)" = เสี่ยงปลอม · ไม่ผ่านข้ออื่น = หักราคา 15% · ผลนี้ส่งให้ AI ตอนสแกนใหม่ด้วย</div>`);}
function setHand(i,val){const a=ana;if(!a)return;const h=(HAND[a.cat]||HAND.generic)[i];hand[h.q]=hand[h.q]===val?undefined:val;if(hand[h.q]===undefined)delete hand[h.q];
 window._fast=true;try{analyze(a.price)}finally{window._fast=false}}
function RefCard(a){if(!API.url()||!imgs.length)return'';
 return Card(`<div class="text-[12px] font-bold">ของชิ้นนี้ยืนยันแล้วว่าแท้?</div><div class="mt-1 text-[11px] text-slate-500">เช่น ผู้เชี่ยวชาญเช็คแล้ว หรือซื้อจากช็อปแท้ เก็บรูปทุกจุดไว้เป็น "ตัวอย่างของแท้" ให้ AI ใช้เทียบครั้งต่อไป</div>
 <button onclick="addRefs()" class="tapscale mt-2 w-full rounded-xl ${confirmRef?'bg-sky-600 text-white':'bg-black/5'} py-2 text-xs font-bold">${confirmRef?'กดอีกครั้งเพื่อยืนยัน: ของแท้แน่นอน':'⭐ เก็บเป็นรูปอ้างอิงของแท้'}</button>`);}
async function addRefs(srcImgs,srcLabels,cat){
 if(!srcImgs&&!confirmRef){confirmRef=true;renderAfterAdd();return;}confirmRef=false;
 const I=srcImgs||imgs,L=srcLabels||labels,C=cat||(ana&&ana.cat)||'generic';let n=0;
 try{for(let k=0;k<I.length;k++){const small=await shrink(I[k],800);
  const r=await fetch(API.url()+'/api/refs',{method:'POST',headers:{'content-type':'application/json','x-app-key':API.key()},body:JSON.stringify({category:C,checkpoint:L[k]||'',image:small,note:ana?ana.name:''})});
  const d=await r.json();if(d.error)throw new Error(d.error);n++;}
  delete refsCache[C];loadRefs(C);toast(`เก็บรูปอ้างอิงของแท้ ${n} รูปแล้ว`);}catch(e){toast('เก็บรูปไม่สำเร็จ: '+e.message);}
 if(!srcImgs)renderAfterAdd();}
function shrink(dataUrl,max){return new Promise(res=>{const im=new Image();im.onload=()=>{const s=Math.min(1,max/Math.max(im.width,im.height));const c=document.createElement('canvas');c.width=im.width*s;c.height=im.height*s;c.getContext('2d').drawImage(im,0,0,c.width,c.height);res(c.toDataURL('image/jpeg',.8));};im.src=dataUrl;});}
async function loadRefs(cat){if(!cat||refsCache[cat]||!API.url())return;refsCache[cat]=[];
 try{const r=await fetch(API.url()+'/api/refs?category='+encodeURIComponent(cat),{headers:{'x-app-key':API.key()}});const d=await r.json();if(d.items){refsCache[cat]=d.items;if(ana&&ana.cat===cat)renderAfterAdd();}}catch(e){}}
function DefectCard(a){const D=a.defects||[];if(!D.length&&!a.size&&!a.lesson)return'';
 return Card(`${a.lesson?`<div class="rounded-xl bg-brand-500/10 p-2.5 text-[12px]">💡 <b>รู้ไว้:</b> ${a.lesson}</div>`:''}
 ${a.size?`<div class="mt-2">${Row('ไซซ์',a.size)}</div>`:''}
 ${D.length?`<div class="mt-2 text-[12px] font-bold">ตำหนิที่เจอ ${a.defectPct?`<span class="font-normal text-rose-500">(หักราคา ${a.defectPct.toFixed(0)}%)</span>`:''}</div>
 <div class="mt-1 space-y-1">${D.map(x=>`<div class="flex justify-between text-[12px]"><span>${x.severity==='major'?'🔸':'▫️'} ${x.what}</span><span class="text-slate-500">−${+x.price_impact_pct||0}%</span></div>`).join('')}</div>`:''}`);}
'''+s[j:]

# ---------- Result: data-thin banner + defect card ----------
rep("${AuthCard(a)}","${a.soldN<3&&a.low?Card(`<div class=\"text-[12px] text-amber-600\">⚠ ข้อมูลราคาขายจริงน้อย (${a.soldN} จุด) — ราคาตลาด${Math.round(a.low)===Math.round(a.high)?'ประมาณ <b>'+money(a.mid)+'</b> (ยังไม่มีช่วงราคาให้เทียบ)':'น่าจะอยู่ช่วง <b>'+money(a.low)+'–'+money(a.high)+'</b>'} ใช้คะแนนเป็นแนวทางเท่านั้น</div>`,'ring-1 ring-amber-500/30'):''}\n ${AuthCard(a)}\n ${DefectCard(a)}")

# ---------- FindDeal: batch button + hunting list ----------
rep(''' <h1 class="text-2xl font-extrabold tracking-tight">สแกนของ</h1>''',''' <h1 class="text-2xl font-extrabold tracking-tight">สแกนของ</h1>
 <button onclick="go('/batch')" class="tapscale mx-auto flex items-center gap-1.5 rounded-full bg-black/5 px-4 py-2 text-xs font-bold dark:bg-white/5">⚡ โหมดสแกนรัว (กองเสื้อ/กระสอบ)${Batch.items.length?` · คิว ${Batch.items.length}`:''}</button>
 ${HuntChips()}''')

# ---------- saveDeal: keep images in IndexedDB, reset ----------
rep("function saveDeal(){if(!ana)return;Store.add({...ana,events:[{t:'found',at:Date.now()}]});",
    "function saveDeal(){if(!ana)return;const dd=Store.add({...ana,events:[{t:'found',at:Date.now()}]});const I=[...imgs],L=[...labels];Promise.all(I.map(x=>shrink(x,800))).then(sm=>IDB.set('img:'+dd.id,{imgs:sm,labels:L}));hand={};labels=[];")

# ---------- saveResult: auto days ----------
rep("const s=+V('r_sell'),dy=+V('r_days');if(!s)return toast('กรอกราคาขายจริง');const d=Store.get(id);",
    "const s=+V('r_sell');let dy=+V('r_days');if(!s)return toast('กรอกราคาขายจริง');const d=Store.get(id);if(!dy){const pe=(d.events||[]).find(e=>e.t==='purchased');dy=Math.max(1,Math.round((Date.now()-((pe&&pe.at)||d.createdAt))/864e5));}")

# ---------- listing: honest, no authenticity claim, block high risk ----------
i=s.find('listing(d){'); j=s.find(' negoScript(d,tone)')
s=s[:i]+r'''listing(d){const c=CAT[d.cat]||CAT.generic;
  if(d.auth&&d.auth.level==='high_risk'||d.mistake)return{blocked:true};
  const defects=(d.defects||[]).map(x=>x.what).filter(Boolean);
  const title=[d.name,d.era,d.size?'ไซซ์ '+d.size:'',d.brand&&!(d.name||'').includes(d.brand)?d.brand:''].filter(Boolean).join(' ');
  return{title,
  desc:`${d.name}\n• สภาพ: ${T.cond[d.cond]||'-'}${d.size?'\n• ไซซ์: '+d.size:''}${d.era?'\n• ยุค (ประเมิน): '+d.era:''}\n• ตำหนิ: ${defects.length?defects.join(', '):'ไม่พบตำหนิที่เห็นชัด'}\n• มีรูป${(c.check||[]).slice(0,3).join(' / ')}ให้ดูประกอบ\n• ขายตามสภาพ ดูรูปก่อนตัดสินใจ สอบถามได้`,
  price:d.target,min:Math.round(d.target*.88),
  tags:['#'+(d.brand||'มือสอง').replace(/\s/g,''),'#'+c.th.replace(/\s/g,''),d.era?'#'+d.era.replace(/\s/g,''):'#มือสอง'],
  note:'ไม่เขียนว่า "ของแท้" ในประกาศ เว้นแต่ผ่านผู้เชี่ยวชาญแล้ว · แนบรูปป้าย/ตะเข็บ/ตำหนิที่ถ่ายตอนเช็ค'};},
'''+s[j:]
rep("""if(tab==='sales')body=`${decay&&active?Card(decayChart(d),'mb-3'):''}
 ${Card(`""","""if(tab==='sales')body=`${decay&&active?Card(decayChart(d),'mb-3'):''}
 ${L.blocked?Card(`<div class="text-sm font-bold text-rose-500">ไม่สร้างประกาศขายให้ดีลนี้</div><div class="mt-1 text-xs text-slate-500">ผลเช็คเสี่ยงของปลอม หรือถูกบันทึกว่าพลาด การขายของที่ใช้เครื่องหมายการค้าปลอมผิดกฎหมาย</div>`,'ring-1 ring-rose-500/30'):Card(`""")
rep("""<div class="mt-1 text-xs text-brand-500">${L.tags.join(' ')}</div>`)}""","""<div class="mt-1 text-xs text-brand-500">${L.tags.join(' ')}</div>
 <div class="mt-2 text-[11px] text-amber-600">${L.note}</div>
 <button onclick="dealPhotos('${d.id}')" class="tapscale mt-2 w-full rounded-xl bg-black/5 py-2 text-xs font-semibold dark:bg-white/5">🖼 ดูรูปที่ถ่ายตอนเช็ค (ใช้ลงประกาศ)</button><div id="dealPh"></div>`)}""")
rep("function copyL(){const d=Store.get(param),L=AI.listing(d);","function copyL(){const d=Store.get(param),L=AI.listing(d);if(L.blocked)return toast('ดีลนี้สร้างประกาศไม่ได้');")

# ---------- Detail overview: mistake + verify buttons ----------
rep("""if(tab==='overview')body=`""","""if(tab==='overview')body=`${MistakeCard(d)}""")

# ---------- Insights: fastest sellers + hunt list + lessons ----------
rep("""${Card(`${Section('💡 บทเรียนจากดีลจริง')}""","""${Card(`${Section('⚡ ขายเร็ว-กำไรดี (ควรล่าอีก)')}${HuntTable()}`)}
 ${Card(`${Section('🚩 ดีลที่พลาด/ของปลอม')}${Store.all().filter(x=>x.mistake).map(x=>`<div class="text-[13px] text-rose-400">• ${x.name}: ${x.mistake}</div>`).join('')||'<div class="text-[13px] text-slate-500">ยังไม่มี</div>'}`)}
 ${Card(`${Section('📚 ความรู้ที่ได้จากการสแกน')}<div class="space-y-1 text-[13px] text-slate-500">${(Store.d.lessons||[]).slice(0,15).map(l=>`<div>• ${l}</div>`).join('')||'ยังไม่มี'}</div>`)}
 ${Card(`${Section('💡 บทเรียนจากดีลจริง')}""")

# ---------- router: batch page ----------
rep("cur==='/deal'?Detail():Insights();","cur==='/deal'?Detail():cur==='/batch'?BatchPage():Insights();")

# ---------- new module block (before router) ----------
block=r'''
/* ============ IndexedDB (เก็บรูป/คิว ในเครื่อง) ============ */
const IDB={db:null,open(){return this.db?Promise.resolve(this.db):new Promise((res,rej)=>{const r=indexedDB.open('dealhunter',1);r.onupgradeneeded=()=>r.result.createObjectStore('kv');r.onsuccess=()=>{this.db=r.result;res(this.db)};r.onerror=()=>rej(r.error)})},
 async get(k){try{const db=await this.open();return await new Promise(res=>{const q=db.transaction('kv').objectStore('kv').get(k);q.onsuccess=()=>res(q.result||null);q.onerror=()=>res(null)})}catch(e){return null}},
 async set(k,v){try{const db=await this.open();await new Promise(res=>{const t=db.transaction('kv','readwrite');t.objectStore('kv').put(v,k);t.oncomplete=res;t.onerror=res})}catch(e){}}};

/* ============ ดีลพลาด / ยืนยันของแท้ ============ */
function MistakeCard(d){if(d.mistake)return Card(`<div class="text-xs font-bold text-rose-500">🚩 บันทึกว่าพลาด: ${d.mistake}</div>`,'mb-3 ring-1 ring-rose-500/30');
 return Card(`<div class="flex flex-wrap gap-2"><button onclick="document.getElementById('mkBox').classList.toggle('hidden')" class="tapscale flex-1 rounded-xl bg-rose-500/10 py-2 text-xs font-bold text-rose-500">🚩 ของชิ้นนี้ปลอม/พลาด</button>
 <button onclick="verifyDeal('${d.id}')" class="tapscale flex-1 rounded-xl bg-sky-500/10 py-2 text-xs font-bold text-sky-600">⭐ ยืนยันแท้ → เก็บเป็นรูปอ้างอิง</button></div>
 <div id="mkBox" class="hidden mt-2">${Inp('mk_what','พลาดเพราะอะไร (AI จะจำไว้ระวังครั้งหน้า)','เช่น ป้ายคอเป็นป้ายใหม่ที่เย็บทับ')}
 <button onclick="saveMistake('${d.id}')" class="tapscale mt-2 w-full rounded-xl bg-rose-500 py-2 text-xs font-bold text-white">บันทึก</button></div>`,'mb-3');}
async function saveMistake(id){const what=V('mk_what');if(!what)return toast('บอกสาเหตุสั้นๆ ก่อน');const d=Store.get(id);
 if(API.url()){try{await fetch(API.url()+'/api/mistakes',{method:'POST',headers:{'content-type':'application/json','x-app-key':API.key()},body:JSON.stringify({category:d.cat,name:d.name,what})});}catch(e){}}
 Store.upd(id,{mistake:what});toast('บันทึกแล้ว — AI จะระวังจุดนี้ครั้งหน้า');}
async function verifyDeal(id){const d=Store.get(id);const p=await IDB.get('img:'+id);
 if(!p||!p.imgs||!p.imgs.length)return toast('ไม่มีรูปของดีลนี้เก็บไว้ในเครื่อง');
 if(!API.url())return toast('ตั้งค่าเซิร์ฟเวอร์ก่อน');
 await addRefs(p.imgs,p.labels,d.cat);Store.upd(id,{verified:true});}
async function dealPhotos(id){const p=await IDB.get('img:'+id);const el=document.getElementById('dealPh');if(!el)return;
 el.innerHTML=p&&p.imgs?`<div class="mt-2 grid grid-cols-3 gap-1.5">${p.imgs.map((x,i)=>`<a href="${x}" download="deal-${i+1}.jpg"><img src="${x}" class="aspect-square w-full rounded-lg object-cover"><div class="truncate text-[10px] text-slate-500">${(p.labels||[])[i]||''}</div></a>`).join('')}</div><div class="mt-1 text-[10px] text-slate-400">แตะรูปเพื่อบันทึกลงเครื่อง</div>`:'<div class="mt-2 text-xs text-slate-500">ไม่มีรูปเก็บไว้</div>';}

/* ============ ของที่ควรล่า (จากดีลที่ขายแล้ว) ============ */
function huntData(){const h=Learn.history().filter(x=>x.actualProfit!=null);const g={};
 h.forEach(x=>{const k=((x.brand&&x.brand!=='ไม่ทราบ'?x.brand+' ':'')+(x.model&&x.model!=='ไม่ทราบ'&&x.model!=='—'?x.model:x.name)).trim();
  g[k]=g[k]||{k,cat:x.cat,n:0,profit:0,days:0,win:0};const o=g[k];o.n++;o.profit+=x.actualProfit;o.days+=(x.actualDays||CAT[x.cat].days);if(x.actualProfit>0)o.win++;});
 return Object.values(g).map(o=>({...o,avgProfit:o.profit/o.n,avgDays:o.days/o.n,perDay:o.profit/Math.max(1,o.days)})).filter(o=>o.avgProfit>0).sort((a,b)=>b.perDay-a.perDay);}
function HuntTable(){const H=huntData();if(!H.length)return'<div class="text-[13px] text-slate-500">ขายของได้แล้วบันทึกราคาขายจริง ระบบจะจัดอันดับให้</div>';
 return`<table class="w-full text-left text-[13px]"><thead class="text-xs text-slate-500"><tr><th class="pb-1.5">สินค้า</th><th>ขาย (วัน)</th><th>กำไร/ชิ้น</th><th>กำไร/วัน</th></tr></thead><tbody>
 ${H.slice(0,10).map(o=>`<tr class="border-t border-black/5 dark:border-white/5"><td class="py-2">${o.k} <span class="text-[10px] text-slate-500">×${o.n}</span></td><td>${o.avgDays.toFixed(0)}</td><td>${money(o.avgProfit)}</td><td class="font-bold text-emerald-500">${money(o.perDay)}</td></tr>`).join('')}</tbody></table>`;}
function HuntChips(){const H=huntData().slice(0,6);if(!H.length)return'';
 return`<div class="mx-auto max-w-sm text-left"><div class="mb-1 text-[11px] font-semibold text-slate-500">🎯 ของที่ควรมองหาวันนี้ (ขายเร็ว กำไรดี)</div><div class="flex flex-wrap gap-1.5">${H.map(o=>`<span class="rounded-full bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-600">${o.k} · ${money(o.avgProfit)}</span>`).join('')}</div></div>`;}

/* ============ โหมดสแกนรัว + คิวออฟไลน์ ============ */
const Batch={items:[],busy:false,loaded:false,
 async load(){if(this.loaded)return;this.loaded=true;const x=await IDB.get('batch');if(Array.isArray(x))this.items=x;if(cur==='/batch')render();this.run();},
 save(){IDB.set('batch',this.items.map(({img,...r})=>({...r,img})));},
 async add(img,thumb,price){this.items.unshift({id:uid(),img,thumb,price:price||null,status:'queued',pick:false,at:Date.now()});this.save();this.run();},
 async run(){if(this.busy||!API.url())return;this.busy=true;
  try{while(true){const it=this.items.find(x=>x.status==='queued'||x.status==='offline');if(!it)break;
   if(!navigator.onLine){this.items.forEach(x=>{if(x.status==='queued')x.status='offline'});this.save();break;}
   it.status='scanning';this.redraw();
   try{const d=await callScan([it.img],['ตัวสินค้าเต็มชิ้น'],{});it.scan=d;it.status='done';}
   catch(e){if(!navigator.onLine||/Failed to fetch|NetworkError|Load failed/i.test(e.message)){it.status='offline';this.save();this.redraw();break;}it.status='error';it.err=e.message;}
   this.save();this.redraw();}}finally{this.busy=false;}},
 redraw(){if(cur==='/batch'){const el=document.getElementById('batchList');if(el){el.innerHTML=BatchRows();document.getElementById('batchSum').innerHTML=BatchSummary();}}},
 quick(it){const d=it.scan;if(!d)return null;const p=scanEvidence({...d});const E=Engine.evidence(p);const c=d.item&&d.item.condition||'good';
  const v=Engine.valuation(E,c);const dp=Math.min(50,(d.defects||[]).reduce((a,x)=>a+(+x.price_impact_pct||0),0));const f=1-dp/100;
  const mid=(v.mid||0)*f,maxBuy=(v.maxBuy||0)*f,target=(v.target||0)*f;const lvl=d.auth?d.auth.level:'suspicious';
  let light=lvl==='high_risk'?'red':!mid?'yellow':it.price?(it.price<=maxBuy?(lvl==='pass'?'green':'yellow'):'red'):(lvl==='pass'?'green':'yellow');
  if(d.item&&d.item.category==='luxury')light='red';
  return{mid,maxBuy,target,light,lvl,name:d.item.name,soldN:E.soldN};}};
window.addEventListener('online',()=>Batch.run());
async function batchUpload(el){for(const f of [...el.files]){const big=await resizeImg(f,1280,.82);const th=await resizeImg(f,300,.7);await Batch.add(big,th,null);}el.value='';render();}
const LIGHT={green:['🟢','ซื้อได้'],yellow:['🟡','ดูเพิ่ม/ต่อราคา'],red:['🔴','ข้าม']};
function BatchRows(){if(!Batch.items.length)return'<div class="py-8 text-center text-xs text-slate-500">ยังไม่มีของในคิว กดถ่ายได้เลย</div>';
 return Batch.items.map(it=>{const q=Batch.quick(it);const st={queued:'รอสแกน',scanning:'กำลังสแกน...',offline:'รอเน็ต 📶',error:'ผิดพลาด'}[it.status];
  return`<div class="flex items-center gap-2.5 rounded-2xl bg-black/[.03] p-2 dark:bg-white/[.03]">
  <img src="${it.thumb}" class="h-14 w-14 shrink-0 rounded-xl object-cover">
  <div class="min-w-0 flex-1 text-[12px]">${q?`<div class="truncate font-bold">${LIGHT[q.light][0]} ${q.name}</div>
   <div class="text-slate-500">ซื้อไม่เกิน <b class="text-amber-600">${money(q.maxBuy)}</b> · ขายได้ ~${money(q.target)}${q.soldN<3?' · ข้อมูลน้อย':''}</div>`:`<div class="font-semibold text-slate-500">${st}${it.err?' — '+it.err:''}</div>`}
   <div class="mt-1 flex items-center gap-1.5"><input type="number" inputmode="numeric" placeholder="ราคาแม่ค้า" value="${it.price||''}" onchange="batchPrice('${it.id}',this.value)" class="w-24 rounded-lg bg-white/70 px-2 py-1 text-[12px] ring-1 ring-black/10 dark:bg-white/10">
   ${q?`<label class="flex items-center gap-1 text-[11px]"><input type="checkbox" ${it.pick?'checked':''} onchange="batchPick('${it.id}',this.checked)" class="h-4 w-4 accent-emerald-500">เอา</label>
   <button onclick="batchOpen('${it.id}')" class="ml-auto rounded-full bg-black/5 px-2 py-0.5 text-[10px] dark:bg-white/10">ละเอียด</button>`:''}
   ${it.status==='error'?`<button onclick="batchRetry('${it.id}')" class="rounded-full bg-black/5 px-2 py-0.5 text-[10px]">ลองใหม่</button>`:''}
   <button onclick="batchDel('${it.id}')" class="${q?'':'ml-auto '}rounded-full px-1.5 text-[11px] text-slate-400">✕</button></div></div></div>`}).join('');}
function BatchSummary(){const P=Batch.items.filter(x=>x.pick&&x.scan);if(!P.length)return'<div class="text-[12px] text-slate-500">ติ๊ก "เอา" ตัวที่จะซื้อ ระบบจะสรุปเงินที่ต้องจ่ายและกำไรรวม</div>';
 let pay=0,sell=0,noPrice=0;P.forEach(it=>{const q=Batch.quick(it);if(it.price)pay+=it.price;else noPrice++;sell+=q.target;});
 const fee=sell*.06+P.length*40;
 return`${Row('เลือกไว้',P.length+' ชิ้น')}${Row('จ่ายรวม',money(pay)+(noPrice?` (+${noPrice} ชิ้นยังไม่ใส่ราคา)`:''))}${Row('ขายได้รวม (ประมาณ)',money(sell))}${Row('ค่าธรรมเนียม+ส่ง (ประมาณ)',money(fee))}
 <div class="mt-1 flex justify-between rounded-xl bg-black/[.03] px-3 py-2 dark:bg-white/[.03]"><b class="text-sm">กำไรรวมประมาณ</b><b class="text-lg ${sell-pay-fee>=0?'text-emerald-500':'text-rose-500'}">${sgn(sell-pay-fee)}</b></div>
 <button onclick="batchSave()" class="tapscale mt-2 w-full rounded-xl bg-ink-900 py-2.5 text-sm font-bold text-white dark:bg-white dark:text-ink-950">💾 บันทึกตัวที่เลือกเป็นดีล</button>`;}
function batchPrice(id,v){const it=Batch.items.find(x=>x.id===id);it.price=+v||null;Batch.save();Batch.redraw();}
function batchPick(id,v){const it=Batch.items.find(x=>x.id===id);it.pick=v;Batch.save();Batch.redraw();}
function batchDel(id){Batch.items=Batch.items.filter(x=>x.id!==id);Batch.save();Batch.redraw();}
function batchRetry(id){const it=Batch.items.find(x=>x.id===id);it.status='queued';it.err='';Batch.run();}
function batchClear(){Batch.items=Batch.items.filter(x=>!x.scan||x.pick===false&&false);Batch.items=[];Batch.save();render();}
function batchOpen(id){const it=Batch.items.find(x=>x.id===id);if(!it||!it.scan)return;
 imgs=[it.img];thumbs=[it.thumb];labels=['ตัวสินค้าเต็มชิ้น'];hand={};ana=null;go('/find');applyScan(it.scan);
 const q=document.getElementById('q_price');if(it.price&&q){q.value=it.price;const f=document.getElementById('f_price');if(f)f.value=it.price;}
 renderDrop(false);if(it.price)analyze(it.price);else askPrice();}
function batchSave(){const P=Batch.items.filter(x=>x.pick&&x.scan);const miss=P.filter(x=>!x.price);if(miss.length)return toast('ใส่ราคาแม่ค้าให้ครบทุกตัวที่เลือกก่อน');
 let n=0;window._fast=true;try{P.forEach(it=>{imgs=[it.img];thumbs=[it.thumb];labels=['ตัวสินค้าเต็มชิ้น'];hand={};applyScan(it.scan);const a=analyze(it.price);
  if(a){const dd=Store.add({...a});IDB.set('img:'+dd.id,{imgs:[it.img],labels:['ตัวสินค้าเต็มชิ้น']});n++;}});}finally{window._fast=false;}
 Batch.items=Batch.items.filter(x=>!(x.pick&&x.scan));Batch.save();imgs=[];thumbs=[];labels=[];scan=null;ana=null;pending=[];toast(`บันทึก ${n} ดีลแล้ว`);go('/deals');}
function BatchPage(){Batch.load();return`<div class="pagefade space-y-4"><button onclick="go('/find')" class="text-xs font-medium text-slate-500">← กลับหน้าสแกน</button>
 <h1 class="text-2xl font-extrabold tracking-tight">⚡ สแกนรัว</h1>
 <div class="text-xs text-slate-500">ถ่ายต่อกันได้เลย ระบบสแกนให้ทีละตัวเบื้องหลัง ไม่มีเน็ตก็ถ่ายเก็บไว้ได้ จะสแกนให้เองเมื่อมีสัญญาณ</div>
 ${API.url()?'':Card('<div class="text-xs text-amber-600">ยังไม่ได้ตั้งค่าเซิร์ฟเวอร์ — ไปหน้าสแกนเพื่อตั้งค่าก่อน</div>')}
 <button onclick="document.getElementById('f_bimg').click()" class="tapscale w-full rounded-[2rem] bg-gradient-to-br from-brand-400 to-teal-600 py-6 text-base font-extrabold text-white shadow-glow">📷 ถ่ายตัวต่อไป</button>
 <input type="file" id="f_bimg" accept="image/*" capture="environment" multiple class="hidden" onchange="batchUpload(this)">
 <div id="batchList" class="space-y-2">${BatchRows()}</div>
 ${Card(`${Section('สรุปกองนี้')}<div id="batchSum">${BatchSummary()}</div>`)}
 ${Batch.items.length?`<button onclick="batchClear()" class="w-full text-center text-[11px] text-slate-400 underline">ล้างคิวทั้งหมด</button>`:''}</div>`;}
'''
rep("/* ============ router","%s\n/* ============ router" % block)
rep("render();\n</script>","render();Batch.load();\n</script>") if "render();\n</script>" in s else None
open('deal-hunter-v2.html','w',encoding='utf-8').write(s)
print('ok',len(s))
