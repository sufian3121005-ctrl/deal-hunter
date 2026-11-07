import worker from '../worker/worker.js';
import fs from 'fs';
// --- mock KV ---
const store=new Map(),meta=new Map();
const KV={async get(k,t){const v=store.get(k);return v==null?null:(t==='json'?JSON.parse(v):v)},async put(k,v,o){store.set(k,v);meta.set(k,o&&o.metadata)},
 async list({prefix}){return{keys:[...store.keys()].filter(k=>k.startsWith(prefix)).map(name=>({name,metadata:meta.get(name)}))}}};
let calls=[];let secondLevel='pass';
globalThis.fetch=async(url,opt)=>{
  if(url.includes('serper')){const q=JSON.parse(opt.body).q;return new Response(JSON.stringify({organic:q.includes('ebay')?[{title:'Vintage Pubs of Dublin tee',snippet:'Sold $38.00',link:'https://www.ebay.com/itm/1'}]:[{title:'เสื้อ Pubs of Dublin',snippet:'฿1,290 ขายแล้ว',link:'https://shopee.co.th/x'},{title:'Dublin 90s',snippet:'950 บาท',link:'https://facebook.com/m/1'}]}))}
  const body=JSON.parse(opt.body);const txt=body.contents[0].parts[0].text;calls.push(txt.slice(0,40));
  let out;
  if(txt.startsWith('เทียบสินค้า')) out={level:'high_risk',summary:'ป้ายคอฟอนต์ต่างจากของแท้',differences:['ฟอนต์ป้ายคอหนากว่า']};
  else if(txt.startsWith('จากผลค้นหา')) out={items:[{i:0,amount:1290,currency:'THB',type:'sold'},{i:1,amount:950,currency:'THB',type:'listing'},{i:2,amount:38,currency:'USD',type:'sold'}]};
  else { const n=calls.filter(c=>c.startsWith('คุณคือ')).length;
    out={name_th:'เสื้อวินเทจ Pubs of Dublin',brand:'Fruit of the Loom',model:'Pubs of Dublin',category:'apparel.vintage',era:'ยุค 90',size:'XL',condition:'good',id_confidence:85,
     search_query_en:'vintage pubs of dublin tee',search_query_th:'เสื้อ pubs of dublin',
     auth:{level:n===1?'pass':secondLevel,summary:'ป้ายตรงยุค',checks:[{point:'ป้ายคอ',status:'pass'},{point:'RN',status:'pass'},{point:'ตะเข็บ',status:'pass'},{point:'ปี',status:'not_photographed'}],red_flags:[]},
     defects:[{what:'รูเล็กที่ชายเสื้อ',severity:'minor',price_impact_pct:10}],photo_quality:[{index:1,ok:true}],need_photos:['ปีลิขสิทธิ์'],lesson:'ป้าย Fruit of the Loom แบบนี้พบในยุค 90',
     est_price_thb:{low:2500,mid:3500,high:4500}};
    if(txt.includes('บทเรียนจากของปลอม')) out.notes='saw-mistakes'; }
  return new Response(JSON.stringify({candidates:[{content:{parts:[{text:JSON.stringify(out)}]}}]}));
};
const env={GEMINI_API_KEY:'x',SERPER_API_KEY:'y',APP_KEY:'k',CACHE:KV};
const call=async(path,method='GET',b)=>{const r=await worker.fetch(new Request('https://w'+path,{method,headers:{'x-app-key':'k','content-type':'application/json'},body:b?JSON.stringify(b):undefined}),env);return [r.status,r.headers.get('content-type'),r.headers.get('content-type').includes('json')?await r.json():null]};
const img='data:image/jpeg;base64,'+fs.readFileSync('test/shirt.jpg').toString('base64');
// 1 plain scan (no refs, est 3500 >= 3000 → double check, second disagrees)
secondLevel='suspicious';
let [st,,d]=await call('/api/scan','POST',{images:[img],labels:['ตัวสินค้าเต็มชิ้น']});
console.log('1 scan',st,'level',d.auth.level,'disagree',d.auth.disagree,'double',d.auth.double_checked,'defects',d.defects.length,'lesson',!!d.lesson,'size',d.item.size,'cps',d.checkpoints.length,'calls',calls.length);
fs.writeFileSync('test/sample-response.json',JSON.stringify({...d,auth:{...d.auth,level:'suspicious'}}));
// 2 refs
[st,,d]=await call('/api/refs','POST',{category:'apparel.vintage',checkpoint:'ป้ายคอถ่ายใกล้ๆ ให้อ่านตัวหนังสือได้',image:img,note:'ของแท้'});console.log('2 addRef',st,d.ok);
[st,,d]=await call('/api/refs?category=apparel.vintage');console.log('  list',d.items.length,d.items[0].checkpoint.slice(0,10));
let r=await worker.fetch(new Request('https://w/api/refs/img?key='+encodeURIComponent(d.items[0].key)+'&k=k'),env);console.log('  img',r.status,r.headers.get('content-type'),(await r.arrayBuffer()).byteLength);
// 3 mistakes
[st,,d]=await call('/api/mistakes','POST',{category:'apparel.vintage',name:'เสื้อ X',what:'ป้ายใหม่เย็บทับ'});console.log('3 mistake',st,d.total);
// 4 scan with refs + mistakes → compare high_risk
calls=[];secondLevel='pass';
[st,,d]=await call('/api/scan','POST',{images:[img],labels:['ตัวสินค้าเต็มชิ้น']});
console.log('4 scan w/ refs',st,'level',d.auth.level,'refs_used',d.auth.refs_used,'flags',d.auth.red_flags,'mistakes in prompt',d.item.notes);
// 5 luxury rule + no KV
// 6 unauthorized
r=await worker.fetch(new Request('https://w/api/refs'),env);console.log('6 noauth',r.status);
r=await worker.fetch(new Request('https://w/api/refs',{headers:{'x-app-key':'k'}}),{...env,CACHE:undefined});console.log('7 noKV',r.status,(await r.json()).error);
