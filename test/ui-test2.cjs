const http=require('http'),fs=require('fs');const {chromium}=require('playwright');
const sample=JSON.parse(fs.readFileSync(__dirname+'/sample-response.json'));
let refs=[],mistakes=[],scanCount=0,offline=false;
const srv=http.createServer((q,r)=>{r.setHeader('access-control-allow-origin','*');r.setHeader('access-control-allow-headers','content-type, x-app-key');
 if(q.method==='OPTIONS'){r.end();return}
 const send=o=>{r.setHeader('content-type','application/json');r.end(JSON.stringify(o))};
 let b='';q.on('data',c=>b+=c);q.on('end',()=>{
  if(q.url.startsWith('/api/scan')){if(offline){r.destroy();return}scanCount++;const n=JSON.parse(b);console.log('  scan#'+scanCount,'imgs',n.images.length,'labels',JSON.stringify(n.labels),'hand',JSON.stringify(n.hint.hand||[]).slice(0,80));setTimeout(()=>send(sample),200);return}
  if(q.url.startsWith('/api/kb'))return send({entries:JSON.parse(fs.readFileSync(__dirname+'/../knowledge/apparel-kb.json')).entries});
  if(q.url.startsWith('/api/refs/img'))return send({});
  if(q.url.startsWith('/api/refs')&&q.method==='POST'){const d=JSON.parse(b);refs.push({key:'ref:'+d.category+':'+refs.length,checkpoint:d.checkpoint});return send({ok:true})}
  if(q.url.startsWith('/api/refs'))return send({items:refs});
  if(q.url.startsWith('/api/mistakes')){mistakes.push(JSON.parse(b));return send({ok:true})}
  r.setHeader('content-type','text/html; charset=utf-8');r.end(fs.readFileSync(__dirname+'/../app/deal-hunter-v2.html'));});}).listen(8788);
const ok=(c,m)=>console.log((c?'PASS ':'FAIL ')+m);
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2});const p=await ctx.newPage();
 const errs=[];p.on('pageerror',e=>{if(!/tailwind/.test(e.message))errs.push(e.message)});
 await p.route('**/cdn.tailwindcss.com/**',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(__dirname+'/node_modules/@tailwindcss/browser/dist/index.global.js')}));
 await p.route('**/unpkg.com/**',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(__dirname+'/node_modules/lucide/dist/umd/lucide.min.js')}));
 await p.route('**/fonts.googleapis.com/**',r=>r.fulfill({contentType:'text/css',body:''}));
 await p.goto('http://localhost:8788/');await p.waitForTimeout(1200);
 await p.fill('#s_url','http://localhost:8788');await p.fill('#s_key','k');await p.click('text=บันทึก');await p.waitForTimeout(400);
 // blurry photo check
 const {execSync}=require('child_process');execSync(`python3 -c "from PIL import Image,ImageFilter;Image.open('${__dirname}/shirt.jpg').filter(ImageFilter.GaussianBlur(12)).save('${__dirname}/blur.jpg')"`);
 await p.setInputFiles('#f_img',__dirname+'/blur.jpg');await p.waitForTimeout(1500);
 ok((await p.textContent('#result')).includes('เบลอ'),'blurry photo detected');
 await p.click('text=ใช้รูปนี้ต่อ');await p.waitForSelector('#ask_price',{timeout:8000});
 // restart with good photo
 await p.setInputFiles('#f_img',__dirname+'/shirt.jpg');await p.waitForSelector('#ask_price',{timeout:8000});
 await p.fill('#ask_price','300');await p.click('text=ดูผล');await p.waitForTimeout(2200);
 let t=await p.textContent('#result');
 ok(t.includes('จากฐานความรู้ของระบบ')&&t.includes('Fruit of the Loom'),'KB card in result');ok(t.includes('เช็คด้วยมือ'),'hand-check card');ok(t.includes('ถ่ายทีละจุด'),'guided checkpoints');ok(t.includes('รู้ไว้'),'lesson shown');ok(t.includes('หักราคา'),'defect deduction');ok(t.includes('ข้อมูลราคาขายจริงน้อย'),'thin-data banner');
 await p.screenshot({path:__dirname+'/v21-result.png',fullPage:true});
 // hand check auth fail → PASS decision
 await p.locator('text=✗ ไม่ผ่าน').first().click();await p.waitForTimeout(400);t=await p.textContent('#result');
 ok(t.includes('เช็คด้วยมือไม่ผ่าน')&&t.includes('ไม่แนะนำ'),'auth hand fail → ไม่แนะนำ');
 await p.locator('text=✗ ไม่ผ่าน').first().click();await p.waitForTimeout(400);
 // shoot checkpoint
 const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.locator('button:has-text("ถ่าย")').first().click()]);await fc.setFiles(__dirname+'/shirt.jpg');await p.waitForTimeout(1500);
 t=await p.textContent('#result');ok(t.includes('สแกนใหม่ด้วยรูปทั้งหมด (2 รูป)'),'rescan button after checkpoint photo');
 await p.click('text=สแกนใหม่ด้วยรูปทั้งหมด');await p.waitForTimeout(2500);
 // ref add (two-step)
 await p.click('text=เก็บเป็นรูปอ้างอิงของแท้');await p.waitForTimeout(300);await p.click('text=กดอีกครั้งเพื่อยืนยัน');await p.waitForTimeout(1500);
 ok(refs.length===2,'refs uploaded: '+refs.length);
 // save deal
 await p.click('text=บันทึกเป็นดีล');await p.waitForTimeout(800);
 await p.locator('text=Pubs of Dublin').first().click();await p.waitForTimeout(600);
 ok((await p.textContent('#main')).includes('ของชิ้นนี้ปลอม/พลาด'),'mistake button in detail');
 await p.click('text=ช่วยขาย');await p.waitForTimeout(400);t=await p.textContent('#main');
 ok(t.includes('ไม่เขียนว่า "ของแท้"')&&!/ของแท้แน่นอน/.test(t),'honest listing');
 await p.click('text=ดูรูปที่ถ่ายตอนเช็ค');await p.waitForTimeout(500);ok(await p.locator('#dealPh img').count()===2,'deal photos from IndexedDB');
 await p.click('text=ภาพรวม >> nth=1').catch(()=>{});await p.waitForTimeout(300);
 await p.locator('button:has-text("ภาพรวม")').first().click().catch(()=>{});await p.waitForTimeout(300);
 await p.click('text=ของชิ้นนี้ปลอม/พลาด');await p.fill('#mk_what','ป้ายใหม่เย็บทับ');await p.click('#mkBox button');await p.waitForTimeout(600);
 ok(mistakes.length===1,'mistake sent');await p.click('text=ช่วยขาย');await p.waitForTimeout(300);ok((await p.textContent('#main')).includes('ไม่สร้างประกาศขาย'),'listing blocked after mistake');
 // batch mode + offline
 await p.goto('http://localhost:8788/');await p.waitForTimeout(800);
 await p.click('text=โหมดสแกนรัว');await p.waitForTimeout(500);
 await p.setInputFiles('#f_bimg',[__dirname+'/shirt.jpg',__dirname+'/shirt.jpg']);await p.waitForTimeout(2500);
 t=await p.textContent('#batchList');ok(t.includes('ซื้อไม่เกิน'),'batch scanned');
 await ctx.setOffline(true);await p.setInputFiles('#f_bimg',__dirname+'/shirt.jpg');await p.waitForTimeout(1200);
 t=await p.textContent('#batchList');ok(t.includes('รอเน็ต'),'offline queued');
 await ctx.setOffline(false);await p.waitForTimeout(2500);t=await p.textContent('#batchList');ok(!t.includes('รอเน็ต'),'auto-scan when online');
 const prices=p.locator('#batchList input[type=number]');for(let i=0;i<3;i++){await prices.nth(i).fill('250');await prices.nth(i).dispatchEvent('change');await p.waitForTimeout(150);}
 const picks=p.locator('#batchList input[type=checkbox]');await picks.nth(0).check();await p.waitForTimeout(150);await picks.nth(1).check();await p.waitForTimeout(300);
 ok((await p.textContent('#batchSum')).includes('กำไรรวมประมาณ'),'batch summary');
 await p.screenshot({path:__dirname+'/v21-batch.png',fullPage:true});
 await p.click('text=บันทึกตัวที่เลือกเป็นดีล');await p.waitForTimeout(1000);
 ok((await p.textContent('#main')).split('Pubs of Dublin').length>=3,'batch deals saved');
 // insights after sale
 const id=await p.evaluate(()=>Store.all().find(d=>d.name.includes('Pubs')&&!d.mistake).id);
 await p.evaluate(id=>go('/deal',id),id);await p.waitForTimeout(300);await p.click('text=ผลลัพธ์');await p.fill('#r_sell','1100');await p.click('text=บันทึกผลลัพธ์');await p.waitForTimeout(500);
 await p.evaluate(()=>go('/insights'));await p.waitForTimeout(500);t=await p.textContent('#main');
 ok(t.includes('ขายเร็ว-กำไรดี')&&t.includes('ความรู้ที่ได้'),'insights hunt list + lessons');
 await p.evaluate(()=>go('/find'));await p.waitForTimeout(400);ok((await p.textContent('#main')).includes('ของที่ควรมองหาวันนี้'),'hunt chips on scan page');
 await p.evaluate(()=>go('/kb'));await p.waitForTimeout(800);t=await p.textContent('#main');ok(t.includes('Screen Stars')&&t.includes('Big E'),'KB page lists entries');
 await p.fill('input[placeholder^="ค้น"]','big e');await p.waitForTimeout(300);t=await p.textContent('#kbList');ok(t.includes("Levi's")&&!t.includes('Screen Stars'),'KB search filter');
 await p.screenshot({path:__dirname+'/v22-kb.png'});
 console.log('scans',scanCount,'errors',errs);await b.close();srv.close();})().catch(e=>{console.log('TEST CRASH',e.message);process.exit(1)});
