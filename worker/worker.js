// =============================================================
//  Deal Hunter — หลังบ้าน (Cloudflare Worker)  v2.1
//
//  POST /api/scan      { images:[dataURL], labels?:[string], hint?:{name, hand:[{q,ok}]} }
//  GET  /api/refs?category=apparel.vintage        รายการรูปอ้างอิงของแท้
//  POST /api/refs      { category, checkpoint, image, note }   เพิ่มรูปอ้างอิงของแท้
//  GET  /api/refs/img?key=...                      ดึงรูปอ้างอิง
//  POST /api/mistakes  { category, name, what }   บันทึกว่าพลาด/ของปลอม เพื่อให้ AI ระวังครั้งต่อไป
//  GET  /api/mistakes?category=...
//
//  ตัวแปรใน Cloudflare (Settings → Variables and Secrets):
//    GEMINI_API_KEY       (จำเป็น)
//    SERPER_API_KEY       (แนะนำ)   ค้นราคาตลาด
//    APP_KEY              (แนะนำ)   รหัสผ่านแอป
//    GEMINI_MODEL         (ไม่บังคับ) ค่าเริ่มต้น gemini-2.5-flash
//    USD_THB              (ไม่บังคับ) ค่าเริ่มต้น 33
//    DOUBLE_CHECK_ABOVE   (ไม่บังคับ) ราคา (บาท) ที่ให้ AI ตรวจของแท้ซ้ำรอบสอง ค่าเริ่มต้น 3000
//  KV binding ชื่อ CACHE (แนะนำ): แคชราคา + คลังรูปของแท้ + บันทึกของปลอม
// =============================================================

const CATEGORIES = {
  'apparel.vintage': {
    th: 'เสื้อวินเทจ',
    checks: [
      'ป้ายคอ: ยี่ห้อป้ายและรูปแบบป้ายตรงกับยุคที่อ้าง (เช่น Fruit of the Loom, Screen Stars, Hanes, Anvil, Giant)',
      'เลข RN บนป้าย (ถ้ามี) อ่านได้ชัด ใช้ระบุผู้ผลิต',
      'ความเก่าของป้ายสอดคล้องกับตัวเสื้อ (เสื้อซีดมากแต่ป้ายใหม่เอี่ยม = สัญญาณอันตราย)',
      'ตะเข็บปลายแขนและชายเสื้อ: ตะเข็บเดี่ยว (single stitch) พบมากในเสื้อก่อนกลางยุค 90',
      'ตัวเสื้อไม่มีตะเข็บข้าง (tubular) พบบ่อยในเสื้อยุคเก่า',
      'ปีลิขสิทธิ์ (©) ใต้ลายสกรีน สอดคล้องกับป้ายและตะเข็บ',
      'ลายสกรีนเก่าพอๆ กับเนื้อผ้า (ผ้าซีดแต่ลายสดใหม่ = อาจพิมพ์ใหม่บนเสื้อเก่า) ไม่ใช่พิมพ์ดิจิทัลหรือฟอกให้ดูเก่า',
      'ป้ายประเทศผลิตและป้ายวิธีซัก สอดคล้องกับยุค'
    ],
    photos: ['ป้ายคอถ่ายใกล้ๆ ให้อ่านตัวหนังสือได้', 'ป้ายวิธีซัก/เลข RN', 'ตะเข็บปลายแขนด้านใน', 'ตะเข็บชายเสื้อด้านใน', 'ด้านข้างลำตัว (ดูว่ามีตะเข็บข้างไหม)', 'ปีลิขสิทธิ์ใต้ลายสกรีน'],
    defects: 'รู, คราบ, คราบเหลืองใต้รักแร้, คอยืด, ลายแตกมาก, สีตก, ขาด'
  },
  'apparel.denim': {
    th: 'ยีนส์/แจ็คเก็ต/เสื้อผ้าวินเทจ',
    checks: [
      "แท็บแดง Levi's: Big E (ก่อน 1971) หรือ small e และพิมพ์สองด้านหรือไม่",
      'ป้ายวิธีซัก: มีหรือไม่ และรหัสวันผลิต (3 หลักตั้งแต่ราว 1984, 4 หลักตั้งแต่ 1993) สอดคล้องกับยุคที่อ้าง',
      'ป้ายหลังเอว: หนัง (ราวก่อน 1955) หรือกระดาษ และเลขรุ่น',
      'ผ้าริม (selvedge) ด้านในตะเข็บข้างขา และสีโพ้ง (ส้มราว 1981, ขาวราว 1985)',
      'กระเป๋าหลัง: หมุดซ่อน (1937–1966) หรือบาร์แทค, ตะเข็บด้านบนกระเป๋า',
      'ด้านหลังกระดุมเม็ดบน: ตัวเลขโรงงาน (อ่านให้ได้)',
      'การซีด: rope dye ซีดแนวตั้ง/รังผึ้งตามธรรมชาติ ไม่ใช่ฟอกสม่ำเสมอ'
    ],
    photos: ['แท็บแดงที่กระเป๋าหลังใกล้ๆ', 'ป้ายหลังเอว', 'ป้ายวิธีซักด้านใน (ให้เห็นรหัสวันที่)', 'ด้านในตะเข็บข้างขา (ดูผ้าริม)', 'ด้านหลังกระดุมเม็ดบน', 'กระเป๋าหลังด้านใน (หมุด/บาร์แทค)'],
    defects: 'ขาดที่เป้า/ก้น, ขอบขาลุ่ย, ซิปเสีย, คราบสี, รอยปะ, ผ้าบางจนเกือบขาด'
  },
  'apparel.football': {
    th: 'เสื้อฟุตบอล',
    checks: [
      'ป้ายรหัสสินค้า: Nike ป้ายเล็กใกล้ชายเสื้อ (ตัวเลข 6 หลัก-3 หลัก), adidas ป้ายคอด้านใน (อักษร 2 ตัว + ตัวเลข 4 ตัว) อ่านให้ได้',
      'ป้ายคอ: Umbro ยุค 90 ตัวอักษรมีจุด, Kappa ยุค 90 จุด 6 จุดเรียงทแยง, adidas มีตัวย่อชื่อทีม',
      'โลโก้แบรนด์: ขอบคม ไม่มีด้ายลาก ระยะตัวอักษรสม่ำเสมอ',
      'ตราสโมสร: แบบรีดร้อน (รุ่นนักเตะ) หรือปัก (รุ่นแฟน) และด้านในไม่มีวัสดุรองเกิน',
      'Jock tag ด้านหน้ามุมล่าง (ถ้ามี) ตรงกับรุ่น',
      'สปอนเซอร์ สี และลายตรงกับฤดูกาลที่อ้าง'
    ],
    photos: ['ป้ายรหัสสินค้าด้านใน (ให้อ่านรหัสได้)', 'ป้ายคอด้านใน', 'โลโก้แบรนด์ใกล้ๆ', 'ตราสโมสรด้านหน้า', 'ด้านในหลังตราสโมสร', 'jock tag มุมล่างด้านหน้า'],
    defects: 'เบอร์/ชื่อร่อนหรือละลาย, สปอนเซอร์ลอก, ขุย, ด้ายดึง, รูรักแร้, คราบเหลืองคอ'
  },
  'tools.power': {
    th: 'เครื่องมือช่าง',
    checks: [
      'เพลทรุ่นและ serial ชัดเจน ไม่ถูกขูดหรือแกะ',
      'โลโก้และฟอนต์บนฉลากตรงกับของแท้ (ของปลอมมักใช้ฟอนต์หนาทึบกว่า)',
      'แบต Makita: ใต้แบตมีปลั๊กสีขาวใกล้ด้านหน้า',
      'แบต Makita: กดปุ่มปลดล็อกแล้วเห็นแถบสีแดงด้านใน',
      'แบต: ช่องขั้วต่อเรียบตรง ไม่แหลมขรุขระ, รางสไลด์ลาดนุ่ม ไม่หักฉาก',
      'วัสดุและงานประกอบบอดี้ ไม่มีรอยต่อหยาบหรือพลาสติกบาง'
    ],
    photos: ['เพลทรุ่น/serial ใต้ตัวเครื่อง', 'โลโก้และฉลากใกล้ๆ', 'ใต้แบตเตอรี่ (ปลั๊กสีขาว/ขั้วต่อ)', 'รางสไลด์ของแบตด้านข้าง'],
    defects: 'บอดี้แตก, สายไฟชำรุด, หัวจับดอกหลวม, สนิม, แบตบวม, ไหม้'
  },
  'shoes.brand': {
    th: 'รองเท้าแบรนด์',
    checks: [
      'ป้ายในลิ้นรองเท้า: รหัสรุ่น (style code) ตรงกับสีและรุ่น',
      'ตะเข็บสม่ำเสมอ ไม่มีกาวล้น',
      'พื้นรองเท้าและโลโก้ด้านหลัง',
      'กล่องและป้ายกล่องตรงกับรองเท้า'
    ],
    photos: ['ป้ายในลิ้นรองเท้า', 'ตะเข็บด้านข้าง', 'พื้นรองเท้า', 'ป้ายกล่อง'],
    defects: 'พื้นสึก, หนังแตก, กาวหลุด, คราบเหลือง'
  },
  'luxury': {
    th: 'กระเป๋า/นาฬิกาแบรนด์เนม',
    checks: ['รหัสผลิต/serial', 'ฟอนต์และการปั๊มโลโก้', 'อะไหล่โลหะและงานเย็บ', 'ใบรับประกัน/ใบเสร็จ'],
    photos: ['รหัสผลิต/serial', 'โลโก้ใกล้ๆ', 'อะไหล่โลหะ', 'ใบรับประกัน'],
    defects: 'มุมถลอก, หนังลอก, กระจกร้าว'
  },
  'generic': {
    th: 'ทั่วไป',
    checks: ['ยี่ห้อ/โลโก้ชัดเจนและถูกต้อง', 'มีรุ่นหรือ serial ให้ตรวจสอบได้', 'สภาพโดยรวมและความครบชุด'],
    photos: ['ป้ายหรือโลโก้ใกล้ๆ', 'รุ่น/serial (ถ้ามี)'],
    defects: 'แตก, ชำรุด, ขาดชิ้นส่วน'
  }
};
const CAT_KEYS = ['apparel.vintage', 'apparel.denim', 'apparel.football', 'tools.power', 'shoes.brand', 'luxury', 'phone', 'appliance', 'generator', 'bike', 'furniture', 'generic'];

// ฐานความจำ (สร้างจาก knowledge/apparel-kb.json ด้วย tools/build_worker.py — อย่าแก้ตรงนี้ด้วยมือ)
const KB = /*KB_START*/[{"id": "rule-stitch", "category": "apparel.vintage", "kind": "rule", "brand": "", "title": "ตะเข็บเดี่ยว vs ตะเข็บคู่", "era": "ก่อนปลายยุค 90", "keywords": ["single stitch", "ตะเข็บเดี่ยว", "double stitch"], "cues": ["ตะเข็บเดี่ยวที่ปลายแขนและชายเสื้อ = เสื้อวินเทจโดยทั่วไป", "ตะเข็บคู่สองแถว = มักผลิตหลังปลายยุค 90"], "red_flags": ["ข้อยกเว้น: เสื้อทัวร์ยุโรปปลายยุค 90 บางตัวใช้ตะเข็บคู่ ใช้ประกอบกับป้ายเสมอ"], "value_notes": "", "confidence": "sourced", "sources": ["https://nostos.pages.dev/guides/vintage-band-tee-reprint-and-bootleg-identification-guide"]}, {"id": "rule-print", "category": "apparel.vintage", "kind": "rule", "brand": "", "title": "ดูลายสกรีน: ของเก่าจริง vs พิมพ์ใหม่", "era": "", "keywords": ["print", "สกรีน", "dtg", "heat transfer"], "cues": ["สกรีนยุคเก่า: หมึกแตก ซีด ซึมลงเนื้อผ้า จับแล้วนุ่ม", "พิมพ์ DTG สมัยใหม่: หมึกหนา ยาง มันวาว ลอยบนผ้า", "ลายรีดร้อน (heat transfer) ยุค 1993–2000 เป็นของจริงแต่ราคาต่ำกว่าสกรีน: ขอบคม ผิวคล้ายพลาสติก ด้านในไม่มีหมึกซึม"], "red_flags": ["ผ้าซีดเก่าแต่ลายสดใหม่ = อาจพิมพ์ใหม่บนเสื้อเก่า"], "value_notes": "", "confidence": "sourced", "sources": ["https://nostos.pages.dev/guides/vintage-band-tee-reprint-and-bootleg-identification-guide"]}, {"id": "rule-fake-aging", "category": "apparel.vintage", "kind": "rule", "brand": "", "title": "ทำเก่าปลอม vs เก่าจริง", "era": "", "keywords": ["distressed", "ฟอก", "ทำเก่า"], "cues": ["เก่าจริง: ซีดแดดตามธรรมชาติ รูเข็มเล็กๆ แถวคอ/เอว คอนิ่มและลุ่ย"], "red_flags": ["ฟอกเคมีเป็นด่างไม่เป็นธรรมชาติ", "รูที่ตัดด้วยกรรไกร", "คอที่ขัดกระดาษทราย", "ตัดป้ายออกจนเป็นรูเละ หรือเป็นป้ายฉีกแบบกระดาษสมัยใหม่"], "value_notes": "", "confidence": "sourced", "sources": ["https://nostos.pages.dev/guides/vintage-band-tee-reprint-and-bootleg-identification-guide"]}, {"id": "rule-weak-signals", "category": "apparel.vintage", "kind": "rule", "brand": "", "title": "สัญญาณที่ใช้ตัดสินยุคอย่างเดียวไม่ได้", "era": "", "keywords": ["made in usa", "50/50", "double tag"], "cues": ["Made in USA, ผ้า 50/50, ป้ายซ้อนสองชั้น พบได้หลายแบรนด์หลายยุค ต้องใช้ร่วมกับรูปแบบป้ายและตะเข็บ", "ช่วงปีของแต่ละแบรนด์ทับซ้อนกัน ใช้ช่วงปีอย่างเดียวระบุแบรนด์ไม่ได้"], "red_flags": [], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide"]}, {"id": "rule-copyright", "category": "apparel.vintage", "kind": "rule", "brand": "", "title": "ปีลิขสิทธิ์ (©) บนลายสกรีน", "era": "", "keywords": ["©", "copyright", "ลิขสิทธิ์"], "cues": ["ปี © คือปีที่ลายได้ลิขสิทธิ์ ไม่ใช่ปีที่พิมพ์เสื้อ และไม่ค่อยถูกอัปเดต เสื้อพิมพ์ยุค 2000 อาจยังเขียน © 1994", "มีหลายปี: ปีแรกคือลิขสิทธิ์เดิม ปีหลังคือแก้ไข เสื้อมักผลิตหลังปีล่าสุด (เช่น Snoopy 1958/1965/1971 น่าจะผลิตยุค 80 ขึ้นไป)", "ตัวอย่าง: Metallica Ride the Lightning ที่พิมพ์ยุค 2000 มักมี © 1994", "เสื้อวงที่พิมพ์ยุค 2000 หลายตัวไม่มีบรรทัด © เลย"], "red_flags": ["ไม่มี © ไม่ได้แปลว่าปลอม (bootleg เก่าหลายตัวไม่มี)", "มี © ก็ไม่ได้แปลว่าแท้ เพราะ bootleg ก็ลอก © ได้", "ใช้ปี © ตัดสินยุคอย่างเดียวไม่ได้ ต้องดูป้ายและงานพิมพ์ประกอบ"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.defunkd.com/copyrights-on-vintage-t-shirts/"]}, {"id": "rule-rn", "category": "apparel.vintage", "kind": "rule", "brand": "", "title": "เลข RN บนป้าย", "era": "", "keywords": ["rn", "rn number", "wpl"], "cues": ["RN คือเลขที่ FTC สหรัฐฯ ออกให้ผู้ผลิต/ผู้นำเข้า ใช้ค้นว่าใครผลิต", "Screen Stars ใช้ RN 13765"], "red_flags": ["RN หรือ WPL สมัยใหม่บนป้ายที่อ้างว่าเก่า = สัญญาณป้ายปลอม"], "value_notes": "", "confidence": "sourced", "sources": ["https://1800vintage.substack.com/p/rn-numbers", "https://www.defunkd.com/blog/2016/12/06/the-screen-stars-timeline/amp/", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "rule-fake-tag", "category": "apparel.vintage", "kind": "rule", "brand": "", "title": "สัญญาณป้ายคอปลอม (ทั่วไป)", "era": "", "keywords": ["fake tag", "ป้ายปลอม"], "cues": ["เทียบกับป้ายแท้หลายๆ ใบ เพราะป้ายแท้เองก็มีหลายแบบ", "ดูทั้งป้ายและลายสกรีนประกอบกัน"], "red_flags": ["โลโก้หนาทึบ เส้นด้ายหยาบ จุดลายหายไป", "ฟอนต์ ความสูงตัวอักษร ระยะห่างผิด", "สะกดผิด", "ขาดรายละเอียด เงา ขอบ หรือความแวววาว", "สีผิด", "ไซซ์บนป้ายไม่ตรงกับขนาดจริง", "ป้ายรอง/เลข RN-WPL ไม่ตรงยุค", "ตำแหน่ง ™ ผิด"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-screen-stars", "category": "apparel.vintage", "kind": "tag", "brand": "Screen Stars", "title": "Screen Stars", "era": "1980–1994", "keywords": ["screen stars", "screenstars", "super screen stars", "screen stars best"], "cues": ["1980: ป้ายแรก สีน้ำเงิน/ขาว/ส้ม ใช้ปีเดียว ส่วนใหญ่ 50/50", "1981–1983: ตัว A แบบ \"Funky A\" (แบบที่ดังที่สุด), Super Screen Stars แถบเขียว 50/50, แถบน้ำเงิน 100% cotton", "1983–1990: ตัว A แบบเรียบขึ้น, มีรุ่น Made in Canada / Ireland / El Salvador", "1987–90s: Screen Stars Best แถบแดง 50/50 และแถบน้ำเงิน 100% cotton", "RN 13765 (เครือ Fruit of the Loom)"], "red_flags": ["ป้าย \"Screen Stars by FOTL Value Weight\" ปลอม: น้ำเงินเข้มเกิน กล่องสี่เหลี่ยมจัตุรัส ฟอนต์ \"by\" ผิด"], "value_notes": "ป้ายที่นักสะสมรู้จักดี เสื้อลายดีบนป้ายนี้มักขายได้ราคา", "confidence": "sourced", "sources": ["https://www.defunkd.com/blog/2016/12/06/the-screen-stars-timeline/amp/", "https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-fotl", "category": "apparel.vintage", "kind": "tag", "brand": "Fruit of the Loom", "title": "Fruit of the Loom", "era": "1970–1998 (ป้ายวินเทจ)", "keywords": ["fruit of the loom", "fotl", "fruit"], "cues": ["มีรูปแบบป้ายแยกช่วง 1970s–1983 และ 1984–1993", "มีรุ่น \"Best\" และ Lofteez/heavy cotton แบบป้ายซ้อน", "ป้ายยุค 2004–2012 ไม่นับเป็นวินเทจยุคทอง"], "red_flags": ["ป้ายปลอม: ไม่มีรายละเอียดและเงาของผลไม้ และองุ่นเป็นสีม่วง"], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-hanes", "category": "apparel.vintage", "kind": "tag", "brand": "Hanes", "title": "Hanes", "era": "1989–1997", "keywords": ["hanes", "beefy-t", "beefy", "ultraweight", "hanes heavyweight"], "cues": ["ป้าย 50/50, 100% cotton, Ultraweight, Beefy-T, Heavyweight, ป้ายซ้อน, Made in USA"], "red_flags": ["Heavyweight ปลอม: เครื่องหมาย ® เหนือตัว S กลับด้าน", "Ultraweight ปลอม: ตัว H สูงเกิน", "แถบน้ำเงินปลอม: ขาตัว H ไม่ยาวสุด", "Heavyweight ป้ายซ้อนปลอม: ป้ายล่างสั้นเกิน ฟอนต์และตำแหน่งผิด"], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-anvil", "category": "apparel.vintage", "kind": "tag", "brand": "Anvil", "title": "Anvil (และ Ched)", "era": "Anvil 1989–2007, Ched 1976–1988", "keywords": ["anvil", "ched"], "cues": ["Ched quality knits / Anvil Athletic / Ched by Anvil = 1976–1988", "Anvil 100% cotton pre-shrunk Made in USA, ป้ายแถบน้ำเงิน/แดง"], "red_flags": ["Anvil แถบน้ำเงิน ผลิตนิการากัว เริ่มราว 2004 ถ้าอ้างว่าเก่ากว่านี้ = น่าสงสัย"], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-giant", "category": "apparel.vintage", "kind": "tag", "brand": "Giant", "title": "Giant", "era": "1991–1996", "keywords": ["giant", "tee jays", "giant by"], "cues": ["Giant by Tee Jays / by Anvil / by Tultex, ผลิต El Salvador", "พบมากบนเสื้อวงดนตรียุค 90"], "red_flags": ["ป้ายปลอมเยอะมาก: โลโก้หนาเกินไม่มีจุดลาย, ฟอนต์ใต้ \"Tee Jays\" ผิดขนาด", "สะกด \"SY\" แทน \"BY\"", "Giant by Tultex แท้ ตัว LT ใน TULTEX เกี่ยวกัน", "Silver Thread ปลอม: สะกดผิดที่ป้ายล่าง ™ สีแดง"], "value_notes": "ป้ายนี้อยู่บนเสื้อวงที่ราคาสูง จึงถูกปลอมบ่อย ตรวจละเอียด", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-winterland", "category": "apparel.vintage", "kind": "tag", "brand": "Winterland", "title": "Winterland", "era": "1982–2008", "keywords": ["winterland"], "cues": ["Winterland Productions พบบนเสื้อวงร็อกคลาสสิกและเสื้อวงฝั่งตะวันตก (สาย Grateful Dead)"], "red_flags": ["ป้ายปลอม: โลโก้สูงเกิน กรอบรอบตัว W สูงเกิน ™ ต่ำเกิน ข้อความขาด/สะกดผิด"], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/", "https://nostos.pages.dev/guides/vintage-band-tee-reprint-and-bootleg-identification-guide"]}, {"id": "tag-brockum", "category": "apparel.vintage", "kind": "tag", "brand": "Brockum", "title": "Brockum", "era": "ก่อน 1995", "keywords": ["brockum"], "cues": ["ป้าย Brockum บ่งชี้เสื้อทัวร์ก่อนปี 1995 (เช่น Rolling Stones, U2)"], "red_flags": ["Brockum Worldwide ปลอม: ฟอนต์ยืด ระยะห่างผิด โลโก้ชิดกรอบเกิน", "The Brockum Group ปลอม: O กับ C ห่างเกิน", "The Brockum Collection ปลอม: ไม่มีเงาเงิน สีฟ้าผิด"], "value_notes": "เสื้อทัวร์ทางการยุคนั้น ราคาสูง", "confidence": "sourced", "sources": ["https://nostos.pages.dev/guides/vintage-band-tee-reprint-and-bootleg-identification-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-stedman", "category": "apparel.vintage", "kind": "tag", "brand": "Stedman", "title": "Stedman / Hi-Cru", "era": "1971–1997", "keywords": ["stedman", "hi-cru", "hi cru"], "cues": ["Hi-Cru, Sport-T by Stedman, Golden Hi-Cru, Super Hi-Cru, Stedman by Hanes, Made in USA"], "red_flags": ["ป้ายปลอม: ฟอนต์ผิดเกือบทั้งหมด"], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-sportswear", "category": "apparel.vintage", "kind": "tag", "brand": "Sportswear", "title": "Sportswear", "era": "1968–1990", "keywords": ["sportswear"], "cues": ["สองชุดป้าย: 1968–1981 และ Sportswear II 1981–1990"], "red_flags": [], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide"]}, {"id": "tag-signal", "category": "apparel.vintage", "kind": "tag", "brand": "Signal", "title": "Signal", "era": "1977–1994", "keywords": ["signal", "signal artwear", "ssi"], "cues": ["100% cotton, Sports, SSI, Signal Artwear, Signal Sport"], "red_flags": [], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide"]}, {"id": "tag-jerzees", "category": "apparel.vintage", "kind": "tag", "brand": "Jerzees", "title": "Jerzees", "era": "1985–1998", "keywords": ["jerzees", "russell"], "cues": ["Jerzees by Russell, Super-T, 100% combed cotton, pre-shrunk"], "red_flags": [], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide"]}, {"id": "tag-oneita", "category": "apparel.vintage", "kind": "tag", "brand": "Oneita", "title": "Oneita", "era": "1984–1999", "keywords": ["oneita", "power-t", "powerpro"], "cues": ["Power-T, PowerPro, Power/50, ผ้า 50/50 หรือ 100%"], "red_flags": ["Power-T สีปลอม: ระยะห่างตัวอักษรโลโก้กว้างเกิน"], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-delta", "category": "apparel.vintage", "kind": "tag", "brand": "Delta", "title": "Delta", "era": "1988–2014", "keywords": ["delta", "pro-weight", "magnum weight"], "cues": ["Pro-Weight, Magnum Weight, Made in USA; ช่วง 2002–2013 ประกอบที่ฮอนดูรัส (ใหม่กว่า)"], "red_flags": [], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide"]}, {"id": "tag-tennessee-river", "category": "apparel.vintage", "kind": "tag", "brand": "Tennessee River", "title": "Tennessee River", "era": "1984–2010", "keywords": ["tennessee river"], "cues": ["ป้ายสีทอง, ป้ายซ้อน, ประกอบที่เม็กซิโก (รุ่นหลัง)"], "red_flags": [], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide"]}, {"id": "tag-wild-oats", "category": "apparel.vintage", "kind": "tag", "brand": "Wild Oats", "title": "Wild Oats", "era": "1984–1997", "keywords": ["wild oats"], "cues": ["Made in USA, ข้อความ \"100% oats\""], "red_flags": ["ป้ายปลอม: เขียน LG ข้าง XL (ของแท้เป็น TG)"], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-alstyle", "category": "apparel.vintage", "kind": "tag", "brand": "Alstyle", "title": "Alstyle (AAA)", "era": "1995–2006", "keywords": ["alstyle", "aaa"], "cues": ["เครื่องหมาย AAA, 100% cotton pre-shrunk, ทำที่เม็กซิโกจากผ้าสหรัฐฯ"], "red_flags": ["ป้ายปลอม: มีเส้นเกินที่ด้านล่าง ฟอนต์และระยะห่างผิด"], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-gildan", "category": "apparel.vintage", "kind": "tag", "brand": "Gildan", "title": "Gildan", "era": "1995–2002 (ป้ายยุคเก่า)", "keywords": ["gildan", "ultra cotton"], "cues": ["ป้าย Heavyweight / Ultra Cotton ยุคปลาย 90", "Gildan ยังผลิตจนปัจจุบัน ป้ายรุ่นใหม่ไม่นับเป็นวินเทจ"], "red_flags": ["เสื้อวงที่อ้างว่ายุค 80 แต่ป้าย Gildan = ผลิตใหม่ (reprint)", "Ultra Cotton ปลอม: ระยะตัวอักษรและฟอนต์แถบน้ำเงินผิด ตัว U ลอยสูง"], "value_notes": "", "confidence": "sourced", "sources": ["https://defunkd.com/vintage-t-shirt-tag-dating-guide", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-3d-emblem", "category": "apparel.vintage", "kind": "tag", "brand": "3D Emblem", "title": "3D Emblem", "era": "ยุค 80 (Harley และอื่นๆ)", "keywords": ["3d emblem", "3-d emblem"], "cues": ["พบบนเสื้อ Harley-Davidson ยุค 80 บางตัว"], "red_flags": ["ป้ายปลอม: ไม่มีเอฟเฟกต์ 3D ฟอนต์หนา เลข 3 กับตัว D ไม่เข้ากัน ฟอนต์ \"Emblem\" ผิด"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.vintagerareusa.com/blogs/news/vintage-harley-davidson-3d-emblem-tee-shirt-label-history-since-1960s-vintage-rare-usa", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-liquid-blue", "category": "apparel.vintage", "kind": "tag", "brand": "Liquid Blue", "title": "Liquid Blue", "era": "", "keywords": ["liquid blue"], "cues": [], "red_flags": ["ป้ายปลอม: สีเพี้ยน มีเส้นขอบรอบลายวน/หยด เส้นด้ายหยาบ"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-tultex", "category": "apparel.vintage", "kind": "tag", "brand": "Tultex", "title": "Tultex", "era": "", "keywords": ["tultex"], "cues": [], "red_flags": ["ป้ายปลอม: ระยะตัวอักษรกว้างเกิน \"X-Large\" ไม่อยู่กลางแถบแดง"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.defunkd.com/fake-tag-archive/"]}, {"id": "tag-spring-ford", "category": "apparel.vintage", "kind": "tag", "brand": "Spring Ford", "title": "Spring Ford", "era": "", "keywords": ["spring ford"], "cues": [], "red_flags": ["ป้ายปลอม: ใช้ฟอนต์ตัวเขียน และไม่มีจุดหลัง U.S.A"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.defunkd.com/fake-tag-archive/"]}, {"id": "genre-band", "category": "apparel.vintage", "kind": "genre", "brand": "", "title": "เสื้อวงดนตรี (Band tee)", "era": "", "keywords": ["band", "tour", "เสื้อวง", "metallica", "nirvana", "rolling stones", "u2", "grateful dead", "guns n roses", "iron maiden", "concert"], "cues": ["3 ระดับ: เสื้อทัวร์ทางการ (ราคาสูงสุด) > bootleg ยุคเก่าที่ขายหน้าคอนเสิร์ต (ก็มีมูลค่า) > ของปลอม/พิมพ์ใหม่", "เสื้อทางการ: มีป้ายลิขสิทธิ์ บรรทัด © และป้ายตรงยุค", "Bootleg ยุคเก่า: ลายใหญ่ ไม่มีป้ายลิขสิทธิ์ แต่ตัวเสื้อและป้ายเปล่าเก่าจริง", "วงที่นักสะสมตามหามาก: Nirvana (In Utero), Metallica (Ride the Lightning) และวงกรันจ์/เมทัลยุค 90", "ดูวันทัวร์ด้านหลังเทียบกับยุคป้าย"], "red_flags": ["ลายเบลอแตกพิกเซล โลโก้ถูกตัด/บิด พิมพ์เบี้ยว", "ป้ายลิขสิทธิ์ไม่มีหรือดูไม่เป็นทางการ (สำหรับเสื้อที่อ้างว่าเป็นของทางการ)", "ราคาถูกผิดปกติ"], "value_notes": "หมวดราคาสูงสุดของเสื้อยืดวินเทจ จึงเป็นหมวดที่ถูกปลอมมากที่สุด", "confidence": "sourced", "sources": ["https://nostos.pages.dev/guides/vintage-band-tee-reprint-and-bootleg-identification-guide", "https://rockabilia.com/pages/official-vs-bootleg-band-merchandise"]}, {"id": "genre-harley", "category": "apparel.vintage", "kind": "genre", "brand": "", "title": "Harley-Davidson", "era": "", "keywords": ["harley", "harley-davidson", "harley davidson", "motor clothes", "sturgis", "laconia"], "cues": ["ยุค 60–70: มักไม่มีป้ายเฉพาะ ใช้เสื้อเปล่า Hanes/Screen Stars/Champion", "ยุค 80: ป้าย Harley สีดำโลโก้ bar & shield ส้มขาว บางตัวใช้ป้าย 3D Emblem", "ยุค 90: ป้ายทอเรียบร้อยขึ้น บางตัวเขียน Harley-Davidson Motor Clothes", "ด้านหลังมักพิมพ์ชื่อดีลเลอร์/เมือง (นิยมในยุค 80)", "Made in USA ยุค 80–90 มักเป็นตะเข็บเดี่ยว; ผลิตในสหรัฐฯ ส่วนใหญ่หยุดราว 2010"], "red_flags": ["ป้าย \"Harley Clothes\" ปลอม: ฟอนต์ HARLEY สูงผอมเกิน ระยะรอบ \"Clothes\" ผิด"], "value_notes": "ลายดีลเลอร์เฉพาะพื้นที่ยุค 80 และเสื้องานแรลลี่ (Sturgis, Laconia) นักสะสมนิยม", "confidence": "sourced", "sources": ["https://www.vintagerareusa.com/blogs/news/vintage-harley-davidson-3d-emblem-tee-shirt-label-history-since-1960s-vintage-rare-usa", "https://www.defunkd.com/fake-tag-archive/"]}, {"id": "genre-nike", "category": "apparel.vintage", "kind": "brand", "brand": "", "title": "Nike (ป้ายเสื้อผ้า)", "era": "", "keywords": ["nike", "swoosh"], "cues": ["Pinwheel 1978–1982", "ป้ายส้ม 1978–1983", "ป้ายน้ำเงิน 1984–1987", "ป้ายเทา ราว 1987–1994", "ป้ายดำ ราว 1994", "ป้ายขาว 1994–1999", "ป้ายแดงดำ 1997–1999", "ป้ายเงิน ต้น-กลางยุค 2000"], "red_flags": ["ป้ายบอกช่วงเวลา ไม่ใช่ปีเป๊ะ และช่วงทับซ้อนกันได้", "ผลิตนอกสหรัฐฯ ไม่ได้แปลว่าปลอมหรือใหม่เสมอไป"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.vintagerareusa.com/blogs/news/how-to-date-my-vintage-nike-with-the-tags-vintage-rare-usa"]}, {"id": "genre-champion", "category": "apparel.vintage", "kind": "brand", "brand": "", "title": "Champion Reverse Weave", "era": "", "keywords": ["champion", "reverse weave"], "cues": ["ยุค 50–60: ป้ายแรกที่มีคำว่า Reverse Weave", "ปลาย 60–70: ป้ายหลายสี (น้ำเงิน เหลือง แดง เขียว ดำ) Made in USA", "ยุค 80: Made in USA ผ้า 90% cotton/10% acrylic หรือ 89/8/3 (cotton/acrylic/rayon)", "ยุค 90: ส่วนใหญ่ USA บางส่วนเม็กซิโก", "ปลาย 90–2000: ย้ายไปเม็กซิโก/เอลซัลวาดอร์"], "red_flags": [], "value_notes": "สเวตเตอร์ Reverse Weave Made in USA เป็นที่ต้องการ", "confidence": "sourced", "sources": ["https://www.vintagerareusa.com/blogs/news/champion-reverse-weave-label-history-per-year"]}, {"id": "genre-souvenir", "category": "apparel.vintage", "kind": "genre", "brand": "", "title": "เสื้อท่องเที่ยว/ที่ระลึก", "era": "", "keywords": ["souvenir", "tourist", "city", "hard rock cafe", "dublin", "hawaii", "florida", "pubs"], "cues": ["ราคาขึ้นกับลาย (ลายแผนที่/ภาพประกอบสวยขายง่ายกว่า) ตะเข็บเดี่ยว และสภาพ"], "red_flags": ["Hard Rock Cafe ผลิตเยอะมาก ราคาส่วนใหญ่ไม่สูง"], "value_notes": "ราคาส่วนใหญ่ระดับกลาง-ล่าง เหมาะเป็นของหมุนเร็ว", "confidence": "general", "sources": []}, {"id": "genre-cartoon-movie", "category": "apparel.vintage", "kind": "genre", "brand": "", "title": "เสื้อการ์ตูน/คอมิก/หนัง", "era": "", "keywords": ["disney", "mickey", "looney", "simpsons", "marvel", "spider-man", "spiderman", "star wars", "pulp fiction", "matrix", "movie", "การ์ตูน", "หนัง"], "cues": ["ลิขสิทธิ์ทางการมีบรรทัด © ของเจ้าของลิขสิทธิ์", "Marvel ยุค 90 เป็นที่ต้องการ: เสื้อ Spider-Man/Daredevil/Silver Surfer ปี 1997 เคยขายออนไลน์ได้ 220,000 บาท", "เสื้อโปรโมตหนังยุคแรก (Star Wars, Pulp Fiction, The Matrix) หลายรุ่นไม่ได้ผลิตขายทั่วไป นักสะสมตามหา"], "red_flags": ["ลายการ์ตูนดังถูกพิมพ์ซ้ำเยอะ เช็คป้ายกับยุคของลายเสมอ"], "value_notes": "ตัวที่ราคาสูงคือลายหายากและของเก่าจริง ลายทั่วไปราคาระดับกลาง", "confidence": "sourced", "sources": ["https://www.benarnews.org/english/news/thai/secondhand-clothes-boom-deep-south-02142025113206.html", "https://esquire.co.th/2026/07/30/vintage-t-shirts-value-michael-b-jordan"]}, {"id": "genre-anime", "category": "apparel.vintage", "kind": "genre", "brand": "", "title": "เสื้ออนิเมะยุค 90 (Akira, Dragon Ball ฯลฯ)", "era": "", "keywords": ["akira", "dragon ball", "dbz", "ghost in the shell", "anime", "อนิเมะ", "manga"], "cues": ["Akira ถูกยกเป็นตัวท็อป ลายต้นฉบับปี 1988 มีรายงานราคาประมูลเกิน $3,000", "Dragon Ball Z ยุค 90 โดยเฉพาะลายพิมพ์รอบตัว (AOP), Ghost in the Shell", "ป้ายต้องเข้ากับยุคของลาย: ลาย Akira 1988 บนป้ายยุค 2010 = พิมพ์ใหม่", "ตะเข็บเดี่ยว, สกรีนซึมเนื้อผ้า, © พิมพ์ลงเนื้อผ้า ไม่ลอยบนผิว"], "red_flags": ["ซีดด้วยน้ำยาฟอกขาวเลียนแบบความเก่า", "ลายพิมพ์ดิจิทัล/รีดร้อนที่ผิวเป็นพลาสติก"], "value_notes": "ตัวเลขราคามาจากร้านขาย ยังไม่มีแหล่งอื่นยืนยัน ใช้เป็นแนวทางเท่านั้น", "confidence": "general", "sources": ["https://www.yiume.com/es/pages/faq-why-vintage-anime-shirts-expensive-2026"]}, {"id": "band-value", "category": "apparel.vintage", "kind": "genre", "brand": "", "title": "เสื้อวงที่ราคาสูง (ข้อมูลขายจริง)", "era": "", "keywords": ["nirvana", "grateful dead", "bjork", "björk", "soundgarden", "metallica", "red hot chili peppers", "rhcp", "guns n roses", "guns n' roses", "green day", "pearl jam", "earth wind", "oasis", "pushead"], "cues": ["ผลศึกษาราคาขายต่อ (ธ.ค. 2023–ก.ย. 2024): Grateful Dead \"Panther\" สูงสุด $2,750, Nirvana In Utero แขนยาว $2,000, Björk Post (1995), Soundgarden Louder Than Love (1989), Metallica Load (1996), Nirvana Sliver tour (1992)", "วงที่ราคาเฉลี่ยต่อตัวสูง: Nirvana, Red Hot Chili Peppers, Earth Wind & Fire, Guns N' Roses, Green Day, Paul McCartney, Pearl Jam", "ยุคที่ราคาดีที่สุด: ปลายยุค 80 ถึงกลางยุค 90 แนวร็อกราคาเฉลี่ยสูงกว่าป๊อปและแร็ป", "Grateful Dead ลาย Dancing Bears/Skeleton และ Metallica ลายของ Pushead เป็นที่ตามหา", "Oasis ยุค 90 ความต้องการเพิ่มขึ้นหลังประกาศรียูเนียนปี 2025"], "red_flags": ["ราคาประเมินกับราคาซื้อขายจริงต่างกันได้มาก (เช่น เสื้อ Nirvana staff ปี 1991 ที่มีข่าวประเมิน 1.35 ล้านบาท แต่เจ้าของซื้อมาหลักหมื่น)", "วงดังที่สุดคือวงที่มีของพิมพ์ใหม่มากที่สุด"], "value_notes": "เสื้อทัวร์ทางการ/ลายอัลบั้มเฉพาะ และเสื้อทีมงานที่ผลิตน้อย ราคาสูงสุด", "confidence": "sourced", "sources": ["https://loudwire.com/study-bands-most-valuable-vintage-t-shirts/", "https://esquire.co.th/2026/07/30/vintage-t-shirts-value-michael-b-jordan", "https://marketeeronline.co/archives/429691"]}, {"id": "market-thai-bale", "category": "apparel.vintage", "kind": "market", "brand": "", "title": "ตลาดเสื้อมือสองกระสอบในไทย", "era": "", "keywords": ["กระสอบ", "bale", "มือสอง", "โรงเกลือ", "ยะลา", "ปัตตานี"], "cues": ["เสื้อมือสองส่วนใหญ่มาจากสหรัฐฯ ส่งเรือไปมาเลเซียแล้วเข้าไทย", "ตัวอย่างจากภาคใต้: กระสอบละราว 1,000 บาท มีเสื้อยืด 200–220 ตัว หรือแจ็คเก็ต/กางเกง 150–180 ตัว", "ตลาดที่มีข่าว: ตลาดมะพร้าว (ยะลา), รูสะมิแล และยะหริ่ง (ปัตตานี)", "ของที่ขายได้ราคา: เสื้อยืดผลิตในสหรัฐฯ ผ้าบาง (นักสะสมญี่ปุ่นชอบ), เสื้อวงทั้งทางการและ bootleg, เสื้อทหารยุคสงคราม, ชุดทำงาน, ยีนส์, เสื้อกีฬา, เสื้อฮาวาย", "ตัวอย่าง: เสื้อยุค 70 ซื้อ 80 บาท ขายได้ 22,000 บาท"], "red_flags": [], "value_notes": "กำไรมาจากการรู้ว่าตัวไหนมีค่า ใช้โหมดสแกนรัวคัดกอง", "confidence": "sourced", "sources": ["https://www.benarnews.org/english/news/thai/secondhand-clothes-boom-deep-south-02142025113206.html"]}, {"id": "trend-now", "category": "apparel.vintage", "kind": "trend", "brand": "", "title": "กระแสตอนนี้ (อัปเดต พ.ย. 2026)", "era": "", "keywords": ["trend", "กระแส", "blokecore", "oasis", "world cup"], "cues": ["เสื้อกราฟิก/วินเทจกลับมาได้รับความสนใจในช่วง 2–3 ปีที่ผ่านมา เสื้อวงและเสื้อหนังนิยมสูง", "เสื้อบอลย้อนยุคมาแรงจากกระแส blokecore และฟุตบอลโลก 2026", "Oasis ยุค 90 ความต้องการเพิ่มหลังรียูเนียน", "เสื้ออนิเมะยุค 90 คนรุ่นใหม่สนใจ"], "red_flags": ["กระแสเปลี่ยนเร็ว ควรอัปเดตหัวข้อนี้ทุก 2–3 เดือน"], "value_notes": "", "confidence": "sourced", "sources": ["https://esquire.co.th/2026/07/30/vintage-t-shirts-value-michael-b-jordan", "https://www.outlookindia.com/sports/football/fifa-world-cup-2026-hottest-jerseys-blokecore-retro-shirts-fashion-trends", "https://marketeeronline.co/archives/429691"]}, {"id": "levis-tab", "category": "apparel.denim", "kind": "brand", "brand": "", "title": "Levi's: แท็บแดง (Big E / small e)", "era": "", "keywords": ["levi's", "levis", "levi", "big e", "red tab", "แท็บแดง", "บิ๊กอี"], "cues": ["Big E (LEVI'S ตัว E ใหญ่) = ก่อนปี 1971", "small e (Levi's ตัว e เล็ก) = ตั้งแต่ 1971", "แท็บพิมพ์ด้านเดียว = รุ่นเก่ามาก (ราวก่อนกลางยุค 50)", "ราว 10% ของการผลิตใช้แท็บเปล่า แท็บเปล่าจึงไม่ได้บอกยุค", "small e บางรุ่นก็หายากและมีราคา"], "red_flags": ["Big E กลับมาใช้อีกตั้งแต่ 2018 บนสินค้าพรีเมียม", "LVC (Levi's Vintage Clothing) และของปลอมอาจมีทั้ง Big E และป้ายวิธีซัก = ต้องดูป้ายวิธีซักและรายละเอียดอื่นประกอบ"], "value_notes": "Big E ราคาสูงกว่ามาก", "confidence": "sourced", "sources": ["https://www.thecollectorscompanion.co.uk/features/vintage-clothing/dating-levis/", "https://www.ropedye.com/2013/05/guide-how-to-date-levis-501-jeans/", "https://selvedgestory.pages.dev/en/guide/vintage-denim-authentication-guide/"]}, {"id": "levis-construction", "category": "apparel.denim", "kind": "rule", "brand": "", "title": "Levi's: หมุด ตะเข็บ ริม ป้ายหลัง", "era": "", "keywords": ["levi's", "levis", "501", "selvedge", "redline", "ริมแดง", "hidden rivet"], "cues": ["หมุดซ่อนในกระเป๋าหลัง 1937–1966 จากนั้นเปลี่ยนเป็นบาร์แทค", "ป้ายหนัง Two Horse จนถึงราว 1955 จากนั้นเป็นป้ายกระดาษ (Jacron)", "ผ้าริม (selvedge/ริมแดง) ด้านในตะเข็บข้างขา = ราวก่อนกลางยุค 80", "ตะเข็บด้านนอกขาแบบโพ้งสีส้มราว 1981, โพ้งสีขาวราว 1985", "ตะเข็บด้านบนกระเป๋าหลังแบบเดี่ยว (lock stitch) ราวก่อน 1976 จากนั้นเป็นแบบโซ่", "หลังเอวรัด (cinch back) เลิกราว 1947"], "red_flags": ["ซีดสม่ำเสมอผิดธรรมชาติหรือฟอกดูถูก = ระวัง", "ของ repro ญี่ปุ่นทำรายละเอียดได้เหมือนมาก ต้องดูหลายจุดประกอบ"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.thecollectorscompanion.co.uk/features/vintage-clothing/dating-levis/", "https://www.ropedye.com/2013/05/guide-how-to-date-levis-501-jeans/", "https://selvedgestory.pages.dev/en/guide/vintage-denim-authentication-guide/"]}, {"id": "levis-care", "category": "apparel.denim", "kind": "rule", "brand": "", "title": "Levi's: อ่านป้ายวิธีซักและรหัสวันผลิต", "era": "", "keywords": ["levi's", "levis", "care tag", "care label", "ป้ายวิธีซัก"], "cues": ["ไม่มีป้ายวิธีซักเลย = ก่อนราว 1971", "ราว 1968–1972: วิธีซักพิมพ์ในผ้ากระเป๋า", "1973–1983: ป้ายกระดาษเล็กข้างตะเข็บซ้าย มีวงกลมสีบอกรหัส", "ราว 1984 เป็นต้นไป: รหัส 3 หลัก เช่น 127 = ธันวาคม 1987", "1993 เป็นต้นไป: รหัส 4 หลัก เช่น 1295 = ธันวาคม 1995", "ป้ายรูป batwing ตั้งแต่ 1986/1987, คำว่า \"Care on Reverse\" = ก่อนราว 1992", "Made in USA สิ้นสุดราวปี 2003"], "red_flags": ["ป้ายบอกปีล่าสุดแต่ดีไซน์อ้างว่าเก่า = รุ่น repro/LVC"], "value_notes": "", "confidence": "sourced", "sources": ["https://levis-vintage-id.vercel.app/en/articles/article-care-label", "https://www.thecollectorscompanion.co.uk/features/vintage-clothing/dating-levis/"]}, {"id": "levis-jackets", "category": "apparel.denim", "kind": "brand", "brand": "", "title": "Levi's: แจ็คเก็ตยีนส์ Type I / II / III", "era": "", "keywords": ["jacket", "trucker", "506xx", "507xx", "557", "70505", "แจ็คเก็ต", "type i", "type ii", "type iii"], "cues": ["Type I (506XX): ก่อนยุค 40 กระเป๋าหน้าเดียวมีหมุดที่มุม หลังมีหัวเข็มขัดรัด (หายากสุด)", "Type II (507XX): ปลายยุค 40–60 กระเป๋าอกสองข้างมีฝาติดกระดุม ใช้บาร์แทคแทนหมุด", "Type III (557XX): 1962 ฝากระเป๋าแหลม (ทรง Trucker)", "ก่อน 1971: ตะเข็บแถวเดียวที่รังกระดุมล่าง; ตั้งแต่ 1971: ตะเข็บสองแถว + small e", "กลางยุค 80 ขึ้นไป: 4 กระเป๋า (อก 2 + ล้วงข้าง 2) นักสะสมสนใจน้อยกว่า"], "red_flags": [], "value_notes": "ยิ่งเก่า (Big E, 2 กระเป๋า) ยิ่งแพง", "confidence": "sourced", "sources": ["https://bragvintage.com/levis-denim-jacket-guide"]}, {"id": "lee", "category": "apparel.denim", "kind": "brand", "brand": "", "title": "Lee 101 / 101Z", "era": "", "keywords": ["lee", "101z", "101j", "storm rider", "lazy s"], "cues": ["ผ้า Left-Hand Twill (ลายทแยงกลับด้านกับ Levi's)", "ตะเข็บกระเป๋าหลังรูป Lazy S (ปรับดีไซน์ราว 1944–1946)", "101Z ซิปหน้าเริ่มราว 1926–1927", "ป้ายเปลี่ยนจากหนังเป็นกระดาษใส"], "red_flags": [], "value_notes": "", "confidence": "sourced", "sources": ["https://selvedgestory.pages.dev/en/guide/vintage-denim-authentication-guide/"]}, {"id": "wrangler", "category": "apparel.denim", "kind": "brand", "brand": "", "title": "Wrangler 13MWZ", "era": "", "keywords": ["wrangler", "13mwz", "blue bell", "11mwz"], "cues": ["13MWZ เปิดตัว 1947", "ผ้าทวิลธรรมดา 1947–1963, ผ้า Broken Twill ตั้งแต่ 1964", "หมุดซ่อน ตะเข็บรูป W นูนที่กระเป๋าหลัง ซิปหน้า"], "red_flags": [], "value_notes": "", "confidence": "sourced", "sources": ["https://selvedgestory.pages.dev/en/guide/vintage-denim-authentication-guide/"]}, {"id": "carhartt", "category": "apparel.denim", "kind": "brand", "brand": "", "title": "Carhartt", "era": "", "keywords": ["carhartt", "detroit jacket", "j01", "j97", "chore coat", "double knee"], "cues": ["รหัสวันที่ในป้ายวิธีซัก อ่านเป็นเดือน-ปี เช่น 0698 = มิถุนายน 1998, ต้นยุค 90 อาจไม่มีศูนย์นำหน้า เช่น 591 = พฤษภาคม 1991", "ป้าย Union + Made in USA = ยุคก่อนย้ายฐานผลิต", "J01 Detroit: ผ้าดั๊กแข็ง 12oz ไซซ์เป็นตัวเลข (38–44) ปกลูกฟูก", "J97 Detroit: ปลายยุค 90 ไซซ์ตัวอักษร ผ้านุ่มกว่า"], "red_flags": ["ซิปไม่มียี่ห้อเบาๆ (ของเก่ามักเป็น YKK หนัก หรือ Talon ทองเหลือง)", "ปักโลโก้ใหญ่หรือเบี้ยว", "ซับในฟลีซเทาสังเคราะห์ (ของเก่ามักเป็นซับผ้าห่มลายสก็อต)", "ทำเก่าด้วยเคมี"], "value_notes": "Detroit Jacket และ Made in USA เป็นที่ต้องการ", "confidence": "sourced", "sources": ["https://nostos.pages.dev/guides/identifying-vintage-carhartt-and-workwear"]}, {"id": "denim-general", "category": "apparel.denim", "kind": "rule", "brand": "", "title": "ยีนส์วินเทจ: ดูผ้าและการซีด", "era": "", "keywords": ["denim", "jeans", "ยีนส์", "rope dye"], "cues": ["ยีนส์เก่าส่วนใหญ่ย้อมแบบ rope dye ซีดเป็นเส้นแนวตั้ง มีรอยรังผึ้งหลังเข่าและหนวดแมว", "ผ้ายีนส์วินเทจมักหนาราว 13–15oz"], "red_flags": ["ซีดสม่ำเสมอผิดธรรมชาติ", "อย่าเชื่อป้าย \"Made in [ปี]\" หรือคำบรรยายของผู้ขายโดยไม่ตรวจเอง", "อย่าใช้ Big E อย่างเดียวตัดสิน"], "value_notes": "", "confidence": "sourced", "sources": ["https://selvedgestory.pages.dev/en/guide/vintage-denim-authentication-guide/"]}, {"id": "fb-rule-check", "category": "apparel.football", "kind": "rule", "brand": "", "title": "เสื้อบอล: เช็คของแท้พื้นฐาน", "era": "", "keywords": ["football", "soccer", "jersey", "kit", "เสื้อบอล", "เสื้อฟุตบอล", "product code"], "cues": ["หารหัสสินค้าบนป้ายด้านใน แล้วค้นใน Google ต้องขึ้นเสื้อตัวเดียวกันเป๊ะ (ทีม ปี เหย้า/เยือน)", "ผู้ขายไม่ยอมโชว์ป้าย = สัญญาณเตือน, ป้ายถูกตัดออก = ซื้อเสี่ยงเอง", "เทียบสี ความคมของลาย และตำแหน่งดีไซน์กับรูปจากร้านทางการ"], "red_flags": ["ป้ายเสื้อเก่ามีรอยปากกา/ดินสอเขียน", "เสื้อออกใหม่ลด 50% หรือของหายากราคาถูกผิดปกติ", "เสื้อก่อนปี 2000 มีครบทุกไซซ์ XS–XXL", "ประกาศใช้คำว่า \"replica\" หรือ \"retro\" (อาจเป็นงานทำใหม่หรือของปลอม)"], "value_notes": "", "confidence": "sourced", "sources": ["https://footballshirtcollective.com/blogs/collectors-club/spot-a-fake-shirt"]}, {"id": "fb-thai-grade", "category": "apparel.football", "kind": "rule", "brand": "", "title": "คำว่า \"เกรดเอ / เกรดแฟนบอล / เกรดนักเตะ\" ในไทย", "era": "", "keywords": ["เกรดเอ", "เกรด a", "aaa", "เกรดไทย", "งานไทย", "เกรดนักเตะ", "เกรดแฟนบอล"], "cues": ["ในไทยมีร้านขายเสื้อบอลที่ระบุว่า \"เกรดเอ/เกรดแฟนบอล/เกรดนักเตะ/เกรดพรีเมียม\" แยกจากของลิขสิทธิ์", "ของลิขสิทธิ์จริงก็มีรุ่นนักเตะ (Player/Authentic) กับรุ่นแฟน (Replica) แต่ต้องเช็ครหัสสินค้าได้"], "red_flags": ["ผู้ขายเรียกว่า \"เกรด...\" แทนการบอกว่าลิขสิทธิ์แท้ = ให้ถือว่าไม่ใช่ของลิขสิทธิ์ อย่าซื้อในราคาของแท้ และอย่าขายต่อว่าเป็นของแท้"], "value_notes": "", "confidence": "general", "sources": ["https://www.welovefootballshop.com/product/tag/%E0%B9%80%E0%B8%AA%E0%B8%B7%E0%B9%89%E0%B8%AD%E0%B8%9F%E0%B8%B8%E0%B8%95%E0%B8%9A%E0%B8%AD%E0%B8%A5%E0%B8%AB%E0%B8%A5%E0%B8%B1%E0%B8%87%E0%B8%AA%E0%B8%99%E0%B8%B2%E0%B8%A1%E0%B8%A8%E0%B8%B8%E0%B8%A0?tskp=13"]}, {"id": "fb-player-fan", "category": "apparel.football", "kind": "rule", "brand": "", "title": "รุ่นนักเตะ (Player/Authentic) vs รุ่นแฟน (Replica)", "era": "", "keywords": ["player issue", "player version", "authentic", "replica", "fan version", "vaporknit", "dri-fit adv", "heat.rdy", "aeroready", "รุ่นนักเตะ", "รุ่นแฟน"], "cues": ["รุ่นนักเตะ: ทรงเข้ารูป ผ้าบางเบาระบายอากาศ โลโก้/ตราแบบรีดร้อน ใช้ Nike Dri-FIT ADV หรือ adidas HEAT.RDY", "รุ่นแฟน: ทรงปกติ ผ้าหนากว่า โลโก้/ตราแบบปัก ใช้ Nike Dri-FIT หรือ adidas AEROREADY", "ทั้งสองรุ่นเป็นของลิขสิทธิ์ คำว่า \"authentic\" หมายถึงรุ่นนักเตะ", "ราคาป้ายยุโรป: รุ่นนักเตะราว €140–160, รุ่นแฟนราว €90–110", "เสื้อยุคเก่า รุ่นนักเตะกับรุ่นแฟนแยกกันชัดเจนแค่ราว 10 ปีหลัง"], "red_flags": [], "value_notes": "", "confidence": "sourced", "sources": ["https://first11shirts.com/blogs/informative/player-vs-fan-version-football-shirts-what-s-the-difference", "https://themomentum.co/feature-football-jersey/"]}, {"id": "fb-nike", "category": "apparel.football", "kind": "brand", "brand": "", "title": "Nike: เช็คเสื้อบอล", "era": "", "keywords": ["nike", "swoosh"], "cues": ["รหัสสินค้า: ป้ายเล็กด้านในใกล้ชายเสื้อ รูปแบบ ตัวเลข 6 หลัก-3 หลัก (เช่น 123456-789) ค้นแล้วต้องขึ้นเสื้อตัวนั้นเป๊ะ", "Jock tag (ป้ายด้านหน้ามุมล่าง) มีรหัสยาวที่ไม่ซ้ำกันในแต่ละตัว", "เสื้อรุ่นใหม่มีป้ายที่ปลายแขน", "ขอบ swoosh คม"], "red_flags": ["รหัสสินค้าขึ้นเป็นเสื้ออีกตัว (เช่น ชุดเหย้าแทนชุดเยือน)", "ไม่มีป้ายรหัสสินค้า", "รหัส jock tag ซ้ำกับเสื้อหลายตัว", "ปลาย swoosh ลากยาว งานปักเละ", "ด้านในหลัง swoosh/ตรามีวัสดุรองเกินมาก (สัญญาณคลาสสิก)", "ป้ายคอบนเสื้อรุ่นใหม่ (ไม่ได้ปลอมเสมอ แต่ต้องเช็คเพิ่ม)", "France 2016 ชุดเยือน เป็นรหัสที่ของปลอมใช้บ่อย"], "value_notes": "", "confidence": "sourced", "sources": ["https://footballshirtcollective.com/blogs/collectors-club/spot-fake-nike"]}, {"id": "fb-adidas", "category": "apparel.football", "kind": "brand", "brand": "", "title": "adidas: เช็คเสื้อบอล", "era": "", "keywords": ["adidas", "three stripes", "trefoil"], "cues": ["รหัสสินค้าที่ป้ายคอด้านใน: ตัวอักษร 2 ตัว + ตัวเลข 4 ตัว (เช่น DP2644) ค้นแล้วต้องตรงเสื้อ", "ป้ายคอของแท้มีตัวย่อชื่อสโมสร/ประเทศ", "โลโก้: ตัวหนังสือแตะขอบล่างของแถบ ระยะตัวอักษรสม่ำเสมอ แถบตรง", "jock tag มักอยู่มุมล่างด้านหน้า ไม่มีก็ไม่ได้แปลว่าปลอม (รุ่นแฟนบางรุ่นไม่มี)"], "red_flags": ["ป้ายคอเขียนกว้างๆ ว่า \"ADIDAS JSY\"", "ป้ายคอติดกลับหัว", "ด้ายลากระหว่างตัวอักษร ฟอนต์บางเกิน แถบเบี้ยว ผ้าย่นรอบโลโก้", "ของหายากราคาถูก หรือมีครบทุกไซซ์"], "value_notes": "", "confidence": "sourced", "sources": ["https://footballshirtcollective.com/blogs/collectors-club/spot-fake-adidas"]}, {"id": "fb-umbro", "category": "apparel.football", "kind": "brand", "brand": "", "title": "Umbro ยุค 90", "era": "", "keywords": ["umbro"], "cues": ["ป้ายคอสีน้ำเงิน ตัวอักษร UMBRO มีจุดชัด", "บางตัวมีป้ายขาวบอกไซซ์/วิธีซักใต้ป้ายน้ำเงิน (ต้นยุค 90 มักไม่มี ปลายยุค 90 เกือบทุกตัวมี)", "ป้ายคอสีขาวตัวอักษรน้ำเงิน พบบ่อยในเสื้อ Celtic", "ช่วง 1998–2000 เปลี่ยนแบบป้าย อาจเจอทั้งสองแบบในเสื้อลายเดียวกัน"], "red_flags": ["ไม่มีจุดในตัวอักษร UMBRO", "ป้ายแบนเรียบ เย็บน้อยกว่า (แต่ป้ายยุค 90 เย็บไม่สวยก็เป็นของแท้ได้)"], "value_notes": "", "confidence": "sourced", "sources": ["https://casualfootballshirts.co.uk/pages/1990s-umbro-shirts-authenticity-checks"]}, {"id": "fb-kappa", "category": "apparel.football", "kind": "brand", "brand": "", "title": "Kappa", "era": "", "keywords": ["kappa", "omini", "kombat"], "cues": ["รุ่นใหม่: ป้ายด้านในมีหมายเลข/QR ตรวจที่ BasicLabels.net", "ยุค 90: ป้ายหลักด้านในมีจุด 6 จุดเรียงสองแนวทแยง สม่ำเสมอ", "ของแท้มักมีป้ายด้านในมากกว่าของปลอม", "Barcelona 1992–95 ชุดเหย้า: ด้านหน้าไม่มีโลโก้ Kappa ดูป้าย \"Barça F.C.B.\" และ \"Sports Kappa S.A.\" ด้านใน"], "red_flags": ["หมายเลขตรวจไม่เจอหรือขึ้นเสื้อตัวอื่น", "จุดบนป้ายกระจายไม่เท่ากัน", "ตัวอักษร Kappa ป่อง", "รูปคนสองคนใน Omini ผิดทรง", "ป้าย KOMBAT แบบตัวอักษรเจาะทะลุ"], "value_notes": "เสื้อ Kappa ยุค 90 ถูกปลอมเยอะมาก", "confidence": "sourced", "sources": ["https://footballshirtcollective.com/blogs/collectors-club/spot-fake-kappa"]}, {"id": "fb-demand-thai", "category": "apparel.football", "kind": "genre", "brand": "", "title": "เสื้อบอลวินเทจที่คนไทยตามหา", "era": "", "keywords": ["manchester united", "man utd", "แมนยู", "everton", "ac milan", "milan", "man city", "แมนซิตี้", "real madrid", "southampton", "liverpool", "ลิเวอร์พูล", "sharp", "batistuta", "shevchenko", "totti", "gerrard", "beckham", "england 1990"], "cues": ["นักเตะยุค 90–2000 ที่นิยม: Batistuta, Shevchenko, Totti, Gerrard, Le Tissier", "Everton และแมนยูยุคสปอนเซอร์ Sharp", "AC Milan ชุดเหย้าครบรอบ 100 ปี, แมนซิตี้ชุดเยือน 1993–94 (แฟน Oasis ตาม), เรอัลมาดริดยุค Beckham, อังกฤษฟุตบอลโลก 1990", "หายาก: Southampton 1991–93, แมนยูชุดเยือน 1970", "ราคาที่บทความระบุ: ส่วนใหญ่หลักร้อยถึงหลักพัน, AC Milan 100 ปี 8,000–10,000 บาท, แมนซิตี้เยือน 93–94 ตั้งแต่ 15,000 บาท, แมนยูเยือน 1970 หลักหมื่นขึ้นไป", "ร้านเฉพาะทาง: TJ Football Shop จตุจักร (อาคารตึกแดง)"], "red_flags": ["ความร้อนทำให้เบอร์/ชื่อที่พิมพ์ละลาย เก็บในถุง ไม่ตากแดด", "การติดอาร์มแขนไม่ดีทำให้เสื้อเสียหาย"], "value_notes": "ยุค 70–80 หายากที่สุด ทีม/ฤดูกาลที่ผูกกับนักเตะหรือเหตุการณ์ดังราคาดี ราคาในบทความอาจเปลี่ยนแล้ว", "confidence": "sourced", "sources": ["https://themomentum.co/feature-football-jersey/"]}, {"id": "fb-demand-global", "category": "apparel.football", "kind": "trend", "brand": "", "title": "เสื้อบอลย้อนยุคที่ฮิต (กระแส blokecore + ฟุตบอลโลก 2026)", "era": "", "keywords": ["germany", "nigeria", "brazil", "argentina", "england", "mexico", "france", "croatia", "japan", "canada", "norway", "world cup", "blokecore", "ทีมชาติ"], "cues": ["ย้อนยุคที่ฮิต: เยอรมนี Italia 90, ไนจีเรีย 1994, บราซิล 2002, อาร์เจนตินา 1986, อังกฤษ Euro 96, เม็กซิโก 1998, ฝรั่งเศส 1998, โครเอเชีย 1998", "ชุดฟุตบอลโลก 2026 ที่ถูกพูดถึง: เยอรมนีเหย้า, เม็กซิโกเหย้า, ญี่ปุ่นเยือน, แคนาดาเยือนสีดำ, นอร์เวย์, อาร์เจนตินา", "กระแส blokecore ใส่เสื้อบอลคู่กับยีนส์ทรงหลวม"], "red_flags": ["ชุดที่ฮิตคือชุดที่ถูกทำซ้ำ (retro remake) และปลอมมากที่สุด เช็ครหัสสินค้าเสมอ"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.outlookindia.com/sports/football/fifa-world-cup-2026-hottest-jerseys-blokecore-retro-shirts-fashion-trends"]}, {"id": "fb-thailand", "category": "apparel.football", "kind": "genre", "brand": "", "title": "เสื้อทีมชาติไทย", "era": "", "keywords": ["thailand", "ทีมชาติไทย", "ช้างศึก", "ชบาแก้ว", "grand sport", "แกรนด์สปอร์ต", "warrix", "วอริกซ์"], "cues": ["ผู้ผลิตที่ผ่านมา: Grand Sport และปัจจุบัน Warrix มีทั้งเกรดนักเตะและเกรดแฟน", "ที่นักสะสมสนใจ: Grand Sport ลาย \"ศักดิ์ศรีปฐพีไทย\" และเสื้อครบรอบ 100 ปี (2016–17) ที่บทความบอกว่าหายากแล้ว, รุ่น Limited Edition", "ราคาป้าย Warrix ฤดูกาล 2023/24: Player 2,490 บาท, Replica 890 บาท, เสื้อเชียร์ 399 บาท"], "red_flags": ["เสื้อเชียร์ราคาถูกไม่ใช่เสื้อแข่ง อย่าตีราคาเท่ารุ่น Player"], "value_notes": "", "confidence": "sourced", "sources": ["https://www.ktc.co.th/article/lifestyle/sport/thailand-national-team-kits", "https://www.bangkokbiznews.com/lifestyle/1085512", "https://www.classicfootballshirts.co.uk/2016-17-thailand-100th-anniversary-shirt-xl-this16365185.html"]}]/*KB_END*/;

function kbPrompt() {
  if (!KB.length) return '';
  return KB.map(e => `[${e.id}] ${e.title}${e.era ? ' (' + e.era + ')' : ''}: ${e.cues.join(' / ')}${e.red_flags.length ? ' | ระวัง: ' + e.red_flags.join(' / ') : ''}${e.confidence === 'general' ? ' (ความรู้ทั่วไป ยังไม่ยืนยัน)' : ''}`).join('\n');
}
function kbMatch(item, auth, usedIds) {
  if (!KB.length) return [];
  const text = [item.name_th, item.brand, item.model, item.era, item.notes, ...(auth.checks || []).map(c => c.note || ''), ...(auth.red_flags || [])]
    .join(' ').toLowerCase();
  const used = new Set(usedIds || []);
  const scored = KB.map(e => {
    let sc = used.has(e.id) ? 5 : 0;
    for (const k of e.keywords) if (k && text.includes(k)) sc += k.length > 3 ? 2 : 1;
    if (sc && e.category === item.category) sc += 1;
    return { e, sc };
  }).filter(x => x.sc > 0).sort((a, b) => b.sc - a.sc).slice(0, 6);
  return scored.map(({ e }) => ({ id: e.id, title: e.title, era: e.era, cues: e.cues.slice(0, 4), red_flags: e.red_flags.slice(0, 3), value_notes: e.value_notes, confidence: e.confidence, source: e.sources[0] || '' }));
}

const json = (obj, status = 200, cors = {}) =>
  new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json; charset=utf-8', ...cors } });
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);

export default {
  async fetch(req, env) {
    const cors = {
      'access-control-allow-origin': '*',
      'access-control-allow-methods': 'POST, GET, OPTIONS',
      'access-control-allow-headers': 'content-type, x-app-key'
    };
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors });
    const url = new URL(req.url);
    const path = url.pathname;

    if (path === '/' || path === '/api/health') {
      return json({ ok: true, gemini: !!env.GEMINI_API_KEY, serper: !!env.SERPER_API_KEY, kv: !!env.CACHE, locked: !!env.APP_KEY, model: env.GEMINI_MODEL || 'gemini-2.5-flash' }, 200, cors);
    }
    // รูปอ้างอิงเปิดดูได้โดยใส่ key ใน query (เพราะ <img> ส่ง header ไม่ได้)
    const key = req.headers.get('x-app-key') || url.searchParams.get('k');
    if (env.APP_KEY && key !== env.APP_KEY) return json({ error: 'รหัสแอปไม่ถูกต้อง' }, 401, cors);

    try {
      if (path === '/api/kb' && req.method === 'GET') return json({ entries: KB }, 200, cors);
      if (path === '/api/scan' && req.method === 'POST') return json(await scan(env, await req.json()), 200, cors);
      if (path === '/api/refs' && req.method === 'GET') return json(await listRefs(env, url.searchParams.get('category')), 200, cors);
      if (path === '/api/refs' && req.method === 'POST') return json(await addRef(env, await req.json()), 200, cors);
      if (path === '/api/refs/img' && req.method === 'GET') {
        needKV(env);
        const d = await env.CACHE.get(url.searchParams.get('key') || '', 'json');
        if (!d) return json({ error: 'not_found' }, 404, cors);
        const m = /^data:(.+?);base64,(.*)$/.exec(d.image);
        const bin = Uint8Array.from(atob(m[2]), c => c.charCodeAt(0));
        return new Response(bin, { headers: { 'content-type': m[1], 'cache-control': 'public, max-age=86400', ...cors } });
      }
      if (path === '/api/mistakes' && req.method === 'POST') return json(await addMistake(env, await req.json()), 200, cors);
      if (path === '/api/mistakes' && req.method === 'GET') return json({ items: await getMistakes(env, url.searchParams.get('category')) }, 200, cors);
      return json({ error: 'not_found' }, 404, cors);
    } catch (e) {
      return json({ error: String(e.message || e) }, e.status || 500, cors);
    }
  }
};

function needKV(env) {
  if (!env.CACHE) { const e = new Error('ยังไม่ได้ผูก KV ชื่อ CACHE ใน Worker (ดูคู่มือข้อ 2.5)'); e.status = 400; throw e; }
}

// =============================================================
//  SCAN
// =============================================================
async function scan(env, body) {
  if (!env.GEMINI_API_KEY) throw new Error('ยังไม่ได้ตั้ง GEMINI_API_KEY ใน Worker');
  const images = (body.images || []).slice(0, 6);
  if (!images.length) { const e = new Error('ไม่มีรูป'); e.status = 400; throw e; }
  const labels = body.labels || [];
  const hint = body.hint || {};

  // known fake patterns (จากที่ผู้ใช้เคยบันทึกว่าพลาด)
  const mistakes = env.CACHE ? await getMistakes(env, null).catch(() => []) : [];

  // 1) ระบุ + เช็คของแท้ + ตำหนิ + คุณภาพรูป
  const item = await identify(env, images, labels, hint, mistakes);
  const cat = CAT_KEYS.includes(item.category) ? item.category : 'generic';
  item.category = cat;
  const catInfo = CATEGORIES[cat] || CATEGORIES.generic;
  let auth = normalizeAuth(item.auth);
  const notes = [];

  // 2) เทียบกับคลังรูปของแท้ (ถ้ามีในหมวดนี้)
  let refsUsed = 0;
  if (env.CACHE) {
    const refs = await loadRefImages(env, cat, 6).catch(() => []);
    if (refs.length) {
      const cmp = await compareWithRefs(env, images, labels, refs, catInfo).catch(e => ({ error: e.message }));
      if (cmp && !cmp.error && cmp.level) {
        refsUsed = refs.length;
        auth.ref_compare = { level: cmp.level, summary: cmp.summary, differences: cmp.differences || [] };
        auth.level = worst(auth.level, cmp.level);
        if ((cmp.differences || []).length) auth.red_flags = [...auth.red_flags, ...cmp.differences.map(d => 'ต่างจากของแท้: ' + d)];
      }
    }
  }

  // 3) ตรวจสองรอบสำหรับของราคาสูง
  const est = item.est_price_thb?.mid || 0;
  const threshold = +(env.DOUBLE_CHECK_ABOVE || 3000);
  if (est >= threshold) {
    try {
      const second = await identify(env, images, labels, hint, mistakes);
      const a2 = normalizeAuth(second.auth);
      auth.double_checked = true;
      if (second.category !== item.category || a2.level !== auth.level) {
        notes.push('AI ตรวจสองรอบได้ผลไม่ตรงกัน → ปรับเป็นต้องเช็คเพิ่ม');
        auth.level = worst(auth.level, a2.level === 'pass' ? 'suspicious' : a2.level);
        if (auth.level === 'pass') auth.level = 'suspicious';
        auth.disagree = true;
      }
    } catch (e) { notes.push('ตรวจรอบสองไม่สำเร็จ: ' + e.message); }
  }

  // 4) กฎหมวดเสี่ยงสูง: แบรนด์เนม/มือถือ ไม่ให้ผ่านจากรูปอย่างเดียว
  if ((cat === 'luxury' || cat === 'phone') && auth.level === 'pass') {
    auth.level = 'suspicious';
    notes.push(cat === 'luxury' ? 'แบรนด์เนมต้องผ่านผู้เชี่ยวชาญเท่านั้น' : 'มือถือต้องเช็ค IMEI/สถานะล็อกก่อนซื้อ');
  }

  // 5) ราคาตลาด
  let market = { evidence: [], links: [], note: '' };
  if (env.SERPER_API_KEY) {
    const cacheKey = 'px:' + (item.search_query_en || item.name_th || '').toLowerCase().trim();
    let cached = null;
    if (env.CACHE) { try { cached = await env.CACHE.get(cacheKey, 'json'); } catch (e) {} }
    if (cached) market = { ...cached, cached: true };
    else {
      market = await marketPrices(env, item);
      if (env.CACHE && market.evidence.length) { try { await env.CACHE.put(cacheKey, JSON.stringify(market), { expirationTtl: 7 * 86400 }); } catch (e) {} }
    }
  } else market.note = 'ยังไม่ได้ตั้ง SERPER_API_KEY ใช้ราคาประเมินจาก AI อย่างเดียว';

  return {
    item: {
      name: item.name_th, brand: item.brand, model: item.model, category: cat, category_th: catInfo.th,
      era: item.era, condition: item.condition, size: item.size || '', id_confidence: item.id_confidence, notes: item.notes
    },
    auth: { ...auth, refs_used: refsUsed, notes },
    defects: Array.isArray(item.defects) ? item.defects : [],
    photo_quality: Array.isArray(item.photo_quality) ? item.photo_quality : [],
    need_photos: item.need_photos && item.need_photos.length ? item.need_photos : catInfo.photos,
    checkpoints: catInfo.photos,
    lesson: item.lesson || '',
    kb_matches: kbMatch(item, auth, item.kb_used),
    ai_estimate: item.est_price_thb || null,
    market
  };
}

const RANK = { pass: 0, suspicious: 1, high_risk: 2 };
const worst = (a, b) => (RANK[b] > RANK[a] ? b : a);

// ---------------- Gemini helpers ----------------
async function gemini(env, parts, what) {
  const model = env.GEMINI_MODEL || 'gemini-2.5-flash';
  const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-goog-api-key': env.GEMINI_API_KEY },
    body: JSON.stringify({ contents: [{ parts }], generationConfig: { responseMimeType: 'application/json', temperature: 0.2 } })
  });
  const d = await r.json();
  if (d.error) {
    if (d.error.code === 404) throw new Error(`ไม่พบโมเดล ${model} — ตั้ง GEMINI_MODEL เป็นรุ่นที่มีใน Google AI Studio`);
    if (d.error.code === 429) throw new Error('โควตา Gemini ฟรีของวันนี้หมดแล้ว ลองใหม่ภายหลัง');
    throw new Error('Gemini: ' + d.error.message);
  }
  const text = (d.candidates?.[0]?.content?.parts || []).map(p => p.text || '').join('');
  try { return JSON.parse(text.replace(/```json|```/g, '').trim()); }
  catch (e) { throw new Error('AI ตอบกลับไม่ใช่ JSON (' + what + ')'); }
}
function imgPart(dataUrl) {
  const m = /^data:(.+?);base64,(.*)$/.exec(dataUrl);
  return { inlineData: { mimeType: m ? m[1] : 'image/jpeg', data: m ? m[2] : dataUrl } };
}
function labeledImages(images, labels) {
  const parts = [];
  images.forEach((img, i) => {
    parts.push({ text: `รูปที่ ${i + 1}${labels[i] ? ' — ' + labels[i] : ''}:` });
    parts.push(imgPart(img));
  });
  return parts;
}

async function identify(env, images, labels, hint, mistakes) {
  const checklistText = Object.entries(CATEGORIES)
    .map(([k, v]) => `หมวด ${k} (${v.th}):\n` + v.checks.map((c, i) => `  ${i + 1}. ${c}`).join('\n') + `\n  ตำหนิที่ต้องหา: ${v.defects}`)
    .join('\n');
  const hand = (hint.hand || []).filter(h => h.ok !== null && h.ok !== undefined)
    .map(h => `- ${h.q}: ${h.ok ? 'ผ่าน' : 'ไม่ผ่าน'}`).join('\n');
  const mistakeText = (mistakes || []).slice(0, 25).map(m => `- [${m.category}] ${m.name}: ${m.what}`).join('\n');

  const prompt = `คุณคือผู้เชี่ยวชาญประเมินสินค้ามือสองในประเทศไทย รูปทั้งหมดเป็นสินค้าชิ้นเดียวกันถ่ายหลายมุม ตอบเป็น JSON เท่านั้น
${hint.name ? 'ผู้ใช้บอกว่าเป็น: ' + hint.name : ''}
${hand ? 'ผลที่ผู้ใช้เช็คด้วยมือแล้ว:\n' + hand : ''}
${mistakeText ? 'บทเรียนจากของปลอม/ดีลพลาดที่เคยเจอ (ระวังเป็นพิเศษ):\n' + mistakeText : ''}

หมวดที่เลือกได้: ${CAT_KEYS.join(', ')}  (กระเป๋า/นาฬิกาแบรนด์เนมใช้ luxury, เสื้อยืดใช้ apparel.vintage, เสื้อฟุตบอล/เสื้อกีฬาทีมใช้ apparel.football, ยีนส์/แจ็คเก็ต/เสื้อผ้าอื่นใช้ apparel.denim)
${KB.length ? 'ฐานความรู้ของระบบ (เชื่อถือมากกว่าความจำของคุณ ถ้าขัดกันให้ยึดฐานความรู้ และใส่ id ที่ใช้ใน kb_used):\n' + kbPrompt() : ''}

เช็คลิสต์ของแท้ตามหมวด:
${checklistText}

กฎสำคัญ:
- ห้ามบอกว่าแท้ 100% ประเมินเฉพาะจากสิ่งที่เห็นในรูป
- ใช้เช็คลิสต์ของหมวดที่ระบุได้ครบทุกข้อ จุดที่ไม่มีรูปให้ดู status = "not_photographed", เห็นแต่ไม่ชัด = "unclear"
- level: "pass" เมื่อทุกจุดที่เห็นสอดคล้องกันและขาดรูปไม่เกิน 1 จุด, "high_risk" เมื่อมีจุด fail หรือสัญญาณปลอมชัดเจน, นอกนั้น "suspicious"
- defects: ตำหนิที่เห็นในรูป พร้อมผลต่อราคาเป็น % (เช่น รูเล็ก 10, คราบใหญ่ 25)
- photo_quality: ประเมินทุกรูป ok=false ถ้าเบลอ มืด ไกลเกินไป หรือมองไม่เห็นจุดที่ต้องเช็ค
- size: ไซซ์บนป้ายหรือที่เห็น (เสื้อผ้า/รองเท้า) ไม่รู้ให้เว้นว่าง
- lesson: ความรู้ 1 ประโยคภาษาไทยที่สอนมือใหม่จากของชิ้นนี้ (เช่น "ป้าย Fruit of the Loom แบบนี้พบในยุค 80-90")
- est_price_thb: ราคามือสองที่ขายกันจริงในไทยโดยประมาณ (บาท) หลังคิดตำหนิแล้ว
- search_query_en ใช้ค้นราคาใน eBay ให้เจาะจง

รูปแบบ JSON:
{"name_th":string,"brand":string,"model":string,"category":string,"era":string,"size":string,"condition":"new|like_new|good|fair|poor",
"id_confidence":0-100,"notes":string,"search_query_en":string,"search_query_th":string,
"auth":{"level":"pass|suspicious|high_risk","summary":string,"checks":[{"point":string,"status":"pass|fail|unclear|not_photographed","note":string}],"red_flags":[string]},
"defects":[{"what":string,"severity":"minor|major","price_impact_pct":number}],
"photo_quality":[{"index":number (เริ่มที่ 1),"ok":boolean,"problem":string}],
"need_photos":[string],"lesson":string,"kb_used":[string (id ในฐานความรู้ที่ใช้ตัดสิน)],
"est_price_thb":{"low":number,"mid":number,"high":number}}`;
  return gemini(env, [{ text: prompt }, ...labeledImages(images, labels)], 'identify');
}

async function compareWithRefs(env, images, labels, refs, catInfo) {
  const parts = [{ text: `เทียบสินค้าที่ผู้ใช้ถ่าย กับ "รูปอ้างอิงของแท้" ในหมวด ${catInfo.th}
ดูเฉพาะจุดที่เทียบกันได้ (ป้าย ฟอนต์ ตะเข็บ ขั้วต่อ ฯลฯ) ห้ามเดา ถ้าไม่มีจุดที่เทียบได้ให้ level = "suspicious"
ตอบ JSON: {"level":"pass|suspicious|high_risk","summary":string (ไทย 1 ประโยค),"differences":[string (จุดที่ต่างจากของแท้ ภาษาไทย)]}` }];
  parts.push({ text: '--- รูปอ้างอิงของแท้ ---' });
  refs.forEach(r => { parts.push({ text: `ของแท้: ${r.checkpoint}${r.note ? ' (' + r.note + ')' : ''}` }); parts.push(imgPart(r.image)); });
  parts.push({ text: '--- รูปสินค้าที่ต้องตรวจ ---' });
  parts.push(...labeledImages(images, labels));
  return gemini(env, parts, 'compare');
}

function normalizeAuth(a) {
  a = a || {};
  const checks = Array.isArray(a.checks) ? a.checks : [];
  const seen = checks.filter(c => c.status !== 'not_photographed').length;
  const missing = checks.length - seen;
  const fails = checks.filter(c => c.status === 'fail').length;
  let level = ['pass', 'suspicious', 'high_risk'].includes(a.level) ? a.level : 'suspicious';
  if (fails > 0) level = 'high_risk';
  else if (level === 'pass' && missing > 1) level = 'suspicious';
  return { level, summary: a.summary || '', checks, red_flags: a.red_flags || [], seen, total: checks.length };
}

// =============================================================
//  REFERENCE LIBRARY (รูปของแท้) + MISTAKES
// =============================================================
async function addRef(env, b) {
  needKV(env);
  if (!b.image || !b.category) { const e = new Error('ต้องมี category และ image'); e.status = 400; throw e; }
  const key = `ref:${b.category}:${uid()}`;
  await env.CACHE.put(key, JSON.stringify({ image: b.image, checkpoint: b.checkpoint || '', note: b.note || '' }),
    { metadata: { checkpoint: b.checkpoint || '', note: (b.note || '').slice(0, 80), at: Date.now() } });
  return { ok: true, key };
}
async function listRefs(env, category) {
  needKV(env);
  const res = await env.CACHE.list({ prefix: category ? `ref:${category}:` : 'ref:' });
  return { items: res.keys.map(k => ({ key: k.name, category: k.name.split(':')[1], ...(k.metadata || {}) })) };
}
async function loadRefImages(env, category, max) {
  const res = await env.CACHE.list({ prefix: `ref:${category}:` });
  const keys = res.keys.slice(-max); // ล่าสุด
  const out = [];
  for (const k of keys) { const d = await env.CACHE.get(k.name, 'json'); if (d) out.push(d); }
  return out;
}
async function addMistake(env, b) {
  needKV(env);
  const list = (await env.CACHE.get('mistakes', 'json')) || [];
  list.unshift({ category: b.category || 'generic', name: (b.name || '').slice(0, 80), what: (b.what || '').slice(0, 200), at: Date.now() });
  await env.CACHE.put('mistakes', JSON.stringify(list.slice(0, 100)));
  return { ok: true, total: list.length };
}
async function getMistakes(env, category) {
  if (!env.CACHE) return [];
  const list = (await env.CACHE.get('mistakes', 'json')) || [];
  return category ? list.filter(m => m.category === category) : list;
}

// =============================================================
//  MARKET PRICES
// =============================================================
async function serper(env, q, gl = 'th') {
  const r = await fetch('https://google.serper.dev/search', {
    method: 'POST',
    headers: { 'X-API-KEY': env.SERPER_API_KEY, 'content-type': 'application/json' },
    body: JSON.stringify({ q, gl, hl: gl === 'th' ? 'th' : 'en', num: 10 })
  });
  const d = await r.json();
  return (d.organic || []).map(o => ({ title: o.title, snippet: o.snippet || '', url: o.link, price: o.price || null }));
}

async function marketPrices(env, item) {
  const qTh = item.search_query_th || item.name_th;
  const qEn = item.search_query_en || item.name_th;
  const [th, ebay] = await Promise.all([
    serper(env, `${qTh} มือสอง ราคา (site:shopee.co.th OR site:kaidee.com OR site:facebook.com OR site:lazada.co.th)`, 'th').catch(() => []),
    serper(env, `${qEn} sold site:ebay.com`, 'us').catch(() => [])
  ]);
  const results = [...th.map(r => ({ ...r, market: 'th' })), ...ebay.map(r => ({ ...r, market: 'ebay' }))];
  if (!results.length) return { evidence: [], links: [], note: 'ค้นไม่เจอประกาศที่ใกล้เคียง' };

  const list = results.map((r, i) => `[${i}] (${r.market}) ${r.title} | ${r.snippet}${r.price ? ' | price ' + r.price : ''}`).join('\n');
  const prompt = `จากผลค้นหาด้านล่าง ดึงราคาของสินค้า "${item.name_th}" (${item.brand} ${item.model}) ออกมา
นับเฉพาะรายการที่เป็นสินค้าแบบเดียวกันจริงๆ ข้ามรายการที่เป็นสินค้าอื่น อุปกรณ์เสริม หรือไม่มีตัวเลขราคา
type = "sold" เฉพาะเมื่อข้อความบอกว่าขายแล้ว/Sold/ปิดการขาย, นอกนั้น "listing"
ตอบ JSON: {"items":[{"i":number,"amount":number,"currency":"THB|USD|GBP|EUR|JPY","type":"sold|listing","same_item":true|false}]}

${list}`;
  let parsed = { items: [] };
  try { parsed = await gemini(env, [{ text: prompt }], 'prices'); }
  catch (e) { return { evidence: [], links: results.slice(0, 5).map(linkOf), note: e.message }; }

  const usd = +(env.USD_THB || 33);
  const fx = { THB: 1, USD: usd, GBP: usd * 1.27, EUR: usd * 1.08, JPY: usd / 150 };
  const evidence = (parsed.items || [])
    .filter(x => x.same_item !== false && x.amount > 0 && results[x.i])
    .map(x => {
      const r = results[x.i];
      return { price: Math.round(x.amount * (fx[x.currency] || 1)), type: x.type === 'sold' ? 'sold' : 'listing', market: r.market, currency: x.currency, amount: x.amount, title: r.title, url: r.url };
    })
    .filter(e => e.price >= 20);
  const links = evidence.slice(0, 6).map(linkOf);
  return { evidence, links: links.length ? links : results.slice(0, 5).map(linkOf), note: '' };
}
function linkOf(r) {
  let host = '';
  try { host = new URL(r.url).hostname.replace('www.', ''); } catch (e) {}
  return { title: r.title, url: r.url, host, price: r.price ?? null, type: r.type || null };
}
