import worker from '../worker/worker.js';
let prompt='';
globalThis.fetch=async(url,opt)=>{const b=JSON.parse(opt.body);prompt=b.contents[0].parts[0].text;
 const out={name_th:'เสื้อแมนยู ชุดเหย้า 1996 Umbro สปอนเซอร์ Sharp',brand:'Umbro',model:'Manchester United 1996 home',category:'apparel.football',era:'1996',condition:'good',id_confidence:80,notes:'ป้ายคอ Umbro สีน้ำเงิน',
  auth:{level:'suspicious',checks:[{point:'ป้ายคอ',status:'pass',note:'มีจุดในตัวอักษร UMBRO'}],red_flags:[]},defects:[],photo_quality:[],need_photos:[],lesson:'x',kb_used:['fb-umbro','fb-demand-thai'],est_price_thb:{low:1500,mid:2500,high:4000}};
 return new Response(JSON.stringify({candidates:[{content:{parts:[{text:JSON.stringify(out)}]}}]}));};
const r=await worker.fetch(new Request('https://w/api/scan',{method:'POST',body:JSON.stringify({images:['data:image/jpeg;base64,AA']})}),{GEMINI_API_KEY:'x'});
const d=await r.json();console.log('football:',r.status,d.item.category,d.checkpoints.length,'cps; kb:',d.kb_matches.map(m=>m.id).join(', '),'; prompt chars',prompt.length);
