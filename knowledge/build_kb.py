# -*- coding: utf-8 -*-
"""สร้างฐานความจำเสื้อผ้าวินเทจ → apparel-kb.json + supabase/knowledge.sql
confidence: 'sourced' = มีแหล่งอ้างอิง, 'general' = ความรู้ทั่วไป ยังไม่ได้ยืนยัน (ระบบจะใช้แบบระวัง)"""
import json, os

S = {
 'defunkd_tags': 'https://defunkd.com/vintage-t-shirt-tag-dating-guide',
 'defunkd_ss': 'https://www.defunkd.com/blog/2016/12/06/the-screen-stars-timeline/amp/',
 'defunkd_fake': 'https://www.defunkd.com/fake-tag-archive/',
 'nostos_band': 'https://nostos.pages.dev/guides/vintage-band-tee-reprint-and-bootleg-identification-guide',
 'rockabilia': 'https://rockabilia.com/pages/official-vs-bootleg-band-merchandise',
 'vru_harley': 'https://www.vintagerareusa.com/blogs/news/vintage-harley-davidson-3d-emblem-tee-shirt-label-history-since-1960s-vintage-rare-usa',
 'vru_nike': 'https://www.vintagerareusa.com/blogs/news/how-to-date-my-vintage-nike-with-the-tags-vintage-rare-usa',
 'vru_champion': 'https://www.vintagerareusa.com/blogs/news/champion-reverse-weave-label-history-per-year',
 'cc_levis': 'https://www.thecollectorscompanion.co.uk/features/vintage-clothing/dating-levis/',
 'lvid_care': 'https://levis-vintage-id.vercel.app/en/articles/article-care-label',
 'ropedye': 'https://www.ropedye.com/2013/05/guide-how-to-date-levis-501-jeans/',
 'selvedge': 'https://selvedgestory.pages.dev/en/guide/vintage-denim-authentication-guide/',
 'brag_jacket': 'https://bragvintage.com/levis-denim-jacket-guide',
 'nostos_carhartt': 'https://nostos.pages.dev/guides/identifying-vintage-carhartt-and-workwear',
 'rn': 'https://1800vintage.substack.com/p/rn-numbers',
 'defunkd_copy': 'https://www.defunkd.com/copyrights-on-vintage-t-shirts/',
 'loudwire': 'https://loudwire.com/study-bands-most-valuable-vintage-t-shirts/',
 'esquire_th': 'https://esquire.co.th/2026/07/30/vintage-t-shirts-value-michael-b-jordan',
 'marketeer': 'https://marketeeronline.co/archives/429691',
 'benar': 'https://www.benarnews.org/english/news/thai/secondhand-clothes-boom-deep-south-02142025113206.html',
 'yiume_anime': 'https://www.yiume.com/es/pages/faq-why-vintage-anime-shirts-expensive-2026',
 'fsc_fake': 'https://footballshirtcollective.com/blogs/collectors-club/spot-a-fake-shirt',
 'fsc_nike': 'https://footballshirtcollective.com/blogs/collectors-club/spot-fake-nike',
 'fsc_adidas': 'https://footballshirtcollective.com/blogs/collectors-club/spot-fake-adidas',
 'fsc_kappa': 'https://footballshirtcollective.com/blogs/collectors-club/spot-fake-kappa',
 'cfs_umbro': 'https://casualfootballshirts.co.uk/pages/1990s-umbro-shirts-authenticity-checks',
 'first11_pv': 'https://first11shirts.com/blogs/informative/player-vs-fan-version-football-shirts-what-s-the-difference',
 'momentum_fb': 'https://themomentum.co/feature-football-jersey/',
 'ktc_thai': 'https://www.ktc.co.th/article/lifestyle/sport/thailand-national-team-kits',
 'bkbiz_warrix': 'https://www.bangkokbiznews.com/lifestyle/1085512',
 'cfs_thai100': 'https://www.classicfootballshirts.co.uk/2016-17-thailand-100th-anniversary-shirt-xl-this16365185.html',
 'outlook_blokecore': 'https://www.outlookindia.com/sports/football/fifa-world-cup-2026-hottest-jerseys-blokecore-retro-shirts-fashion-trends',
 'wlf_grade': 'https://www.welovefootballshop.com/product/tag/%E0%B9%80%E0%B8%AA%E0%B8%B7%E0%B9%89%E0%B8%AD%E0%B8%9F%E0%B8%B8%E0%B8%95%E0%B8%9A%E0%B8%AD%E0%B8%A5%E0%B8%AB%E0%B8%A5%E0%B8%B1%E0%B8%87%E0%B8%AA%E0%B8%99%E0%B8%B2%E0%B8%A1%E0%B8%A8%E0%B8%B8%E0%B8%A0?tskp=13',
}
T, D, F = 'apparel.vintage', 'apparel.denim', 'apparel.football'
E = []
def add(id, category, kind, title, era='', brand='', keywords=(), cues=(), red_flags=(), value='', conf='sourced', src=()):
    E.append(dict(id=id, category=category, kind=kind, brand=brand, title=title, era=era,
                  keywords=[k.lower() for k in keywords], cues=list(cues), red_flags=list(red_flags),
                  value_notes=value, confidence=conf, sources=[S[s] for s in src]))

# ============ กฎทั่วไป: เสื้อยืดวินเทจ ============
add('rule-stitch', T, 'rule', 'ตะเข็บเดี่ยว vs ตะเข็บคู่', 'ก่อนปลายยุค 90',
    keywords=['single stitch', 'ตะเข็บเดี่ยว', 'double stitch'],
    cues=['ตะเข็บเดี่ยวที่ปลายแขนและชายเสื้อ = เสื้อวินเทจโดยทั่วไป', 'ตะเข็บคู่สองแถว = มักผลิตหลังปลายยุค 90'],
    red_flags=['ข้อยกเว้น: เสื้อทัวร์ยุโรปปลายยุค 90 บางตัวใช้ตะเข็บคู่ ใช้ประกอบกับป้ายเสมอ'], src=['nostos_band'])
add('rule-print', T, 'rule', 'ดูลายสกรีน: ของเก่าจริง vs พิมพ์ใหม่', keywords=['print', 'สกรีน', 'dtg', 'heat transfer'],
    cues=['สกรีนยุคเก่า: หมึกแตก ซีด ซึมลงเนื้อผ้า จับแล้วนุ่ม', 'พิมพ์ DTG สมัยใหม่: หมึกหนา ยาง มันวาว ลอยบนผ้า',
          'ลายรีดร้อน (heat transfer) ยุค 1993–2000 เป็นของจริงแต่ราคาต่ำกว่าสกรีน: ขอบคม ผิวคล้ายพลาสติก ด้านในไม่มีหมึกซึม'],
    red_flags=['ผ้าซีดเก่าแต่ลายสดใหม่ = อาจพิมพ์ใหม่บนเสื้อเก่า'], src=['nostos_band'])
add('rule-fake-aging', T, 'rule', 'ทำเก่าปลอม vs เก่าจริง', keywords=['distressed', 'ฟอก', 'ทำเก่า'],
    cues=['เก่าจริง: ซีดแดดตามธรรมชาติ รูเข็มเล็กๆ แถวคอ/เอว คอนิ่มและลุ่ย'],
    red_flags=['ฟอกเคมีเป็นด่างไม่เป็นธรรมชาติ', 'รูที่ตัดด้วยกรรไกร', 'คอที่ขัดกระดาษทราย', 'ตัดป้ายออกจนเป็นรูเละ หรือเป็นป้ายฉีกแบบกระดาษสมัยใหม่'],
    src=['nostos_band'])
add('rule-weak-signals', T, 'rule', 'สัญญาณที่ใช้ตัดสินยุคอย่างเดียวไม่ได้', keywords=['made in usa', '50/50', 'double tag'],
    cues=['Made in USA, ผ้า 50/50, ป้ายซ้อนสองชั้น พบได้หลายแบรนด์หลายยุค ต้องใช้ร่วมกับรูปแบบป้ายและตะเข็บ',
          'ช่วงปีของแต่ละแบรนด์ทับซ้อนกัน ใช้ช่วงปีอย่างเดียวระบุแบรนด์ไม่ได้'], src=['defunkd_tags'])
add('rule-copyright', T, 'rule', 'ปีลิขสิทธิ์ (©) บนลายสกรีน', keywords=['©', 'copyright', 'ลิขสิทธิ์'],
    cues=['ปี © คือปีที่ลายได้ลิขสิทธิ์ ไม่ใช่ปีที่พิมพ์เสื้อ และไม่ค่อยถูกอัปเดต เสื้อพิมพ์ยุค 2000 อาจยังเขียน © 1994',
          'มีหลายปี: ปีแรกคือลิขสิทธิ์เดิม ปีหลังคือแก้ไข เสื้อมักผลิตหลังปีล่าสุด (เช่น Snoopy 1958/1965/1971 น่าจะผลิตยุค 80 ขึ้นไป)',
          'ตัวอย่าง: Metallica Ride the Lightning ที่พิมพ์ยุค 2000 มักมี © 1994',
          'เสื้อวงที่พิมพ์ยุค 2000 หลายตัวไม่มีบรรทัด © เลย'],
    red_flags=['ไม่มี © ไม่ได้แปลว่าปลอม (bootleg เก่าหลายตัวไม่มี)', 'มี © ก็ไม่ได้แปลว่าแท้ เพราะ bootleg ก็ลอก © ได้', 'ใช้ปี © ตัดสินยุคอย่างเดียวไม่ได้ ต้องดูป้ายและงานพิมพ์ประกอบ'],
    src=['defunkd_copy'])
add('rule-rn', T, 'rule', 'เลข RN บนป้าย', keywords=['rn', 'rn number', 'wpl'],
    cues=['RN คือเลขที่ FTC สหรัฐฯ ออกให้ผู้ผลิต/ผู้นำเข้า ใช้ค้นว่าใครผลิต', 'Screen Stars ใช้ RN 13765'],
    red_flags=['RN หรือ WPL สมัยใหม่บนป้ายที่อ้างว่าเก่า = สัญญาณป้ายปลอม'], src=['rn', 'defunkd_ss', 'defunkd_fake'])
add('rule-fake-tag', T, 'rule', 'สัญญาณป้ายคอปลอม (ทั่วไป)', keywords=['fake tag', 'ป้ายปลอม'],
    cues=['เทียบกับป้ายแท้หลายๆ ใบ เพราะป้ายแท้เองก็มีหลายแบบ', 'ดูทั้งป้ายและลายสกรีนประกอบกัน'],
    red_flags=['โลโก้หนาทึบ เส้นด้ายหยาบ จุดลายหายไป', 'ฟอนต์ ความสูงตัวอักษร ระยะห่างผิด', 'สะกดผิด', 'ขาดรายละเอียด เงา ขอบ หรือความแวววาว',
               'สีผิด', 'ไซซ์บนป้ายไม่ตรงกับขนาดจริง', 'ป้ายรอง/เลข RN-WPL ไม่ตรงยุค', 'ตำแหน่ง ™ ผิด'], src=['defunkd_fake'])

# ============ ป้ายเสื้อเปล่า (blank) ============
add('tag-screen-stars', T, 'tag', 'Screen Stars', '1980–1994', 'Screen Stars', ['screen stars', 'screenstars', 'super screen stars', 'screen stars best'],
    cues=['1980: ป้ายแรก สีน้ำเงิน/ขาว/ส้ม ใช้ปีเดียว ส่วนใหญ่ 50/50',
          '1981–1983: ตัว A แบบ "Funky A" (แบบที่ดังที่สุด), Super Screen Stars แถบเขียว 50/50, แถบน้ำเงิน 100% cotton',
          '1983–1990: ตัว A แบบเรียบขึ้น, มีรุ่น Made in Canada / Ireland / El Salvador',
          '1987–90s: Screen Stars Best แถบแดง 50/50 และแถบน้ำเงิน 100% cotton', 'RN 13765 (เครือ Fruit of the Loom)'],
    red_flags=['ป้าย "Screen Stars by FOTL Value Weight" ปลอม: น้ำเงินเข้มเกิน กล่องสี่เหลี่ยมจัตุรัส ฟอนต์ "by" ผิด'],
    value='ป้ายที่นักสะสมรู้จักดี เสื้อลายดีบนป้ายนี้มักขายได้ราคา', src=['defunkd_ss', 'defunkd_tags', 'defunkd_fake'])
add('tag-fotl', T, 'tag', 'Fruit of the Loom', '1970–1998 (ป้ายวินเทจ)', 'Fruit of the Loom', ['fruit of the loom', 'fotl', 'fruit'],
    cues=['มีรูปแบบป้ายแยกช่วง 1970s–1983 และ 1984–1993', 'มีรุ่น "Best" และ Lofteez/heavy cotton แบบป้ายซ้อน', 'ป้ายยุค 2004–2012 ไม่นับเป็นวินเทจยุคทอง'],
    red_flags=['ป้ายปลอม: ไม่มีรายละเอียดและเงาของผลไม้ และองุ่นเป็นสีม่วง'], src=['defunkd_tags', 'defunkd_fake'])
add('tag-hanes', T, 'tag', 'Hanes', '1989–1997', 'Hanes', ['hanes', 'beefy-t', 'beefy', 'ultraweight', 'hanes heavyweight'],
    cues=['ป้าย 50/50, 100% cotton, Ultraweight, Beefy-T, Heavyweight, ป้ายซ้อน, Made in USA'],
    red_flags=['Heavyweight ปลอม: เครื่องหมาย ® เหนือตัว S กลับด้าน', 'Ultraweight ปลอม: ตัว H สูงเกิน', 'แถบน้ำเงินปลอม: ขาตัว H ไม่ยาวสุด',
               'Heavyweight ป้ายซ้อนปลอม: ป้ายล่างสั้นเกิน ฟอนต์และตำแหน่งผิด'], src=['defunkd_tags', 'defunkd_fake'])
add('tag-anvil', T, 'tag', 'Anvil (และ Ched)', 'Anvil 1989–2007, Ched 1976–1988', 'Anvil', ['anvil', 'ched'],
    cues=['Ched quality knits / Anvil Athletic / Ched by Anvil = 1976–1988', 'Anvil 100% cotton pre-shrunk Made in USA, ป้ายแถบน้ำเงิน/แดง'],
    red_flags=['Anvil แถบน้ำเงิน ผลิตนิการากัว เริ่มราว 2004 ถ้าอ้างว่าเก่ากว่านี้ = น่าสงสัย'], src=['defunkd_tags', 'defunkd_fake'])
add('tag-giant', T, 'tag', 'Giant', '1991–1996', 'Giant', ['giant', 'tee jays', 'giant by'],
    cues=['Giant by Tee Jays / by Anvil / by Tultex, ผลิต El Salvador', 'พบมากบนเสื้อวงดนตรียุค 90'],
    red_flags=['ป้ายปลอมเยอะมาก: โลโก้หนาเกินไม่มีจุดลาย, ฟอนต์ใต้ "Tee Jays" ผิดขนาด', 'สะกด "SY" แทน "BY"', 'Giant by Tultex แท้ ตัว LT ใน TULTEX เกี่ยวกัน',
               'Silver Thread ปลอม: สะกดผิดที่ป้ายล่าง ™ สีแดง'], value='ป้ายนี้อยู่บนเสื้อวงที่ราคาสูง จึงถูกปลอมบ่อย ตรวจละเอียด', src=['defunkd_tags', 'defunkd_fake'])
add('tag-winterland', T, 'tag', 'Winterland', '1982–2008', 'Winterland', ['winterland'],
    cues=['Winterland Productions พบบนเสื้อวงร็อกคลาสสิกและเสื้อวงฝั่งตะวันตก (สาย Grateful Dead)'],
    red_flags=['ป้ายปลอม: โลโก้สูงเกิน กรอบรอบตัว W สูงเกิน ™ ต่ำเกิน ข้อความขาด/สะกดผิด'], src=['defunkd_tags', 'defunkd_fake', 'nostos_band'])
add('tag-brockum', T, 'tag', 'Brockum', 'ก่อน 1995', 'Brockum', ['brockum'],
    cues=['ป้าย Brockum บ่งชี้เสื้อทัวร์ก่อนปี 1995 (เช่น Rolling Stones, U2)'],
    red_flags=['Brockum Worldwide ปลอม: ฟอนต์ยืด ระยะห่างผิด โลโก้ชิดกรอบเกิน', 'The Brockum Group ปลอม: O กับ C ห่างเกิน', 'The Brockum Collection ปลอม: ไม่มีเงาเงิน สีฟ้าผิด'],
    value='เสื้อทัวร์ทางการยุคนั้น ราคาสูง', src=['nostos_band', 'defunkd_fake'])
add('tag-stedman', T, 'tag', 'Stedman / Hi-Cru', '1971–1997', 'Stedman', ['stedman', 'hi-cru', 'hi cru'],
    cues=['Hi-Cru, Sport-T by Stedman, Golden Hi-Cru, Super Hi-Cru, Stedman by Hanes, Made in USA'], red_flags=['ป้ายปลอม: ฟอนต์ผิดเกือบทั้งหมด'], src=['defunkd_tags', 'defunkd_fake'])
add('tag-sportswear', T, 'tag', 'Sportswear', '1968–1990', 'Sportswear', ['sportswear'], cues=['สองชุดป้าย: 1968–1981 และ Sportswear II 1981–1990'], src=['defunkd_tags'])
add('tag-signal', T, 'tag', 'Signal', '1977–1994', 'Signal', ['signal', 'signal artwear', 'ssi'], cues=['100% cotton, Sports, SSI, Signal Artwear, Signal Sport'], src=['defunkd_tags'])
add('tag-jerzees', T, 'tag', 'Jerzees', '1985–1998', 'Jerzees', ['jerzees', 'russell'], cues=['Jerzees by Russell, Super-T, 100% combed cotton, pre-shrunk'], src=['defunkd_tags'])
add('tag-oneita', T, 'tag', 'Oneita', '1984–1999', 'Oneita', ['oneita', 'power-t', 'powerpro'], cues=['Power-T, PowerPro, Power/50, ผ้า 50/50 หรือ 100%'],
    red_flags=['Power-T สีปลอม: ระยะห่างตัวอักษรโลโก้กว้างเกิน'], src=['defunkd_tags', 'defunkd_fake'])
add('tag-delta', T, 'tag', 'Delta', '1988–2014', 'Delta', ['delta', 'pro-weight', 'magnum weight'], cues=['Pro-Weight, Magnum Weight, Made in USA; ช่วง 2002–2013 ประกอบที่ฮอนดูรัส (ใหม่กว่า)'], src=['defunkd_tags'])
add('tag-tennessee-river', T, 'tag', 'Tennessee River', '1984–2010', 'Tennessee River', ['tennessee river'], cues=['ป้ายสีทอง, ป้ายซ้อน, ประกอบที่เม็กซิโก (รุ่นหลัง)'], src=['defunkd_tags'])
add('tag-wild-oats', T, 'tag', 'Wild Oats', '1984–1997', 'Wild Oats', ['wild oats'], cues=['Made in USA, ข้อความ "100% oats"'],
    red_flags=['ป้ายปลอม: เขียน LG ข้าง XL (ของแท้เป็น TG)'], src=['defunkd_tags', 'defunkd_fake'])
add('tag-alstyle', T, 'tag', 'Alstyle (AAA)', '1995–2006', 'Alstyle', ['alstyle', 'aaa'], cues=['เครื่องหมาย AAA, 100% cotton pre-shrunk, ทำที่เม็กซิโกจากผ้าสหรัฐฯ'],
    red_flags=['ป้ายปลอม: มีเส้นเกินที่ด้านล่าง ฟอนต์และระยะห่างผิด'], src=['defunkd_tags', 'defunkd_fake'])
add('tag-gildan', T, 'tag', 'Gildan', '1995–2002 (ป้ายยุคเก่า)', 'Gildan', ['gildan', 'ultra cotton'],
    cues=['ป้าย Heavyweight / Ultra Cotton ยุคปลาย 90', 'Gildan ยังผลิตจนปัจจุบัน ป้ายรุ่นใหม่ไม่นับเป็นวินเทจ'],
    red_flags=['เสื้อวงที่อ้างว่ายุค 80 แต่ป้าย Gildan = ผลิตใหม่ (reprint)', 'Ultra Cotton ปลอม: ระยะตัวอักษรและฟอนต์แถบน้ำเงินผิด ตัว U ลอยสูง'],
    src=['defunkd_tags', 'defunkd_fake'], conf='sourced')
add('tag-3d-emblem', T, 'tag', '3D Emblem', 'ยุค 80 (Harley และอื่นๆ)', '3D Emblem', ['3d emblem', '3-d emblem'],
    cues=['พบบนเสื้อ Harley-Davidson ยุค 80 บางตัว'], red_flags=['ป้ายปลอม: ไม่มีเอฟเฟกต์ 3D ฟอนต์หนา เลข 3 กับตัว D ไม่เข้ากัน ฟอนต์ "Emblem" ผิด'],
    src=['vru_harley', 'defunkd_fake'])
add('tag-liquid-blue', T, 'tag', 'Liquid Blue', '', 'Liquid Blue', ['liquid blue'], red_flags=['ป้ายปลอม: สีเพี้ยน มีเส้นขอบรอบลายวน/หยด เส้นด้ายหยาบ'], src=['defunkd_fake'])
add('tag-tultex', T, 'tag', 'Tultex', '', 'Tultex', ['tultex'], red_flags=['ป้ายปลอม: ระยะตัวอักษรกว้างเกิน "X-Large" ไม่อยู่กลางแถบแดง'], src=['defunkd_fake'])
add('tag-spring-ford', T, 'tag', 'Spring Ford', '', 'Spring Ford', ['spring ford'], red_flags=['ป้ายปลอม: ใช้ฟอนต์ตัวเขียน และไม่มีจุดหลัง U.S.A'], src=['defunkd_fake'])

# ============ ประเภทเสื้อที่ตลาดต้องการ ============
add('genre-band', T, 'genre', 'เสื้อวงดนตรี (Band tee)', keywords=['band', 'tour', 'เสื้อวง', 'metallica', 'nirvana', 'rolling stones', 'u2', 'grateful dead', 'guns n roses', 'iron maiden', 'concert'],
    cues=['3 ระดับ: เสื้อทัวร์ทางการ (ราคาสูงสุด) > bootleg ยุคเก่าที่ขายหน้าคอนเสิร์ต (ก็มีมูลค่า) > ของปลอม/พิมพ์ใหม่',
          'เสื้อทางการ: มีป้ายลิขสิทธิ์ บรรทัด © และป้ายตรงยุค', 'Bootleg ยุคเก่า: ลายใหญ่ ไม่มีป้ายลิขสิทธิ์ แต่ตัวเสื้อและป้ายเปล่าเก่าจริง',
          'วงที่นักสะสมตามหามาก: Nirvana (In Utero), Metallica (Ride the Lightning) และวงกรันจ์/เมทัลยุค 90',
          'ดูวันทัวร์ด้านหลังเทียบกับยุคป้าย'],
    red_flags=['ลายเบลอแตกพิกเซล โลโก้ถูกตัด/บิด พิมพ์เบี้ยว', 'ป้ายลิขสิทธิ์ไม่มีหรือดูไม่เป็นทางการ (สำหรับเสื้อที่อ้างว่าเป็นของทางการ)', 'ราคาถูกผิดปกติ'],
    value='หมวดราคาสูงสุดของเสื้อยืดวินเทจ จึงเป็นหมวดที่ถูกปลอมมากที่สุด', src=['nostos_band', 'rockabilia'])
add('genre-harley', T, 'genre', 'Harley-Davidson', keywords=['harley', 'harley-davidson', 'harley davidson', 'motor clothes', 'sturgis', 'laconia'],
    cues=['ยุค 60–70: มักไม่มีป้ายเฉพาะ ใช้เสื้อเปล่า Hanes/Screen Stars/Champion', 'ยุค 80: ป้าย Harley สีดำโลโก้ bar & shield ส้มขาว บางตัวใช้ป้าย 3D Emblem',
          'ยุค 90: ป้ายทอเรียบร้อยขึ้น บางตัวเขียน Harley-Davidson Motor Clothes', 'ด้านหลังมักพิมพ์ชื่อดีลเลอร์/เมือง (นิยมในยุค 80)',
          'Made in USA ยุค 80–90 มักเป็นตะเข็บเดี่ยว; ผลิตในสหรัฐฯ ส่วนใหญ่หยุดราว 2010'],
    red_flags=['ป้าย "Harley Clothes" ปลอม: ฟอนต์ HARLEY สูงผอมเกิน ระยะรอบ "Clothes" ผิด'],
    value='ลายดีลเลอร์เฉพาะพื้นที่ยุค 80 และเสื้องานแรลลี่ (Sturgis, Laconia) นักสะสมนิยม', src=['vru_harley', 'defunkd_fake'])
add('genre-nike', T, 'brand', 'Nike (ป้ายเสื้อผ้า)', keywords=['nike', 'swoosh'],
    cues=['Pinwheel 1978–1982', 'ป้ายส้ม 1978–1983', 'ป้ายน้ำเงิน 1984–1987', 'ป้ายเทา ราว 1987–1994', 'ป้ายดำ ราว 1994', 'ป้ายขาว 1994–1999', 'ป้ายแดงดำ 1997–1999', 'ป้ายเงิน ต้น-กลางยุค 2000'],
    red_flags=['ป้ายบอกช่วงเวลา ไม่ใช่ปีเป๊ะ และช่วงทับซ้อนกันได้', 'ผลิตนอกสหรัฐฯ ไม่ได้แปลว่าปลอมหรือใหม่เสมอไป'], src=['vru_nike'])
add('genre-champion', T, 'brand', 'Champion Reverse Weave', keywords=['champion', 'reverse weave'],
    cues=['ยุค 50–60: ป้ายแรกที่มีคำว่า Reverse Weave', 'ปลาย 60–70: ป้ายหลายสี (น้ำเงิน เหลือง แดง เขียว ดำ) Made in USA',
          'ยุค 80: Made in USA ผ้า 90% cotton/10% acrylic หรือ 89/8/3 (cotton/acrylic/rayon)', 'ยุค 90: ส่วนใหญ่ USA บางส่วนเม็กซิโก', 'ปลาย 90–2000: ย้ายไปเม็กซิโก/เอลซัลวาดอร์'],
    value='สเวตเตอร์ Reverse Weave Made in USA เป็นที่ต้องการ', src=['vru_champion'])
add('genre-souvenir', T, 'genre', 'เสื้อท่องเที่ยว/ที่ระลึก', keywords=['souvenir', 'tourist', 'city', 'hard rock cafe', 'dublin', 'hawaii', 'florida', 'pubs'],
    cues=['ราคาขึ้นกับลาย (ลายแผนที่/ภาพประกอบสวยขายง่ายกว่า) ตะเข็บเดี่ยว และสภาพ'],
    red_flags=['Hard Rock Cafe ผลิตเยอะมาก ราคาส่วนใหญ่ไม่สูง'], value='ราคาส่วนใหญ่ระดับกลาง-ล่าง เหมาะเป็นของหมุนเร็ว', conf='general')
add('genre-cartoon-movie', T, 'genre', 'เสื้อการ์ตูน/คอมิก/หนัง', keywords=['disney', 'mickey', 'looney', 'simpsons', 'marvel', 'spider-man', 'spiderman', 'star wars', 'pulp fiction', 'matrix', 'movie', 'การ์ตูน', 'หนัง'],
    cues=['ลิขสิทธิ์ทางการมีบรรทัด © ของเจ้าของลิขสิทธิ์', 'Marvel ยุค 90 เป็นที่ต้องการ: เสื้อ Spider-Man/Daredevil/Silver Surfer ปี 1997 เคยขายออนไลน์ได้ 220,000 บาท',
          'เสื้อโปรโมตหนังยุคแรก (Star Wars, Pulp Fiction, The Matrix) หลายรุ่นไม่ได้ผลิตขายทั่วไป นักสะสมตามหา'],
    red_flags=['ลายการ์ตูนดังถูกพิมพ์ซ้ำเยอะ เช็คป้ายกับยุคของลายเสมอ'],
    value='ตัวที่ราคาสูงคือลายหายากและของเก่าจริง ลายทั่วไปราคาระดับกลาง', src=['benar', 'esquire_th'])
add('genre-anime', T, 'genre', 'เสื้ออนิเมะยุค 90 (Akira, Dragon Ball ฯลฯ)', keywords=['akira', 'dragon ball', 'dbz', 'ghost in the shell', 'anime', 'อนิเมะ', 'manga'],
    cues=['Akira ถูกยกเป็นตัวท็อป ลายต้นฉบับปี 1988 มีรายงานราคาประมูลเกิน $3,000', 'Dragon Ball Z ยุค 90 โดยเฉพาะลายพิมพ์รอบตัว (AOP), Ghost in the Shell',
          'ป้ายต้องเข้ากับยุคของลาย: ลาย Akira 1988 บนป้ายยุค 2010 = พิมพ์ใหม่', 'ตะเข็บเดี่ยว, สกรีนซึมเนื้อผ้า, © พิมพ์ลงเนื้อผ้า ไม่ลอยบนผิว'],
    red_flags=['ซีดด้วยน้ำยาฟอกขาวเลียนแบบความเก่า', 'ลายพิมพ์ดิจิทัล/รีดร้อนที่ผิวเป็นพลาสติก'],
    value='ตัวเลขราคามาจากร้านขาย ยังไม่มีแหล่งอื่นยืนยัน ใช้เป็นแนวทางเท่านั้น', conf='general', src=['yiume_anime'])
add('band-value', T, 'genre', 'เสื้อวงที่ราคาสูง (ข้อมูลขายจริง)', keywords=['nirvana', 'grateful dead', 'bjork', 'björk', 'soundgarden', 'metallica', 'red hot chili peppers', 'rhcp', 'guns n roses', "guns n' roses", 'green day', 'pearl jam', 'earth wind', 'oasis', 'pushead'],
    cues=['ผลศึกษาราคาขายต่อ (ธ.ค. 2023–ก.ย. 2024): Grateful Dead "Panther" สูงสุด $2,750, Nirvana In Utero แขนยาว $2,000, Björk Post (1995), Soundgarden Louder Than Love (1989), Metallica Load (1996), Nirvana Sliver tour (1992)',
          'วงที่ราคาเฉลี่ยต่อตัวสูง: Nirvana, Red Hot Chili Peppers, Earth Wind & Fire, Guns N\' Roses, Green Day, Paul McCartney, Pearl Jam',
          'ยุคที่ราคาดีที่สุด: ปลายยุค 80 ถึงกลางยุค 90 แนวร็อกราคาเฉลี่ยสูงกว่าป๊อปและแร็ป',
          'Grateful Dead ลาย Dancing Bears/Skeleton และ Metallica ลายของ Pushead เป็นที่ตามหา',
          'Oasis ยุค 90 ความต้องการเพิ่มขึ้นหลังประกาศรียูเนียนปี 2025'],
    red_flags=['ราคาประเมินกับราคาซื้อขายจริงต่างกันได้มาก (เช่น เสื้อ Nirvana staff ปี 1991 ที่มีข่าวประเมิน 1.35 ล้านบาท แต่เจ้าของซื้อมาหลักหมื่น)', 'วงดังที่สุดคือวงที่มีของพิมพ์ใหม่มากที่สุด'],
    value='เสื้อทัวร์ทางการ/ลายอัลบั้มเฉพาะ และเสื้อทีมงานที่ผลิตน้อย ราคาสูงสุด', src=['loudwire', 'esquire_th', 'marketeer'])
add('market-thai-bale', T, 'market', 'ตลาดเสื้อมือสองกระสอบในไทย', keywords=['กระสอบ', 'bale', 'มือสอง', 'โรงเกลือ', 'ยะลา', 'ปัตตานี'],
    cues=['เสื้อมือสองส่วนใหญ่มาจากสหรัฐฯ ส่งเรือไปมาเลเซียแล้วเข้าไทย', 'ตัวอย่างจากภาคใต้: กระสอบละราว 1,000 บาท มีเสื้อยืด 200–220 ตัว หรือแจ็คเก็ต/กางเกง 150–180 ตัว',
          'ตลาดที่มีข่าว: ตลาดมะพร้าว (ยะลา), รูสะมิแล และยะหริ่ง (ปัตตานี)',
          'ของที่ขายได้ราคา: เสื้อยืดผลิตในสหรัฐฯ ผ้าบาง (นักสะสมญี่ปุ่นชอบ), เสื้อวงทั้งทางการและ bootleg, เสื้อทหารยุคสงคราม, ชุดทำงาน, ยีนส์, เสื้อกีฬา, เสื้อฮาวาย',
          'ตัวอย่าง: เสื้อยุค 70 ซื้อ 80 บาท ขายได้ 22,000 บาท'],
    value='กำไรมาจากการรู้ว่าตัวไหนมีค่า ใช้โหมดสแกนรัวคัดกอง', src=['benar'])
add('trend-now', T, 'trend', 'กระแสตอนนี้ (อัปเดต พ.ย. 2026)', keywords=['trend', 'กระแส', 'blokecore', 'oasis', 'world cup'],
    cues=['เสื้อกราฟิก/วินเทจกลับมาได้รับความสนใจในช่วง 2–3 ปีที่ผ่านมา เสื้อวงและเสื้อหนังนิยมสูง',
          'เสื้อบอลย้อนยุคมาแรงจากกระแส blokecore และฟุตบอลโลก 2026', 'Oasis ยุค 90 ความต้องการเพิ่มหลังรียูเนียน', 'เสื้ออนิเมะยุค 90 คนรุ่นใหม่สนใจ'],
    red_flags=['กระแสเปลี่ยนเร็ว ควรอัปเดตหัวข้อนี้ทุก 2–3 เดือน'], src=['esquire_th', 'outlook_blokecore', 'marketeer'])

# ============ ยีนส์และเสื้อผ้าวินเทจอื่น ============
add('levis-tab', D, 'brand', "Levi's: แท็บแดง (Big E / small e)", keywords=["levi's", 'levis', 'levi', 'big e', 'red tab', 'แท็บแดง', 'บิ๊กอี'],
    cues=['Big E (LEVI\'S ตัว E ใหญ่) = ก่อนปี 1971', 'small e (Levi\'s ตัว e เล็ก) = ตั้งแต่ 1971', 'แท็บพิมพ์ด้านเดียว = รุ่นเก่ามาก (ราวก่อนกลางยุค 50)',
          'ราว 10% ของการผลิตใช้แท็บเปล่า แท็บเปล่าจึงไม่ได้บอกยุค', 'small e บางรุ่นก็หายากและมีราคา'],
    red_flags=['Big E กลับมาใช้อีกตั้งแต่ 2018 บนสินค้าพรีเมียม', 'LVC (Levi\'s Vintage Clothing) และของปลอมอาจมีทั้ง Big E และป้ายวิธีซัก = ต้องดูป้ายวิธีซักและรายละเอียดอื่นประกอบ'],
    value='Big E ราคาสูงกว่ามาก', src=['cc_levis', 'ropedye', 'selvedge'])
add('levis-construction', D, 'rule', "Levi's: หมุด ตะเข็บ ริม ป้ายหลัง", keywords=["levi's", 'levis', '501', 'selvedge', 'redline', 'ริมแดง', 'hidden rivet'],
    cues=['หมุดซ่อนในกระเป๋าหลัง 1937–1966 จากนั้นเปลี่ยนเป็นบาร์แทค', 'ป้ายหนัง Two Horse จนถึงราว 1955 จากนั้นเป็นป้ายกระดาษ (Jacron)',
          'ผ้าริม (selvedge/ริมแดง) ด้านในตะเข็บข้างขา = ราวก่อนกลางยุค 80', 'ตะเข็บด้านนอกขาแบบโพ้งสีส้มราว 1981, โพ้งสีขาวราว 1985',
          'ตะเข็บด้านบนกระเป๋าหลังแบบเดี่ยว (lock stitch) ราวก่อน 1976 จากนั้นเป็นแบบโซ่', 'หลังเอวรัด (cinch back) เลิกราว 1947'],
    red_flags=['ซีดสม่ำเสมอผิดธรรมชาติหรือฟอกดูถูก = ระวัง', 'ของ repro ญี่ปุ่นทำรายละเอียดได้เหมือนมาก ต้องดูหลายจุดประกอบ'],
    src=['cc_levis', 'ropedye', 'selvedge'])
add('levis-care', D, 'rule', "Levi's: อ่านป้ายวิธีซักและรหัสวันผลิต", keywords=["levi's", 'levis', 'care tag', 'care label', 'ป้ายวิธีซัก'],
    cues=['ไม่มีป้ายวิธีซักเลย = ก่อนราว 1971', 'ราว 1968–1972: วิธีซักพิมพ์ในผ้ากระเป๋า', '1973–1983: ป้ายกระดาษเล็กข้างตะเข็บซ้าย มีวงกลมสีบอกรหัส',
          'ราว 1984 เป็นต้นไป: รหัส 3 หลัก เช่น 127 = ธันวาคม 1987', '1993 เป็นต้นไป: รหัส 4 หลัก เช่น 1295 = ธันวาคม 1995',
          'ป้ายรูป batwing ตั้งแต่ 1986/1987, คำว่า "Care on Reverse" = ก่อนราว 1992', 'Made in USA สิ้นสุดราวปี 2003'],
    red_flags=['ป้ายบอกปีล่าสุดแต่ดีไซน์อ้างว่าเก่า = รุ่น repro/LVC'], src=['lvid_care', 'cc_levis'])
add('levis-jackets', D, 'brand', "Levi's: แจ็คเก็ตยีนส์ Type I / II / III", keywords=['jacket', 'trucker', '506xx', '507xx', '557', '70505', 'แจ็คเก็ต', 'type i', 'type ii', 'type iii'],
    cues=['Type I (506XX): ก่อนยุค 40 กระเป๋าหน้าเดียวมีหมุดที่มุม หลังมีหัวเข็มขัดรัด (หายากสุด)', 'Type II (507XX): ปลายยุค 40–60 กระเป๋าอกสองข้างมีฝาติดกระดุม ใช้บาร์แทคแทนหมุด',
          'Type III (557XX): 1962 ฝากระเป๋าแหลม (ทรง Trucker)', 'ก่อน 1971: ตะเข็บแถวเดียวที่รังกระดุมล่าง; ตั้งแต่ 1971: ตะเข็บสองแถว + small e',
          'กลางยุค 80 ขึ้นไป: 4 กระเป๋า (อก 2 + ล้วงข้าง 2) นักสะสมสนใจน้อยกว่า'],
    value='ยิ่งเก่า (Big E, 2 กระเป๋า) ยิ่งแพง', src=['brag_jacket'])
add('lee', D, 'brand', 'Lee 101 / 101Z', keywords=['lee', '101z', '101j', 'storm rider', 'lazy s'],
    cues=['ผ้า Left-Hand Twill (ลายทแยงกลับด้านกับ Levi\'s)', 'ตะเข็บกระเป๋าหลังรูป Lazy S (ปรับดีไซน์ราว 1944–1946)', '101Z ซิปหน้าเริ่มราว 1926–1927', 'ป้ายเปลี่ยนจากหนังเป็นกระดาษใส'],
    src=['selvedge'])
add('wrangler', D, 'brand', 'Wrangler 13MWZ', keywords=['wrangler', '13mwz', 'blue bell', '11mwz'],
    cues=['13MWZ เปิดตัว 1947', 'ผ้าทวิลธรรมดา 1947–1963, ผ้า Broken Twill ตั้งแต่ 1964', 'หมุดซ่อน ตะเข็บรูป W นูนที่กระเป๋าหลัง ซิปหน้า'], src=['selvedge'])
add('carhartt', D, 'brand', 'Carhartt', keywords=['carhartt', 'detroit jacket', 'j01', 'j97', 'chore coat', 'double knee'],
    cues=['รหัสวันที่ในป้ายวิธีซัก อ่านเป็นเดือน-ปี เช่น 0698 = มิถุนายน 1998, ต้นยุค 90 อาจไม่มีศูนย์นำหน้า เช่น 591 = พฤษภาคม 1991',
          'ป้าย Union + Made in USA = ยุคก่อนย้ายฐานผลิต', 'J01 Detroit: ผ้าดั๊กแข็ง 12oz ไซซ์เป็นตัวเลข (38–44) ปกลูกฟูก', 'J97 Detroit: ปลายยุค 90 ไซซ์ตัวอักษร ผ้านุ่มกว่า'],
    red_flags=['ซิปไม่มียี่ห้อเบาๆ (ของเก่ามักเป็น YKK หนัก หรือ Talon ทองเหลือง)', 'ปักโลโก้ใหญ่หรือเบี้ยว', 'ซับในฟลีซเทาสังเคราะห์ (ของเก่ามักเป็นซับผ้าห่มลายสก็อต)', 'ทำเก่าด้วยเคมี'],
    value='Detroit Jacket และ Made in USA เป็นที่ต้องการ', src=['nostos_carhartt'])
add('denim-general', D, 'rule', 'ยีนส์วินเทจ: ดูผ้าและการซีด', keywords=['denim', 'jeans', 'ยีนส์', 'rope dye'],
    cues=['ยีนส์เก่าส่วนใหญ่ย้อมแบบ rope dye ซีดเป็นเส้นแนวตั้ง มีรอยรังผึ้งหลังเข่าและหนวดแมว', 'ผ้ายีนส์วินเทจมักหนาราว 13–15oz'],
    red_flags=['ซีดสม่ำเสมอผิดธรรมชาติ', 'อย่าเชื่อป้าย "Made in [ปี]" หรือคำบรรยายของผู้ขายโดยไม่ตรวจเอง', 'อย่าใช้ Big E อย่างเดียวตัดสิน'], src=['selvedge'])

# ============ เสื้อฟุตบอล ============
add('fb-rule-check', F, 'rule', 'เสื้อบอล: เช็คของแท้พื้นฐาน', keywords=['football', 'soccer', 'jersey', 'kit', 'เสื้อบอล', 'เสื้อฟุตบอล', 'product code'],
    cues=['หารหัสสินค้าบนป้ายด้านใน แล้วค้นใน Google ต้องขึ้นเสื้อตัวเดียวกันเป๊ะ (ทีม ปี เหย้า/เยือน)', 'ผู้ขายไม่ยอมโชว์ป้าย = สัญญาณเตือน, ป้ายถูกตัดออก = ซื้อเสี่ยงเอง',
          'เทียบสี ความคมของลาย และตำแหน่งดีไซน์กับรูปจากร้านทางการ'],
    red_flags=['ป้ายเสื้อเก่ามีรอยปากกา/ดินสอเขียน', 'เสื้อออกใหม่ลด 50% หรือของหายากราคาถูกผิดปกติ', 'เสื้อก่อนปี 2000 มีครบทุกไซซ์ XS–XXL', 'ประกาศใช้คำว่า "replica" หรือ "retro" (อาจเป็นงานทำใหม่หรือของปลอม)'],
    src=['fsc_fake'])
add('fb-thai-grade', F, 'rule', 'คำว่า "เกรดเอ / เกรดแฟนบอล / เกรดนักเตะ" ในไทย', keywords=['เกรดเอ', 'เกรด a', 'aaa', 'เกรดไทย', 'งานไทย', 'เกรดนักเตะ', 'เกรดแฟนบอล'],
    cues=['ในไทยมีร้านขายเสื้อบอลที่ระบุว่า "เกรดเอ/เกรดแฟนบอล/เกรดนักเตะ/เกรดพรีเมียม" แยกจากของลิขสิทธิ์', 'ของลิขสิทธิ์จริงก็มีรุ่นนักเตะ (Player/Authentic) กับรุ่นแฟน (Replica) แต่ต้องเช็ครหัสสินค้าได้'],
    red_flags=['ผู้ขายเรียกว่า "เกรด..." แทนการบอกว่าลิขสิทธิ์แท้ = ให้ถือว่าไม่ใช่ของลิขสิทธิ์ อย่าซื้อในราคาของแท้ และอย่าขายต่อว่าเป็นของแท้'],
    conf='general', src=['wlf_grade'])
add('fb-player-fan', F, 'rule', 'รุ่นนักเตะ (Player/Authentic) vs รุ่นแฟน (Replica)', keywords=['player issue', 'player version', 'authentic', 'replica', 'fan version', 'vaporknit', 'dri-fit adv', 'heat.rdy', 'aeroready', 'รุ่นนักเตะ', 'รุ่นแฟน'],
    cues=['รุ่นนักเตะ: ทรงเข้ารูป ผ้าบางเบาระบายอากาศ โลโก้/ตราแบบรีดร้อน ใช้ Nike Dri-FIT ADV หรือ adidas HEAT.RDY',
          'รุ่นแฟน: ทรงปกติ ผ้าหนากว่า โลโก้/ตราแบบปัก ใช้ Nike Dri-FIT หรือ adidas AEROREADY', 'ทั้งสองรุ่นเป็นของลิขสิทธิ์ คำว่า "authentic" หมายถึงรุ่นนักเตะ',
          'ราคาป้ายยุโรป: รุ่นนักเตะราว €140–160, รุ่นแฟนราว €90–110', 'เสื้อยุคเก่า รุ่นนักเตะกับรุ่นแฟนแยกกันชัดเจนแค่ราว 10 ปีหลัง'],
    src=['first11_pv', 'momentum_fb'])
add('fb-nike', F, 'brand', 'Nike: เช็คเสื้อบอล', keywords=['nike', 'swoosh'],
    cues=['รหัสสินค้า: ป้ายเล็กด้านในใกล้ชายเสื้อ รูปแบบ ตัวเลข 6 หลัก-3 หลัก (เช่น 123456-789) ค้นแล้วต้องขึ้นเสื้อตัวนั้นเป๊ะ',
          'Jock tag (ป้ายด้านหน้ามุมล่าง) มีรหัสยาวที่ไม่ซ้ำกันในแต่ละตัว', 'เสื้อรุ่นใหม่มีป้ายที่ปลายแขน', 'ขอบ swoosh คม'],
    red_flags=['รหัสสินค้าขึ้นเป็นเสื้ออีกตัว (เช่น ชุดเหย้าแทนชุดเยือน)', 'ไม่มีป้ายรหัสสินค้า', 'รหัส jock tag ซ้ำกับเสื้อหลายตัว', 'ปลาย swoosh ลากยาว งานปักเละ',
               'ด้านในหลัง swoosh/ตรามีวัสดุรองเกินมาก (สัญญาณคลาสสิก)', 'ป้ายคอบนเสื้อรุ่นใหม่ (ไม่ได้ปลอมเสมอ แต่ต้องเช็คเพิ่ม)', 'France 2016 ชุดเยือน เป็นรหัสที่ของปลอมใช้บ่อย'],
    src=['fsc_nike'])
add('fb-adidas', F, 'brand', 'adidas: เช็คเสื้อบอล', keywords=['adidas', 'three stripes', 'trefoil'],
    cues=['รหัสสินค้าที่ป้ายคอด้านใน: ตัวอักษร 2 ตัว + ตัวเลข 4 ตัว (เช่น DP2644) ค้นแล้วต้องตรงเสื้อ', 'ป้ายคอของแท้มีตัวย่อชื่อสโมสร/ประเทศ',
          'โลโก้: ตัวหนังสือแตะขอบล่างของแถบ ระยะตัวอักษรสม่ำเสมอ แถบตรง', 'jock tag มักอยู่มุมล่างด้านหน้า ไม่มีก็ไม่ได้แปลว่าปลอม (รุ่นแฟนบางรุ่นไม่มี)'],
    red_flags=['ป้ายคอเขียนกว้างๆ ว่า "ADIDAS JSY"', 'ป้ายคอติดกลับหัว', 'ด้ายลากระหว่างตัวอักษร ฟอนต์บางเกิน แถบเบี้ยว ผ้าย่นรอบโลโก้', 'ของหายากราคาถูก หรือมีครบทุกไซซ์'],
    src=['fsc_adidas'])
add('fb-umbro', F, 'brand', 'Umbro ยุค 90', keywords=['umbro'],
    cues=['ป้ายคอสีน้ำเงิน ตัวอักษร UMBRO มีจุดชัด', 'บางตัวมีป้ายขาวบอกไซซ์/วิธีซักใต้ป้ายน้ำเงิน (ต้นยุค 90 มักไม่มี ปลายยุค 90 เกือบทุกตัวมี)',
          'ป้ายคอสีขาวตัวอักษรน้ำเงิน พบบ่อยในเสื้อ Celtic', 'ช่วง 1998–2000 เปลี่ยนแบบป้าย อาจเจอทั้งสองแบบในเสื้อลายเดียวกัน'],
    red_flags=['ไม่มีจุดในตัวอักษร UMBRO', 'ป้ายแบนเรียบ เย็บน้อยกว่า (แต่ป้ายยุค 90 เย็บไม่สวยก็เป็นของแท้ได้)'], src=['cfs_umbro'])
add('fb-kappa', F, 'brand', 'Kappa', keywords=['kappa', 'omini', 'kombat'],
    cues=['รุ่นใหม่: ป้ายด้านในมีหมายเลข/QR ตรวจที่ BasicLabels.net', 'ยุค 90: ป้ายหลักด้านในมีจุด 6 จุดเรียงสองแนวทแยง สม่ำเสมอ', 'ของแท้มักมีป้ายด้านในมากกว่าของปลอม',
          'Barcelona 1992–95 ชุดเหย้า: ด้านหน้าไม่มีโลโก้ Kappa ดูป้าย "Barça F.C.B." และ "Sports Kappa S.A." ด้านใน'],
    red_flags=['หมายเลขตรวจไม่เจอหรือขึ้นเสื้อตัวอื่น', 'จุดบนป้ายกระจายไม่เท่ากัน', 'ตัวอักษร Kappa ป่อง', 'รูปคนสองคนใน Omini ผิดทรง', 'ป้าย KOMBAT แบบตัวอักษรเจาะทะลุ'],
    value='เสื้อ Kappa ยุค 90 ถูกปลอมเยอะมาก', src=['fsc_kappa'])
add('fb-demand-thai', F, 'genre', 'เสื้อบอลวินเทจที่คนไทยตามหา', keywords=['manchester united', 'man utd', 'แมนยู', 'everton', 'ac milan', 'milan', 'man city', 'แมนซิตี้', 'real madrid', 'southampton', 'liverpool', 'ลิเวอร์พูล', 'sharp', 'batistuta', 'shevchenko', 'totti', 'gerrard', 'beckham', 'england 1990'],
    cues=['นักเตะยุค 90–2000 ที่นิยม: Batistuta, Shevchenko, Totti, Gerrard, Le Tissier', 'Everton และแมนยูยุคสปอนเซอร์ Sharp',
          'AC Milan ชุดเหย้าครบรอบ 100 ปี, แมนซิตี้ชุดเยือน 1993–94 (แฟน Oasis ตาม), เรอัลมาดริดยุค Beckham, อังกฤษฟุตบอลโลก 1990',
          'หายาก: Southampton 1991–93, แมนยูชุดเยือน 1970', 'ราคาที่บทความระบุ: ส่วนใหญ่หลักร้อยถึงหลักพัน, AC Milan 100 ปี 8,000–10,000 บาท, แมนซิตี้เยือน 93–94 ตั้งแต่ 15,000 บาท, แมนยูเยือน 1970 หลักหมื่นขึ้นไป',
          'ร้านเฉพาะทาง: TJ Football Shop จตุจักร (อาคารตึกแดง)'],
    red_flags=['ความร้อนทำให้เบอร์/ชื่อที่พิมพ์ละลาย เก็บในถุง ไม่ตากแดด', 'การติดอาร์มแขนไม่ดีทำให้เสื้อเสียหาย'],
    value='ยุค 70–80 หายากที่สุด ทีม/ฤดูกาลที่ผูกกับนักเตะหรือเหตุการณ์ดังราคาดี ราคาในบทความอาจเปลี่ยนแล้ว', src=['momentum_fb'])
add('fb-demand-global', F, 'trend', 'เสื้อบอลย้อนยุคที่ฮิต (กระแส blokecore + ฟุตบอลโลก 2026)', keywords=['germany', 'nigeria', 'brazil', 'argentina', 'england', 'mexico', 'france', 'croatia', 'japan', 'canada', 'norway', 'world cup', 'blokecore', 'ทีมชาติ'],
    cues=['ย้อนยุคที่ฮิต: เยอรมนี Italia 90, ไนจีเรีย 1994, บราซิล 2002, อาร์เจนตินา 1986, อังกฤษ Euro 96, เม็กซิโก 1998, ฝรั่งเศส 1998, โครเอเชีย 1998',
          'ชุดฟุตบอลโลก 2026 ที่ถูกพูดถึง: เยอรมนีเหย้า, เม็กซิโกเหย้า, ญี่ปุ่นเยือน, แคนาดาเยือนสีดำ, นอร์เวย์, อาร์เจนตินา', 'กระแส blokecore ใส่เสื้อบอลคู่กับยีนส์ทรงหลวม'],
    red_flags=['ชุดที่ฮิตคือชุดที่ถูกทำซ้ำ (retro remake) และปลอมมากที่สุด เช็ครหัสสินค้าเสมอ'], src=['outlook_blokecore'])
add('fb-thailand', F, 'genre', 'เสื้อทีมชาติไทย', keywords=['thailand', 'ทีมชาติไทย', 'ช้างศึก', 'ชบาแก้ว', 'grand sport', 'แกรนด์สปอร์ต', 'warrix', 'วอริกซ์'],
    cues=['ผู้ผลิตที่ผ่านมา: Grand Sport และปัจจุบัน Warrix มีทั้งเกรดนักเตะและเกรดแฟน', 'ที่นักสะสมสนใจ: Grand Sport ลาย "ศักดิ์ศรีปฐพีไทย" และเสื้อครบรอบ 100 ปี (2016–17) ที่บทความบอกว่าหายากแล้ว, รุ่น Limited Edition',
          'ราคาป้าย Warrix ฤดูกาล 2023/24: Player 2,490 บาท, Replica 890 บาท, เสื้อเชียร์ 399 บาท'],
    red_flags=['เสื้อเชียร์ราคาถูกไม่ใช่เสื้อแข่ง อย่าตีราคาเท่ารุ่น Player'], src=['ktc_thai', 'bkbiz_warrix', 'cfs_thai100'])

# ============ เขียนไฟล์ ============
here = os.path.dirname(os.path.abspath(__file__))
kb = {'version': '2026-11-07', 'categories': [T, D, F], 'entries': E}
json.dump(kb, open(os.path.join(here, 'apparel-kb.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def q(x): return "'" + str(x).replace("'", "''") + "'"
def arr(xs): return "ARRAY[" + ",".join(q(x) for x in xs) + "]::text[]" if xs else "'{}'::text[]"
def js(x): return q(json.dumps(x, ensure_ascii=False)) + "::jsonb"
sql = ["""-- ฐานความจำระบบดีล (เสื้อผ้าวินเทจ) — รันใน Supabase SQL Editor ได้ทั้งไฟล์ รันซ้ำได้
create table if not exists public.knowledge (
  id text primary key,
  category text not null,
  kind text not null,              -- rule | tag | genre | brand | market | trend
  brand text,
  title text not null,
  era text,
  keywords text[] default '{}',
  cues jsonb default '[]',
  red_flags jsonb default '[]',
  value_notes text,
  confidence text default 'sourced', -- sourced | general | user
  sources jsonb default '[]',
  updated_at timestamptz default now()
);
create index if not exists knowledge_category_idx on public.knowledge (category);
create index if not exists knowledge_keywords_idx on public.knowledge using gin (keywords);
alter table public.knowledge enable row level security;  -- ให้ Worker อ่าน/เขียนด้วย service key เท่านั้น
"""]
for e in E:
    sql.append("insert into public.knowledge (id,category,kind,brand,title,era,keywords,cues,red_flags,value_notes,confidence,sources) values ("
               + ",".join([q(e['id']), q(e['category']), q(e['kind']), q(e['brand']), q(e['title']), q(e['era']), arr(e['keywords']),
                           js(e['cues']), js(e['red_flags']), q(e['value_notes']), q(e['confidence']), js(e['sources'])])
               + ") on conflict (id) do update set category=excluded.category,kind=excluded.kind,brand=excluded.brand,title=excluded.title,era=excluded.era,"
               "keywords=excluded.keywords,cues=excluded.cues,red_flags=excluded.red_flags,value_notes=excluded.value_notes,confidence=excluded.confidence,sources=excluded.sources,updated_at=now();")
os.makedirs(os.path.join(here, '..', 'supabase'), exist_ok=True)
open(os.path.join(here, '..', 'supabase', 'knowledge.sql'), 'w', encoding='utf-8').write("\n".join(sql) + "\n")
print(len(E), 'entries')
