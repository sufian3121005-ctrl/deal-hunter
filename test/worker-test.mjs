// run the real worker with fetch mocked (Gemini + Serper)
import worker from '../worker/worker.js';
let call=0;
globalThis.fetch=async(url,opt)=>{
  if(url.includes('serper')){const q=JSON.parse(opt.body).q;
    return new Response(JSON.stringify({organic: q.includes('ebay')?[
      {title:'Vintage 90s Pubs of Dublin T-Shirt Fruit of the Loom XL',snippet:'Sold Oct 2 2026 · $38.00',link:'https://www.ebay.com/itm/1'},
      {title:'Pubs of Dublin map tee single stitch',snippet:'Sold · $45.50',link:'https://www.ebay.com/itm/2'}]:[
      {title:'เสื้อวินเทจ Pubs of Dublin มือสอง',snippet:'฿1,290 ขายแล้ว',link:'https://shopee.co.th/x'},
      {title:'เสื้อ Dublin vintage 90s',snippet:'ราคา 950 บาท',link:'https://www.facebook.com/marketplace/1'}]}));}
  call++;
  const out = call===1 ? {name_th:'เสื้อยืดวินเทจ Pubs of Dublin',brand:'Fruit of the Loom',model:'Pubs of Dublin map',category:'apparel.vintage',era:'ยุค 90',condition:'good',id_confidence:82,notes:'',
     search_query_en:'vintage Pubs of Dublin t-shirt',search_query_th:'เสื้อวินเทจ Pubs of Dublin',
     auth:{level:'pass',summary:'ป้ายดูตรงยุค',checks:[{point:'ป้ายคอ',status:'pass',note:'Fruit of the Loom Best'},{point:'ตะเข็บปลายแขน',status:'not_photographed',note:''},{point:'ปีลิขสิทธิ์',status:'not_photographed',note:''},{point:'ลายสกรีน',status:'pass',note:''},{point:'เนื้อผ้า',status:'unclear',note:''},{point:'Made in',status:'not_photographed',note:''}],red_flags:[]},
     need_photos:['ตะเข็บปลายแขน','ปีลิขสิทธิ์ใต้ลาย'],est_price_thb:{low:600,mid:1000,high:1500}}
   : {items:[{i:0,amount:1290,currency:'THB',type:'sold',same_item:true},{i:1,amount:950,currency:'THB',type:'listing',same_item:true},{i:2,amount:38,currency:'USD',type:'sold',same_item:true},{i:3,amount:45.5,currency:'USD',type:'sold',same_item:true}]};
  return new Response(JSON.stringify({candidates:[{content:{parts:[{text:JSON.stringify(out)}]}}]}));
};
const env={GEMINI_API_KEY:'x',SERPER_API_KEY:'y',APP_KEY:'k'};
const bad=await worker.fetch(new Request('https://w/api/scan',{method:'POST',body:'{}'}),env); console.log('no key ->',bad.status);
const r=await worker.fetch(new Request('https://w/api/scan',{method:'POST',headers:{'x-app-key':'k'},body:JSON.stringify({images:['data:image/jpeg;base64,AAAA']})}),env);
const d=await r.json(); console.log(r.status, JSON.stringify(d,null,1).slice(0,1800));
import fs from 'fs'; fs.writeFileSync('test/sample-response.json',JSON.stringify(d));
