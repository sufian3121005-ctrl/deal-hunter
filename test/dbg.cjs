const fs=require('fs');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>m.type()==='error'&&console.log('CON',m.text()));
await p.route('**/cdn.tailwindcss.com/**',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(__dirname+'/node_modules/@tailwindcss/browser/dist/index.global.js')}));
await p.route('**/unpkg.com/**',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(__dirname+'/node_modules/lucide/dist/umd/lucide.min.js')}));
await p.route('**/fonts.googleapis.com/**',r=>r.fulfill({contentType:'text/css',body:''}));
for(const f of [process.argv[2]]){await p.goto('file://'+f);await p.waitForTimeout(1000);}
await b.close();})();
