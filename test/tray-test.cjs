const http=require('http'),fs=require('fs');const {chromium}=require('playwright');
const sample=JSON.parse(fs.readFileSync(__dirname+'/sample-response.json'));let last=null;
const srv=http.createServer((q,r)=>{r.setHeader('access-control-allow-origin','*');r.setHeader('access-control-allow-headers','content-type, x-app-key');if(q.method==='OPTIONS'){r.end();return}
 const send=o=>{r.setHeader('content-type','application/json');r.end(JSON.stringify(o))};let b='';q.on('data',c=>b+=c);q.on('end',()=>{
 if(q.url.startsWith('/api/scan')){last=JSON.parse(b);return setTimeout(()=>send(sample),200)}
 if(q.url.startsWith('/api/deals'))return send({deals:[],now:new Date().toISOString()});
 if(q.url.startsWith('/api/'))return send({items:[],entries:[]});
 r.setHeader('content-type','text/html; charset=utf-8');r.end(fs.readFileSync(__dirname+'/../app/deal-hunter-v2.html'));});}).listen(8789);
const ok=(c,m)=>console.log((c?'PASS ':'FAIL ')+m);
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2})).newPage();
 const errs=[];p.on('pageerror',e=>{if(!/tailwind/.test(e.message))errs.push(e.message)});
 await p.route('**/cdn.tailwindcss.com/**',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(__dirname+'/node_modules/@tailwindcss/browser/dist/index.global.js')}));
 await p.route('**/unpkg.com/**',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(__dirname+'/node_modules/lucide/dist/umd/lucide.min.js')}));
 await p.route('**/fonts.googleapis.com/**',r=>r.fulfill({contentType:'text/css',body:''}));
 await p.goto('http://localhost:8789/');await p.waitForTimeout(1200);
 await p.fill('#s_url','http://localhost:8789');await p.fill('#s_key','k');await p.click('text=บันทึก');await p.waitForTimeout(500);
 let t=await p.textContent('#result');ok(t.includes('ถ่ายตามรายการ (0/6)')&&t.includes('ป้ายคอ'),'checklist shown before any photo');
 await p.screenshot({path:__dirname+'/tray-0.png',fullPage:true});
 // shoot 3 via big button (goes in order)
 for(let i=0;i<3;i++){const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.click('#drop')]);await fc.setFiles(__dirname+'/shirt.jpg');await p.waitForTimeout(900);}
 t=await p.textContent('#result');ok(t.includes('(3/6)'),'3 shots in order');ok(scanned()===false,'no scan yet');
 // defect
 {const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.click('text=⚠️ ถ่ายตำหนิ')]);await fc.setFiles(__dirname+'/shirt.jpg');await p.waitForTimeout(900);}
 // switch category
 await p.click('text=⚽ เสื้อบอล');await p.waitForTimeout(300);t=await p.textContent('#result');ok(t.includes('ป้ายรหัสสินค้าด้านใน'),'category switch changes list');
 await p.click('text=👕 เสื้อวินเทจ');await p.waitForTimeout(300);
 await p.screenshot({path:__dirname+'/tray-4.png',fullPage:true});
 await p.click('text=ให้ AI วิเคราะห์');await p.waitForTimeout(2500);
 ok(last&&last.images.length===4,'scan sent 4 images');console.log('  labels',JSON.stringify(last&&last.labels));
 t=await p.textContent('#result');ok(await p.$('#ask_price')||t.includes('เช็คของแท้'),'result/price step shown');
 if(await p.$('#ask_price')){await p.fill('#ask_price','300');await p.click('text=ดูผล');await p.waitForTimeout(2000);}
 t=await p.textContent('#result');ok(t.includes('ซื้อไม่เกิน')&&t.includes('ดูรายละเอียดทั้งหมด'),'compact summary');
 await p.screenshot({path:__dirname+'/summary.png',fullPage:false});
 await p.click('text=ดูรายละเอียดทั้งหมด');await p.waitForTimeout(400);t=await p.textContent('#result');ok(await p.isVisible('text=STEP 1'),'details expand');
 ok(!errs.length,'no js errors '+errs.join('|'));await b.close();srv.close();})();
function scanned(){return !!last}
