const http=require('http'),fs=require('fs');const {chromium}=require('playwright');
const sample=fs.readFileSync(__dirname+'/sample-response.json');
const srv=http.createServer((q,r)=>{r.setHeader('access-control-allow-origin','*');r.setHeader('access-control-allow-headers','content-type, x-app-key');
 if(q.method==='OPTIONS'){r.end();return}
 if(q.url.startsWith('/api/scan')){let b='';q.on('data',c=>b+=c);q.on('end',()=>{const n=JSON.parse(b).images.length;console.log('scan images:',n);setTimeout(()=>{r.setHeader('content-type','application/json');r.end(sample)},300)});return}
 r.setHeader('content-type','text/html; charset=utf-8');r.end(fs.readFileSync(__dirname+'/../app/deal-hunter-v2.html'));}).listen(8787);
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:2});
 const errs=[];
 await p.route('**/cdn.tailwindcss.com/**',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(__dirname+'/node_modules/@tailwindcss/browser/dist/index.global.js')}));
 await p.route('**/unpkg.com/**',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(__dirname+'/node_modules/lucide/dist/umd/lucide.min.js')}));
 await p.route('**/fonts.googleapis.com/**',r=>r.fulfill({contentType:'text/css',body:''}));p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://localhost:8787/');await p.waitForTimeout(1500);
 await p.screenshot({path:__dirname+'/1-setup.png'});
 await p.fill('#s_url','http://localhost:8787');await p.fill('#s_key','k');await p.click('text=บันทึก');await p.waitForTimeout(500);
 await p.setInputFiles('#f_img',__dirname+'/shirt.jpg');
 await p.waitForSelector('#ask_price',{timeout:10000});await p.screenshot({path:__dirname+'/2-askprice.png'});
 await p.fill('#ask_price','300');await p.click('text=ดูผล');await p.waitForTimeout(2500);
 await p.screenshot({path:__dirname+'/3-result.png',fullPage:true});
 await p.setInputFiles('#f_img2',[__dirname+'/shirt.jpg',__dirname+'/shirt.jpg']);await p.waitForTimeout(2500);
 const txt=await p.textContent('#result');console.log('after rescan has result:',txt.includes('ขายที่ไหนดีที่สุด'));
 await p.click('text=บันทึกเป็นดีล');await p.waitForTimeout(800);
 console.log('deals page:',(await p.textContent('#main')).includes('Pubs of Dublin'));
 console.log('errors:',errs);await b.close();srv.close();})();
