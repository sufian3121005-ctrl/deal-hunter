import sys
s=open('deal-hunter-v2.html',encoding='utf-8').read()
def rep(old,new):
    global s
    if s.count(old)<1: sys.exit('NOT FOUND: '+old[:90])
    s=s.replace(old,new,1)

# ดีลตัวอย่างไม่ซิงก์
rep("seed(){const mk=o=>Object.assign({id:uid(),","seed(){const mk=o=>Object.assign({demo:true,id:uid(),")
# ทำเครื่องหมายว่าดีลเปลี่ยน
rep("add(d){d.id=uid();d.createdAt=Date.now();","add(d){d.id=uid();d.createdAt=Date.now();d.updatedAt=Date.now();Sync.mark(d.id);")
rep("upd(id,p){Object.assign(this.get(id),p);this.save()},","upd(id,p){Object.assign(this.get(id),p,{updatedAt:Date.now()});Sync.mark(id);this.save()},")
rep("event(id,t,amt){this.get(id).events.push({t,at:Date.now(),amt});this.save()},","event(id,t,amt){const d=this.get(id);d.events.push({t,at:Date.now(),amt});d.updatedAt=Date.now();Sync.mark(id);this.save()},")

block=r'''
/* ============ ซิงก์ดีลกับฐานข้อมูลกลาง (Supabase) ============ */
const Sync={st:null,timer:null,busy:false,
 s(){if(!this.st){try{this.st=JSON.parse(localStorage.getItem('deal_sync'))||{}}catch(e){this.st={}}this.st.dirty=this.st.dirty||[];}return this.st;},
 keep(){try{localStorage.setItem('deal_sync',JSON.stringify(this.st))}catch(e){}},
 mark(id){const s=this.s();if(!s.dirty.includes(id))s.dirty.push(id);this.keep();clearTimeout(this.timer);this.timer=setTimeout(()=>this.push(),1500);},
 ok(){return API.url()&&API.key()&&navigator.onLine;},
 async call(path,opt){const r=await fetch(API.url()+path,{...(opt||{}),headers:{'content-type':'application/json','x-app-key':API.key()}});const d=await r.json();if(!r.ok||d.error)throw new Error(d.error||r.status);return d;},
 async push(){if(!this.ok()||this.busy)return;const s=this.s();if(!s.dirty.length)return;this.busy=true;
  try{const ids=[...s.dirty];const deals=ids.map(id=>Store.get(id)).filter(d=>d&&!d.demo).map(d=>{const {img,...rest}=d;return{id:d.id,data:rest,updated_at:new Date(d.updatedAt||Date.now()).toISOString()}});
   if(deals.length)await this.call('/api/deals',{method:'POST',body:JSON.stringify({deals})});
   s.dirty=s.dirty.filter(id=>!ids.includes(id));this.keep();setSyncBadge('ok');}
  catch(e){console.warn('sync push',e);setSyncBadge('err');}finally{this.busy=false;}},
 async pull(){if(!this.ok())return;const s=this.s();
  try{const d=await this.call('/api/deals'+(s.lastPull?'?since='+encodeURIComponent(s.lastPull):''));let changed=0;
   if(d.deals.length&&Store.d.deals.some(x=>x.demo)){Store.d.deals=Store.d.deals.filter(x=>!x.demo);changed++;}
   for(const row of d.deals){const loc=Store.get(row.id);const t=Date.parse(row.updated_at);
    if(row.deleted){if(loc){Store.d.deals=Store.d.deals.filter(x=>x.id!==row.id);changed++;}continue;}
    if(!loc){Store.d.deals.push({...row.data,updatedAt:t});changed++;}
    else if((loc.updatedAt||0)<t&&!s.dirty.includes(row.id)){Object.assign(loc,row.data,{img:loc.img,updatedAt:t});changed++;}}
   s.lastPull=d.now;this.keep();
   if(changed){Store.d.deals.sort((a,b)=>(b.createdAt||0)-(a.createdAt||0));localStorage.setItem(Store.k,JSON.stringify(Store.d));render();}
   setSyncBadge('ok');}catch(e){console.warn('sync pull',e);setSyncBadge('err');}},
 /* ครั้งแรก: ส่งดีลที่มีอยู่ในเครื่องขึ้นทั้งหมด */
 first(){const s=this.s();if(s.initialized)return;Store.all().filter(d=>!d.demo).forEach(d=>{if(!s.dirty.includes(d.id))s.dirty.push(d.id)});s.initialized=true;this.keep();},
 async start(){if(!API.url()||!API.key())return;this.first();await this.push();await this.pull();
  setInterval(()=>{if(document.visibilityState==='visible'){this.push();this.pull();}},60000);
  window.addEventListener('online',()=>{this.push();this.pull();});}};
function setSyncBadge(st){const el=document.getElementById('syncBadge');if(el){el.textContent=st==='ok'?'☁︎ ซิงก์แล้ว':'☁︎ ยังไม่ซิงก์';el.className='text-[10px] '+(st==='ok'?'text-emerald-500':'text-amber-500');}}
async function uploadDealImages(id,imgsArr,labelsArr){if(!API.url()||!API.key()||!imgsArr||!imgsArr.length)return;
 try{await Sync.call('/api/deals/images',{method:'POST',body:JSON.stringify({id,images:imgsArr,labels:labelsArr})});}catch(e){console.warn('img upload',e);}}
'''
rep("/* ============ router",block+"\n/* ============ router")

# อัปโหลดรูปดีลขึ้นคลาวด์ด้วย
rep("Promise.all(I.map(x=>shrink(x,800))).then(sm=>IDB.set('img:'+dd.id,{imgs:sm,labels:L}));",
    "Promise.all(I.map(x=>shrink(x,800))).then(sm=>{IDB.set('img:'+dd.id,{imgs:sm,labels:L});uploadDealImages(dd.id,sm,L);});")
rep("if(a){const dd=Store.add({...a});IDB.set('img:'+dd.id,{imgs:[it.img],labels:['ตัวสินค้าเต็มชิ้น']});n++;}",
    "if(a){const dd=Store.add({...a});IDB.set('img:'+dd.id,{imgs:[it.img],labels:['ตัวสินค้าเต็มชิ้น']});shrink(it.img,800).then(x=>uploadDealImages(dd.id,[x],['ตัวสินค้าเต็มชิ้น']));n++;}")
# ดูรูปดีลจากคลาวด์ถ้าไม่มีในเครื่อง
rep("async function dealPhotos(id){const p=await IDB.get('img:'+id);const el=document.getElementById('dealPh');if(!el)return;",
    "async function dealPhotos(id){let p=await IDB.get('img:'+id);const el=document.getElementById('dealPh');if(!el)return;\n if((!p||!p.imgs)&&API.url()){el.innerHTML='<div class=\"mt-2 text-xs text-slate-500\">กำลังโหลดรูปจากคลาวด์...</div>';try{const d=await Sync.call('/api/deals/images?id='+encodeURIComponent(id));if(d.images&&d.images.length)p={imgs:d.images.map(x=>x.url),labels:d.images.map(x=>x.label)};}catch(e){}}")
rep("async function verifyDeal(id){const d=Store.get(id);const p=await IDB.get('img:'+id);",
    "async function verifyDeal(id){const d=Store.get(id);const p=await IDB.get('img:'+id);if((!p||!p.imgs)&&API.url())return toast('รูปของดีลนี้อยู่อีกเครื่อง ยืนยันจากเครื่องที่ถ่ายไว้');")

# ป้ายสถานะซิงก์บนหน้าสแกน + เริ่มซิงก์
rep("<button onclick=\"go('/kb')\" class=\"tapscale mx-auto -mt-2 block","<div class=\"-mt-3 text-center\"><span id=\"syncBadge\" class=\"text-[10px] text-slate-400\">${API.url()&&API.key()?'☁︎ เชื่อมฐานข้อมูลกลาง':''}</span></div>\n <button onclick=\"go('/kb')\" class=\"tapscale mx-auto -mt-2 block")
rep("render();Batch.load();","render();Batch.load();Sync.start();")
rep("function saveSetup(){localStorage.setItem('deal_api_url',V('s_url'));localStorage.setItem('deal_app_key',V('s_key'));toast('บันทึกการตั้งค่าแล้ว');render();}",
    "function saveSetup(){localStorage.setItem('deal_api_url',V('s_url'));localStorage.setItem('deal_app_key',V('s_key'));toast('บันทึกการตั้งค่าแล้ว');render();Sync.start();}")
rep("<title>Deal Hunter v2</title>","<title>Deal Hunter</title>")
open('deal-hunter-v2.html','w',encoding='utf-8').write(s)
print('ok',len(s))
