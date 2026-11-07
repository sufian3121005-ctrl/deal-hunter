import worker from '../worker/worker.js';
let prompt='';
globalThis.fetch=async(url,opt)=>{const b=JSON.parse(opt.body);prompt=b.contents[0].parts[0].text;
 const out={name_th:"กางเกงยีนส์ Levi's 501 Big E",brand:"Levi's",model:'501',category:'apparel.denim',era:'ก่อน 1971',condition:'good',id_confidence:80,notes:'แท็บแดง Big E, มีผ้าริม selvedge',
  auth:{level:'suspicious',checks:[{point:'แท็บแดง',status:'pass',note:'Big E'}],red_flags:[]},defects:[],photo_quality:[],need_photos:[],lesson:'x',kb_used:['levis-tab'],est_price_thb:{low:2000,mid:4000,high:6000}};
 return new Response(JSON.stringify({candidates:[{content:{parts:[{text:JSON.stringify(out)}]}}]}));};
const env={GEMINI_API_KEY:'x',DOUBLE_CHECK_ABOVE:'999999'};
const r=await worker.fetch(new Request('https://w/api/scan',{method:'POST',body:JSON.stringify({images:['data:image/jpeg;base64,AA']})}),env);
const d=await r.json();
console.log('status',r.status,'category',d.item.category,'denim checkpoints',d.checkpoints.length);
console.log('prompt has KB:',prompt.includes('[levis-tab]'),'prompt length',prompt.length);
console.log('kb_matches:',d.kb_matches.map(m=>m.id).join(', '));
const k=await (await worker.fetch(new Request('https://w/api/kb'),env)).json();console.log('/api/kb entries',k.entries.length);
