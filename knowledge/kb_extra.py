# -*- coding: utf-8 -*-
# ฐานความรู้ชุดเสริม (พ.ย. 2026) — ถูก exec จาก build_kb.py (ใช้ add / S จากไฟล์นั้น)
# conf='sourced' = มีแหล่งอ้างอิงที่ตรวจแล้ว, 'general' = ความรู้ทั่วไปในวงการ ยังไม่ได้ยืนยันกับแหล่งเฉพาะ (AI จะใช้แบบระวัง)
S.update({
 'usf_nike': 'https://urbanstylefootwear.com/check-nike-authenticity/',
 'legit_dunk': 'https://legitcheck.app/guides/nike/dunk/real-vs-fake-dunk-universal/',
 'madkicks_j1': 'https://madkicks.com/blog/how-to-spot-fake-jordan-1s-real-vs-fake-guide',
 'chucks': 'https://chucksconnection.com/vintage.html',
 'nb_origin': 'https://truthinadvertising.org/evidence/newbalance-origin-information/',
 'tw_milwaukee': 'https://www.techwalls.com/fake-vs-genuine-milwaukee-m18-battery-differences',
 'sg_dewalt': 'https://www.slashgear.com/1923409/how-tell-dewalt-batteries-real-fake-knock-off-warning-signs-guide',
 'gj_m18': 'https://www.garagejournal.com/forum/threads/the-fake-milwaukee-m18-battery-thread.528520/',
 'lv_codes': 'https://lollipuff.com/louis-vuitton-date-code-guide',
 'lv_chip': 'https://collectorscage.com/blogs/authentication/louis-vuitton-date-code-vs-microchip-the-complete-buyers-guide-to-auth',
 'coach_sn': 'https://blog.shopgoodwill.com/english/coach-purse-serial-number-guide',
 'gshock': 'https://www.gshockmod.com/how-to-spot-fake-g-shock-ultimate-authentication-guide-for-all-models',
 'seiko_cb': 'https://www.plus9time.com/seiko-case-back-information?rq=Serial',
 'seiko_feiko': 'https://www.namokimods.com/blogs/namokitimes/how-to-spot-a-feiko-pay-attention-to-these-9-things',
 'rolex_1916': 'https://www.the1916company.com/blog/spotting-fake-rolex-watches.html',
 'apple_used': 'https://support.apple.com/en-gb/104999',
 'peta_film': 'https://petapixel.com/tips-buying-used-film-camera-lens/',
 'lomo_check': 'https://www.lomography.com/school/fa-ame1kpeg',
 'pts_ps': 'https://www.photographytalk.com/why-are-point-and-shoot-film-cameras-so-expensive-now/',
 'vinyl_grade': 'https://www.mylegendvinyl.co.uk/blogs/news/record-grading',
 'poke_fake': 'https://blog.shopgoodwill.com/english/how-to-tell-if-a-pokemon-card-is-fake',
 'truss_pata': 'https://trussarchive.com/guides/how-to-identify-patagonia',
 'truss_date': 'https://trussarchive.com/guides/how-to-date-vintage-clothing',
 'omega_m65': 'https://omegamilitaria.com/blogs/reference-guides/the-ultimate-visual-buyers-guide-to-the-m65-field-jacket',
 'legit_supreme': 'https://legitcheck.app/guides/supreme/fake-vs-real-supreme-general/',
 'flow_fee': 'https://flowaccount.com/blog/commission-fees-ecommerce-shopee-lazada-tiktok/',
})
SH, TL, LX, PH, GN = 'shoes.brand', 'tools.power', 'luxury', 'phone', 'generic'

# ====================== รองเท้า ======================
add('shoe-nike-sku', SH, 'rule', 'Nike/Jordan: เช็ครหัสสินค้า (style code)', brand='Nike',
    keywords=['nike', 'jordan', 'air max', 'air force', 'dunk', 'style code', 'sku'],
    cues=['ป้ายในลิ้นมีรหัส 6 ตัว-3 ตัว เช่น CW2288-111 (ตัวหลังคือรหัสสี)', 'รหัสในลิ้นต้องตรงกับป้ายกล่องทุกตัว',
          'เอารหัสไปค้น Google ต้องขึ้นรุ่นและสีเดียวกับรองเท้าที่ถือ', 'ช่วงวันผลิตบนป้ายต้องสมเหตุสมผลกับปีที่รุ่นนั้นวางขาย'],
    red_flags=['รหัสค้นแล้วขึ้นรุ่นหรือสีอื่น', 'ไม่มีรหัส หรือรหัสในลิ้นกับกล่องไม่ตรงกัน', 'ราคาต่ำกว่าป้ายมาก (ของปลอมเกรดดีมักตั้ง 40–60% ของราคาป้าย)'],
    src=['usf_nike'])
add('shoe-build', SH, 'rule', 'รองเท้าแบรนด์: ดูงานประกอบ', keywords=['sneaker', 'รองเท้า', 'glue', 'stitching'],
    cues=['ตะเข็บถี่ เท่ากัน เส้นตรง', 'แนวกาวระหว่างตัวรองเท้ากับพื้นเรียบ ไม่ล้น', 'บีบส้นด้านหลัง (heel counter) ต้องแข็ง ไม่ยุบแบน',
          'กดโฟมพื้นต้องเด้งกลับทันที', 'กลิ่นหนัง/ยาง/กาวโรงงานปกติ'],
    red_flags=['กาวล้นเป็นก้อนหรือมีช่องว่างไม่มีกาว', 'กลิ่นสารเคมีแรงแบบทินเนอร์', 'ฝีเข็มห่าง ด้ายหลุดลุ่ย'], src=['usf_nike'])
add('shoe-dunk-j1', SH, 'brand', 'Nike Dunk / Air Jordan 1: จุดที่ของปลอมพลาดบ่อย', brand='Nike',
    keywords=['dunk', 'jordan 1', 'aj1', 'panda'],
    cues=['ทรงส้นเท้าด้านหลังเป็นทรงนาฬิกาทราย (เว้าตรงกลาง)', 'โลโก้ Swoosh ปลายแหลมคม วางตำแหน่งตามรุ่น', 'ปักโลโก้ที่ลิ้นแน่น ตัวอักษรไม่ติดกัน',
          'ป้ายในลิ้นพิมพ์คม ฟอนต์ไม่หนา'],
    red_flags=['ส้นตรงทื่อไม่มีเว้า', 'หนังแข็งมันวาวแบบพลาสติก', 'รู้กันว่ารุ่น Panda ปลอมเยอะที่สุดในตลาด ต้องเช็คละเอียด'],
    value='Dunk Panda มือสองสภาพดีขายง่ายแต่ราคาไม่สูง; รุ่นคอลแลบ/สีหายากราคาดีกว่ามาก', src=['legit_dunk', 'madkicks_j1'])
add('shoe-converse-usa', SH, 'brand', 'Converse Chuck Taylor ผลิตในอเมริกา (วินเทจ)', brand='Converse', era='ก่อนราวปี 2001',
    keywords=['converse', 'chuck taylor', 'all star', 'made in usa'],
    cues=['ป้ายส้นวงกลมสีน้ำเงิน: ดาวใหญ่สีขาว + "Made in U.S.A." ล่างซ้าย ลายเซ็น Chuck Taylor ล่างขวา', 'ด้านในลิ้นมีป้ายชื่อ + ช่อง "Players Name"',
          'หัวยางเล็กกว่ารุ่นปัจจุบัน รูร้อยเชือกห่างกว่า', 'เส้นยางขอบพื้นหนากว่าเล็กน้อย'],
    red_flags=['รุ่นใหม่ป้ายส้นมีเครื่องหมาย ® และตัวอักษร ALL STAR ใหญ่', 'Chuck 70 (ผลิตใหม่) หน้าตาคล้ายวินเทจแต่ไม่ใช่ของเก่า'],
    value='คู่ Made in USA สภาพดีราคาสูงกว่า Chuck 70 หลายเท่า; ไซส์ใหญ่และสีหายากขายง่าย', src=['chucks'])
add('shoe-nb-made', SH, 'brand', 'New Balance Made in USA / Made in UK', brand='New Balance',
    keywords=['new balance', 'nb', '990', '992', '993', '991', '1500', 'made in usa', 'made in uk'],
    cues=['รุ่นผลิตในอเมริกา/อังกฤษเขียนประเทศชัดบนลิ้นหรือป้ายใน (MADE IN USA / MADE IN ENGLAND)', 'ราคาป้ายสูงกว่ารุ่นผลิตในเอเชียมาก',
          'New Balance ระบุว่ารุ่น "Made in USA" มีส่วนผลิตในอเมริกาอย่างน้อย 70% ของมูลค่า'],
    red_flags=['ผู้ขายอ้าง Made in USA แต่ป้ายเขียนประเทศอื่น'], value='99x ซีรีส์มือสองมีตลาดในไทย ราคาขึ้นกับไซส์และสภาพพื้น', src=['nb_origin'])
add('shoe-onitsuka', SH, 'brand', 'Onitsuka Tiger / ASICS', brand='Onitsuka Tiger', keywords=['onitsuka', 'mexico 66', 'asics', 'tiger'],
    cues=['ป้ายในมีรหัสรุ่นตรงกับกล่อง (เช่น 1183A201)', 'แถบลายข้าง (Tiger stripes) เย็บเรียบ ปลายเสมอกัน', 'Mexico 66 รุ่น NIPPON MADE ผลิตญี่ปุ่น ราคาสูงกว่ารุ่นปกติ'],
    red_flags=['ของปลอมเยอะมากในไทย ราคาถูกผิดปกติ', 'ฟอนต์บนลิ้นหนา/เบี้ยว'], conf='general')
add('shoe-condition', SH, 'rule', 'ตีราคารองเท้ามือสองตามสภาพ', keywords=['รองเท้ามือสอง', 'ส้นสึก', 'sole', 'yellowing', 'crumbling'],
    cues=['ดูพื้นสึกด้านส้นและหัวแม่เท้า', 'พื้นยางเหลือง (yellowing) ขัดได้บางส่วน', 'รองเท้าเก่ามากพื้นโฟม PU อาจกรอบแตกเมื่อใส่ (crumbling)',
          'มีกล่องเดิม + ป้ายครบ เพิ่มราคาได้ชัด', 'ไซส์ยอดนิยมผู้ชาย US 8.5–10 ขายเร็วสุด'],
    red_flags=['พื้นแยก/กาวหลุด ต้องส่งซ่อมก่อนขาย', 'รองเท้าวินเทจพื้นโฟมเก่าอย่าซื้อแพงถ้ายังไม่ได้ลองกด'], conf='general')

# ====================== เครื่องมือช่าง ======================
add('tool-milwaukee', TL, 'brand', 'Milwaukee M12/M18: แบตปลอม', brand='Milwaukee', keywords=['milwaukee', 'm18', 'm12', 'redlithium'],
    cues=['ของแท้น้ำหนักแน่น ของปลอมเบากว่าชัดเจน', 'ไฟบอกระดับแบตติดไล่ทีละดวงและสว่าง', 'ฉลากคม โลโก้ตรงกลาง สีแดง-ดำสม่ำเสมอ',
          'มี serial พิมพ์ตรงชัดเจน', 'ขั้วต่อเรียบ เนียน งานกลึงดี'],
    red_flags=['ไฟบอกระดับติดพร้อมกันทุกดวงหรือหรี่', 'ไม่มี serial หรือพิมพ์เบี้ยว', 'ตะเข็บบอดี้หยาบ พลาสติกบาง', 'แพ็กเกจกระดาษแข็งแทนแพ็กพลาสติกใส'],
    src=['tw_milwaukee', 'gj_m18'])
add('tool-dewalt', TL, 'brand', 'DeWalt 20V/18V: แบตปลอม', brand='DeWalt', keywords=['dewalt', '20v', 'flexvolt', 'xr'],
    cues=['ใส่กับเครื่องแท้แล้วล็อกแน่นพอดี', 'น็อตยึดบอดี้เป็นสีเงินหัวโดม (ตามที่ DeWalt ระบุ)', 'ฟอนต์และสติกเกอร์ตรงกับของแท้ ไม่มีคำสะกดผิด',
          'มี serial/date code ให้สอบถาม DeWalt ได้'],
    red_flags=['ใส่หลวมหรือฝืด', 'น็อตสีดำหรือหัวแบน', 'สะกดผิดบนฉลาก', 'ใช้งานได้สั้นผิดปกติ'], src=['sg_dewalt'])
add('tool-makita', TL, 'brand', 'Makita LXT 18V: แบตและตัวเครื่อง', brand='Makita', keywords=['makita', 'lxt', 'bl1860', 'bl1850', 'มากีต้า'],
    cues=['แบตแท้: ใต้แบตมีปลั๊กสีขาวใกล้ด้านหน้า กดปุ่มปลดเห็นแถบแดงด้านใน', 'แบตแท้มีไฟบอกระดับ 4 ดวง (รุ่นมีดาว = มีชิปสื่อสารกับแท่นชาร์จ)',
          'เพลทใต้เครื่องมีรุ่น + serial ชัด', 'เครื่องรุ่นมอเตอร์ไร้แปรงถ่านมีคำว่า Brushless/BL'],
    red_flags=['แบต "6.0Ah" ราคาถูกมากแต่เบา = ใส่เซลล์น้อย', 'เพลทถูกขูด'], value='ในไทยขายง่ายที่สุดในหมวดเครื่องมือ; เครื่องเปล่า (ไม่มีแบต) ราคาต่ำกว่าชุดพร้อมแบตมาก',
    conf='general')
add('tool-bosch-hikoki', TL, 'brand', 'Bosch (เขียว vs น้ำเงิน) / HiKOKI (Hitachi)', keywords=['bosch', 'hikoki', 'hitachi', 'gsr', 'gbh'],
    cues=['Bosch สีน้ำเงิน = รุ่นช่างมืออาชีพ, สีเขียว = รุ่นใช้ในบ้าน ราคาต่างกันมาก', 'HiKOKI คือชื่อใหม่ของ Hitachi Power Tools (เปลี่ยนชื่อปี 2018)',
          'รุ่นเก่าที่เขียน Hitachi ยังหาอะไหล่ได้'],
    red_flags=['ขายรุ่นสีเขียวในราคารุ่นสีน้ำเงิน'], conf='general')
add('tool-test', TL, 'rule', 'ทดสอบเครื่องมือไฟฟ้ามือสองก่อนซื้อ', keywords=['สว่าน', 'drill', 'grinder', 'หินเจียร', 'เครื่องมือ'],
    cues=['ขอเสียบปลั๊ก/ใส่แบตลองเดินเครื่องทุกสปีด', 'ฟังเสียงลูกปืน: หอนหรือแตก = ต้องเปลี่ยน', 'ดูช่องระบายลม: ประกายไฟมากผิดปกติ = แปรงถ่าน/ทุ่นเสีย',
          'หัวจับดอก (chuck) หมุนตรงไม่ส่าย', 'ดมกลิ่นไหม้ (ขดลวดเคยร้อนจัด)', 'แบต: ถามรอบชาร์จ ดูว่าบวมไหม'],
    red_flags=['ไม่ให้ลองเครื่อง', 'บอดี้ร้าวใกล้ด้ามจับ', 'แบตบวม = อันตราย ห้ามซื้อ'], conf='general')

# ====================== กระเป๋า/นาฬิกาแบรนด์เนม ======================
add('lux-lv-datecode', LX, 'brand', 'Louis Vuitton: date code และไมโครชิป', brand='Louis Vuitton',
    keywords=['louis vuitton', 'lv', 'monogram', 'damier', 'neverfull', 'speedy', 'date code'],
    cues=['ยุค 80 ต้น: ตัวเลข 3–4 หลัก (ปี+เดือน)', 'ราว 1990–2006: อักษร 2 ตัว (โรงงาน/ประเทศ) + ตัวเลข 4 หลัก หลักที่ 1,3 = เดือน หลักที่ 2,4 = ปี',
          'ราว 2007–ต้นปี 2021: อักษร 2 ตัว + ตัวเลข 4 หลัก หลักที่ 1,3 = สัปดาห์ หลักที่ 2,4 = ปี', 'ตั้งแต่ราวมีนาคม 2021 เลิก date code ใช้ไมโครชิป NFC ฝังในตัวกระเป๋า (สแกนเองไม่ได้)',
          'date code ไม่ใช่ serial: กระเป๋าหลายใบมีรหัสเดียวกันได้'],
    red_flags=['รหัสบอกปีที่รุ่นนั้นยังไม่ผลิต', 'เลขสัปดาห์เกิน 53 หรือเดือนเกิน 12', 'กระเป๋าผลิตหลัง 2021 แต่มี date code', 'ลายโมโนแกรมถูกตัดกลับหัวด้านหลัง (Speedy/Keepall บางรุ่นเป็นปกติ ต้องเช็คตามรุ่น)'],
    value='ซื้อแบรนด์เนมมือสองให้ใช้บริการตรวจแท้ก่อนขายเสมอ', src=['lv_codes', 'lv_chip'])
add('lux-coach', LX, 'brand', 'Coach: แผ่นหนัง creed และเลข serial', brand='Coach', keywords=['coach', 'creed', 'signature c'],
    cues=['ยุค 70–80: ตัวเลขล้วน', 'ราว 1994–ต้นยุค 2000: อักษร(เดือน)+ตัวเลข(ปี)+อักษร(โรงงาน)-เลขรุ่น 4 หลัก เช่น K8P-9870 = ต.ค. 1998',
          'ราว 2014–2016: แผ่น creed ว่าง เลขรุ่นย้ายไปป้ายผ้าขาวเล็กๆ ด้านใน', 'หลัง 2014: อักษร 1 ตัว + 4 หลัก - 5 หลัก; ขึ้นต้น F = รุ่น Outlet',
          'ลาย C ต้องต่อกันตรงตะเข็บ (ใบเต็ม)'],
    red_flags=['รหัสบอกปีไม่ตรงกับทรงกระเป๋า', 'หนังบาง อะไหล่เบา', 'โลโก้เบี้ยว เย็บไม่เท่ากัน'],
    value='Coach วินเทจ (หนังวัวล้วน ยุค 80–90 ผลิตอเมริกา) มีตลาดสะสม ราคาสูงกว่า Coach Outlet', src=['coach_sn'])
add('lux-general', LX, 'rule', 'แบรนด์เนม: กฎซื้อขายมือสองในไทย', keywords=['แบรนด์เนม', 'chanel', 'gucci', 'prada', 'hermes', 'ysl', 'dior'],
    cues=['ห้ามตัดสินว่าแท้จากรูปอย่างเดียว ส่งตรวจกับบริการตรวจแท้ก่อนขาย', 'ขอใบเสร็จ/การ์ด/ถุงผ้าเดิม แต่ของพวกนี้ก็ปลอมได้',
          'Chanel รุ่นเก่ามีสติกเกอร์ hologram + การ์ด serial ตรงกัน; ตั้งแต่ราวปลาย 2021 เปลี่ยนเป็นแผ่นโลหะ (microchip) ไม่มีการ์ด'],
    red_flags=['ราคาถูกกว่าตลาดมาก', 'ผู้ขายไม่ยอมให้ส่งตรวจ', 'การ์ด/ใบเสร็จดูใหม่เกินอายุกระเป๋า'], conf='general')
add('watch-gshock', LX, 'brand', 'Casio G-Shock: ของแท้ vs ของปลอม', brand='Casio',
    keywords=['g-shock', 'gshock', 'casio', 'ga-2100', 'dw-5600', 'casioak', 'จีช็อค'],
    cues=['ฝาหลังเลขรุ่นตรงกับตัวเรือน ตัวอักษรสลักลึกคม มี "20 BAR"/"WATER RESIST 200M"', 'เลขโมดูล (ตัวเลขในกรอบบนฝาหลัง) ต้องตรงกับรุ่น ค้นเทียบกับเว็บ Casio ได้',
          'ไฟส่องสว่างทั่วหน้าปัด ตัวเลขคม', 'ปุ่มกดแน่นมีคลิก', 'ขอบ bezel แนบสนิท สายยางนิ่มไม่แข็ง'],
    red_flags=['เบากว่าสเปก', 'ไฟหรี่/ไม่ทั่ว', 'ปุ่มนิ่มหลวม', 'ขอบมีช่องว่าง กระจกเป็นคลื่น'],
    value='G-Shock ปลอมเยอะมากในตลาดนัดไทย ราคาต่ำกว่าครึ่งของป้ายมักเป็นของปลอม; รุ่นลิมิเต็ด/คอลแลบมีตลาดสะสม',
    src=['gshock'])
add('watch-seiko', LX, 'brand', 'Seiko วินเทจ: อ่านฝาหลังและเช็คหน้าปัดเปลี่ยน', brand='Seiko',
    keywords=['seiko', 'seiko 5', 'skx', 'presage', 'king seiko', 'grand seiko', 'ไซโก้'],
    cues=['ฝาหลังมีรหัสกลไก-ตัวเรือน เช่น 6309-7040 (4 หลักแรก = กลไก)', 'serial หลักแรก = ปี (หลักสุดท้ายของปี) หลักที่ 2 = เดือน (1–9, X/Y/Z หรือ O/N/D = ต.ค.–ธ.ค.)',
          'รหัสบนหน้าปัดใต้หลัก 6 ควรตรงกับรหัสกลไกบนฝาหลัง', 'หน้าปัดยุคเดียวกับกลไก'],
    red_flags=['"franken": ประกอบจากหลายเรือน หน้าปัดพิมพ์ใหม่/ทาสีใหม่ รหัสไม่ตรงกัน', 'ตัวอักษรหน้าปัดหนา เบลอ โลโก้ตำแหน่งผิด', 'Seiko 5 หน้าปัดสีแปลกที่ไม่มีในแคตตาล็อก'],
    value='Seiko วินเทจเดิมทั้งเรือนมีราคากว่าเรือนที่เปลี่ยนชิ้นส่วนมาก', src=['seiko_cb', 'seiko_feiko'])
add('watch-rolex', LX, 'brand', 'Rolex: จุดเช็คเบื้องต้น', brand='Rolex', keywords=['rolex', 'submariner', 'datejust', 'gmt', 'โรเล็กซ์'],
    cues=['เลนส์ขยายวันที่ (cyclops) ขยาย 2.5 เท่า วันที่เต็มกรอบ', 'รุ่นใหม่มีคำ ROLEX สลักวนขอบใน (rehaut) คมชัด',
          'ฝาหลังรุ่นทั่วไปเรียบ ไม่มีลาย/ไม่ใส', 'เข็มวินาทีกวาดลื่น (กลไกอัตโนมัติ) ไม่กระตุกทีละวินาที',
          'สเตนเลสหนักประมาณ 100–160 กรัม', 'รุ่นหลังปี 2002 มีมงกุฎเล็กสลักบนกระจกที่หลัก 6 (มองยาก)'],
    red_flags=['เข็มวินาทีเดินทีละขีด (เว้นรุ่น Oysterquartz)', 'ฝาหลังใสหรือมีลวดลาย', 'เบา', 'วันที่ขยายน้อย'],
    value='Rolex ต้องส่งร้านหรือผู้เชี่ยวชาญเปิดดูกลไกก่อนซื้อขายเสมอ ของปลอมเกรดสูงหลอกตาได้', src=['rolex_1916'])

# ====================== มือถือ ======================
add('phone-iphone', PH, 'rule', 'iPhone มือสอง: เช็คก่อนซื้อ', brand='Apple', keywords=['iphone', 'apple', 'ไอโฟน', 'icloud'],
    cues=['ต้องไม่ติด Activation Lock / iCloud: ถ้าขึ้น "iPhone Locked to Owner" อย่าซื้อ', 'ตั้งค่า > ทั่วไป > เกี่ยวกับ > ประวัติชิ้นส่วนและการซ่อม: "ชิ้นส่วน Apple ของแท้" = แท้, "ไม่ทราบ" = เปลี่ยนชิ้นส่วนไม่แท้/มือสอง',
          'ตั้งค่า > แบตเตอรี่ > สภาพแบตเตอรี่: ดูความจุสูงสุด (ต่ำกว่า 80% ควรเปลี่ยน)', 'เกี่ยวกับ > การล็อกผู้ให้บริการ: "ไม่มีข้อจำกัดซิม" = ใช้ได้ทุกเครือข่าย',
          'ทดสอบปุ่ม ลำโพง ไมค์ (อัดเสียง) กล้องทุกตัว Face ID/Touch ID'],
    red_flags=['ผู้ขายไม่ยอมลบเครื่อง/ออกจาก iCloud ต่อหน้า', 'จอ "ไม่ทราบ" = เปลี่ยนจอเทียม สีเพี้ยน', 'เครื่องติดล็อก MDM ของบริษัท', 'ราคาถูกผิดปกติ = เครื่องหาย/ติดล็อก'],
    src=['apple_used'])
add('phone-android', PH, 'rule', 'Android มือสอง: เช็คก่อนซื้อ', keywords=['samsung', 'android', 'oppo', 'vivo', 'xiaomi', 'google pixel'],
    cues=['ต้องออกจากบัญชี Google แล้ว (ไม่งั้นติด FRP lock หลังรีเซ็ต)', 'กด *#06# ดู IMEI ให้ตรงกับกล่อง/ถาดซิม', 'Samsung: เช็ค Knox/ล็อกบริษัท',
          'เปิดจอสีขาวล้วนดูจุดไหม้ (burn-in) ของจอ OLED'],
    red_flags=['IMEI ไม่ตรงกล่อง', 'ติดบัญชีเจ้าของเดิม', 'จอมีเงาภาพค้าง'], conf='general')

# ====================== ของสะสม / ทั่วไป ======================
add('cam-film-check', GN, 'rule', 'กล้องฟิล์มมือสอง: เช็คก่อนซื้อ', keywords=['กล้องฟิล์ม', 'film camera', 'กล้อง', 'canon ae-1', 'nikon fm2', 'pentax', 'olympus'],
    cues=['ขึ้นชัตเตอร์แล้วกดหลายครั้ง ม่านต้องเปิด-ปิดสุด ไม่ค้าง', 'ลองทุกสปีด เสียงต้องต่างกันชัด; โหมด B ปล่อยปุ่มแล้วปิดทันที',
          'เปิดฝาหลังดูซีลยาง/โฟมกันแสง: เป็นผงดำเหนียว = ต้องเปลี่ยนซีล (ราคาไม่แพง แต่ต้องบอกในประกาศ)', 'ช่องถ่าน: คราบเขียว/ฟ้า = ถ่านรั่ว อาจวงจรเสีย',
          'วัดแสงต้องเปลี่ยนค่าเมื่อหันไปที่มืด/สว่าง', 'บุบที่หัว pentaprism = เคยตก'],
    red_flags=['กลิ่นอับชื้น/สนิมตามขอบฝา = เก็บในที่ชื้น', 'ม่านชัตเตอร์ยับ/ใบมีดมีน้ำมัน'], src=['peta_film', 'lomo_check'])
add('cam-lens', GN, 'rule', 'เลนส์มือสอง: รา ฝ้า ฝุ่น', keywords=['เลนส์', 'lens', 'รา', 'ฝ้า', 'fungus', 'haze'],
    cues=['ส่องไฟฉายผ่านเลนส์จากด้านหลัง ดูทั้งหน้าและหลัง', 'รา = เส้นใยคล้ายใยแมงมุม มักเริ่มที่ขอบ', 'ฝ้า = ภาพมัวขาวทั่วชิ้นเลนส์',
          'ฝุ่นเล็กน้อยไม่กระทบภาพ ไม่ต้องลดราคามาก', 'ม่านรูรับแสงต้องแห้ง ไม่มีน้ำมัน หุบ-กางไว', 'แหวนโฟกัสหมุนลื่น ไม่ฝืดไม่ครูด'],
    red_flags=['ราเยอะ/ฝ้าหนา ทำความสะอาดแพงหรือไม่หาย', 'รอยขีดลึกที่เลนส์หน้า'], src=['peta_film'])
add('cam-pointshoot', GN, 'trend', 'กล้องฟิล์มคอมแพกต์: ราคาพุ่ง', keywords=['point and shoot', 'คอมแพกต์', 'mju', 'contax t2', 'ricoh gr1', 'olympus mju', 'klasse', 'big mini'],
    cues=['กล้องคอมแพกต์เลนส์ดี (Contax T2/T3, Ricoh GR1, Olympus mju-II, Fuji Klasse, Konica Big Mini) ราคาสูงขึ้นมากจากกระแสฟิล์ม',
          'กล้องคอมแพกต์ระบบอิเล็กทรอนิกส์ซ่อมยาก อะไหล่หายาก เช็คให้ใช้งานได้จริงก่อนซื้อ', 'ลองใส่ถ่าน กดเปิด ดูเลนส์ยืดออก แฟลชทำงาน จอ LCD ไม่ซีด'],
    red_flags=['จอ LCD ตัวเลขขาด', 'เลนส์ยืดออกไม่สุด/มีเสียงขูด', 'ขาย "ไม่ได้เทส" ราคาเต็ม'],
    value='ตลาดนัด/กระสอบญี่ปุ่นในไทยยังเจอกล้องคอมแพกต์ราคาถูก ขายต่อในกลุ่มกล้องฟิล์ม Facebook ได้ราคาดี', src=['pts_ps'])
add('vinyl-grade', GN, 'rule', 'แผ่นเสียง: เกรดสภาพ (Goldmine)', keywords=['แผ่นเสียง', 'vinyl', 'record', 'lp', 'goldmine'],
    cues=['M (Mint) = ใหม่ไม่เคยเล่น, NM = เกือบใหม่, VG+ = มีรอยบางๆ ไม่มีเสียงรบกวน, VG = มีเสียงแตกเบาๆ, G = เสียงรบกวนชัด',
          'เกรดแผ่นและปกแยกกัน', 'ส่องไฟดูรอยขีด ลองฟังถ้าทำได้', 'ดูแผ่นบิด (warp) วางบนโต๊ะแล้วดูขอบ',
          'ข้อความในวงใกล้ป้ายกลาง (matrix/runout) ใช้ระบุว่าเป็นแผ่นพิมพ์ครั้งแรกหรือไม่'],
    red_flags=['แผ่นบิดมาก', 'รอยขีดลึกถึงเล็บสะดุด', 'ปกขึ้นราหรือน้ำท่วม'], value='แผ่นพิมพ์ครั้งแรก (first press) และแผ่นไทยเก่า (ลูกทุ่ง/สตริงยุค 70–80) มีตลาดสะสม',
    src=['vinyl_grade'])
add('cards-pokemon', GN, 'rule', 'การ์ดโปเกมอน: ของแท้ vs ของปลอม', keywords=['pokemon', 'โปเกมอน', 'การ์ด', 'tcg', 'pokémon card'],
    cues=['ส่องไฟฉายผ่านการ์ด: ของแท้มีชั้นสีดำกลางเนื้อการ์ด แสงผ่านน้อย', 'ด้านหลังสีน้ำเงินเข้มไล่เฉด ไม่ซีด ไม่ม่วงจัด',
          'ฟอนต์และสัญลักษณ์ธาตุถูกต้อง ไม่สะกดผิด', 'ผิวการ์ดด้านเรียบ ไม่มันวาวแบบพลาสติก', 'เทียบความหนา/น้ำหนักกับการ์ดแท้'],
    red_flags=['สะกดผิด/ค่า HP แปลก', 'การ์ดฟอยล์ทั้งใบในชุดที่ไม่มี', 'ขายเป็นกองราคาถูกมาก'],
    value='การ์ดเกรด (PSA/BGS) ราคาสูงกว่าการ์ดดิบมาก; ภาษาญี่ปุ่น/อังกฤษราคาต่างกัน', src=['poke_fake'])
add('toys-gunpla', GN, 'genre', 'ของเล่น/ฟิกเกอร์/กันพลา', keywords=['gundam', 'กันพลา', 'figure', 'ฟิกเกอร์', 'bandai', 'tamiya', 'lego', 'hot wheels'],
    cues=['ของในกล่องไม่แกะ (MISB) ราคาสูงกว่าแกะแล้วมาก', 'Bandai แท้มีสติกเกอร์โฮโลแกรม/ตราบนกล่อง', 'ฟิกเกอร์ญี่ปุ่นแท้มีสติกเกอร์ตัวแทนจำหน่าย ข้อความญี่ปุ่นบนกล่องพิมพ์คม',
          'เลโก้: ดูโลโก้ LEGO บนปุ่มตัวต่อทุกปุ่ม'],
    red_flags=['ฟิกเกอร์ราคาถูกมาก สีเลอะ ข้อต่อหลวม = ของ bootleg', 'กล่องพิมพ์สีซีด ฟอนต์เพี้ยน'], conf='general')
add('game-retro', GN, 'genre', 'เกมและเครื่องเล่นเกมเก่า', keywords=['famicom', 'nintendo', 'game boy', 'playstation', 'ps1', 'ps2', 'ตลับเกม', 'sega'],
    cues=['ตลับ Nintendo แท้: ป้ายมีรหัส เช่น DMG-, น็อตหัวพิเศษ (gamebit), แผงวงจรมีโลโก้ Nintendo', 'ลองเสียบเล่นจริงก่อนซื้อ',
          'ตลับ Game Boy Color/Advance เกมที่เซฟได้ใช้ถ่านกระดุม อาจหมด'],
    red_flags=['ตลับเบาผิดปกติ ป้ายพิมพ์มัน/สีเพี้ยน (ของก๊อป)', 'Pokémon ตลับ GBA ปลอมเยอะมาก'], conf='general')
add('thai-sell-fees', GN, 'market', 'ค่าธรรมเนียมขายออนไลน์ในไทย (คำนวณกำไร)', keywords=['shopee', 'lazada', 'tiktok shop', 'ค่าธรรมเนียม', 'ขาย'],
    cues=['ทุกแพลตฟอร์มหักค่าคอมมิชชันตามหมวด + ค่าธุรกรรม/ชำระเงิน รวมราว 8–15% ของราคาขายสำหรับร้านทั่วไป (เช็คตัวเลขล่าสุดก่อนตั้งราคา)',
          'Facebook Marketplace/กลุ่ม ไม่มีค่าธรรมเนียม แต่ต้องจัดการโอน/ส่งเอง', 'คิดค่าส่ง ค่ากล่อง และเวลาที่ใช้ด้วย'],
    red_flags=['ตั้งราคาโดยไม่หักค่าธรรมเนียม ทำให้กำไรจริงหายไป'], src=['flow_fee'], conf='general')
add('thai-markets', GN, 'market', 'แหล่งซื้อของมือสองในไทย', keywords=['ตลาดนัด', 'คลองถม', 'จตุจักร', 'ตลาดรถไฟ', 'กระสอบ', 'โรงเกลือ'],
    cues=['ตลาดโรงเกลือ (สระแก้ว) = แหล่งเสื้อผ้ากระสอบใหญ่ เช้ามืดของดีหมดก่อน', 'คลองถม/วงเวียน 22 = เครื่องมือ อิเล็กทรอนิกส์ ของจิปาถะ',
          'ร้านมือสองญี่ปุ่น (ของจากกระสอบญี่ปุ่น) = กล้อง ของเล่น เครื่องครัว เสื้อผ้าแบรนด์ญี่ปุ่น', 'ไปเช้า พกเงินสดย่อย ไฟฉาย และตลับเมตร'],
    red_flags=['ซื้อตามอารมณ์โดยไม่สแกนเช็คราคาก่อน', 'ต่อรองหลังรู้ว่ามีตำหนิ ไม่ใช่ก่อน'], conf='general')

# ====================== เสริม: เสื้อผ้าวินเทจ ======================
add('brand-patagonia', T, 'brand', 'Patagonia วินเทจ', brand='Patagonia', keywords=['patagonia', 'synchilla', 'retro-x', 'snap-t', 'baggies'],
    cues=['ตั้งแต่ปี 1988 ป้ายในมีรหัสรุ่น + รหัสฤดู/ปี เช่น S9 (ต้องดูแบบป้ายประกอบว่า 1989 หรือ 1999)', 'ตั้งแต่ปี 1995 มีรหัสสี 3–4 ตัวอักษรบนป้าย',
          'ทุกตัวมี RN51884', 'ก่อน 1986 ระบุปีจากรหัสไม่ได้ ดูแบบป้ายคอแทน'],
    red_flags=['รหัสรุ่นค้นแล้วไม่ตรงกับตัวเสื้อ', 'คุณภาพงานเย็บหยาบ ลาย/โลโก้เพี้ยน'],
    value='Snap-T, Retro-X, Synchilla ยุค 80–90 ผลิตอเมริกา ราคาดีในกลุ่มเอาท์ดอร์วินเทจ', src=['truss_pata'])
add('brand-tnf', T, 'brand', 'The North Face วินเทจ', brand='The North Face', keywords=['north face', 'tnf', 'nuptse', 'mountain jacket', 'gore-tex'],
    cues=['ป้ายยุค 70–80: ป้ายน้ำตาล/ครีมลายเส้นขอบ', 'ยุค 90: ป้ายดำโลโก้ขาว ตามด้วยป้ายรุ่น Summit Series/Steep Tech', 'Nuptse 1996 ดั้งเดิม ราคาสูงสุดในกลุ่มขนเป็ด',
          'รุ่นมี Gore-Tex มีป้าย Gore-Tex แยก'],
    red_flags=['TNF ปลอมเยอะมาก: ปักโลโก้หนา ซิปไม่มียี่ห้อ YKK', 'ขนเป็ดยุบเป็นก้อน/มีกลิ่น'], conf='general')
add('brand-polo-rl', T, 'brand', 'Polo Ralph Lauren วินเทจ', brand='Ralph Lauren', keywords=['polo ralph lauren', 'ralph lauren', 'polo sport', 'rrl', 'polo bear', 'snow beach'],
    cues=['ม้าปักต้องละเอียด เห็นขาม้า ไม้โปโล และคนขี่ชัด', 'ป้ายยุค 80–90 ป้ายน้ำเงินกรมท่าปักขาว "Polo by Ralph Lauren"',
          'รุ่นสะสม: Polo Bear, Snow Beach, Stadium 1992, Polo Sport, CP-93, P-Wing'],
    red_flags=['ม้าเป็นก้อน ไม่มีรายละเอียด', 'กระดุมพลาสติกบางไม่มีโลโก้ (บางรุ่น)', 'ป้ายพิมพ์แทนการทอ'],
    value='เสื้อเชิ้ต/โปโลธรรมดาราคากลาง ๆ; ชิ้นสะสม (Stadium, Snow Beach, Polo Bear) ราคาหลักหมื่นขึ้น', conf='general')
add('brand-military', D, 'genre', 'แจ็คเก็ตทหารอเมริกา (M-65, MA-1, M-51)', keywords=['m-65', 'm65', 'ma-1', 'ma1', 'm-51', 'field jacket', 'ทหาร', 'military', 'alpha industries'],
    cues=['ของทหารแท้มีป้ายสัญญา: ชื่อรุ่น, เลขสัญญา DLA/DSA + ปี, NSN (เลขสต็อก 13 หลัก)', 'ปีในเลขสัญญาบอกปีผลิต เช่น DSA-100-69-... = 1969',
          'M-65 ยุคเวียดนาม (ต้นยุค 70 ลงไป) ราคาสูงกว่ายุค 80', 'MA-1 แบรนด์พลเรือน (Alpha Industries) ไม่มีเลขสัญญา ราคาต่ำกว่าของทหาร'],
    red_flags=['ป้ายสัญญาพิมพ์ใหม่บนเสื้อเก่า', 'ซิปพลาสติกในรุ่นที่ควรเป็นโลหะ'], src=['omega_m65'])
add('brand-streetwear', T, 'brand', 'Stüssy / Supreme', keywords=['stussy', 'supreme', 'box logo', 'bogo', 'streetwear'],
    cues=['Supreme: ฟอนต์ Futura Heavy Oblique ตัวอักษรห่างเท่ากัน ป้ายคอแยกตามยุค', 'Supreme เสื้อยืดยุคแรก (ก่อนราวปี 2009) ผลิตอเมริกา',
          'Stüssy วินเทจ: ป้ายดำลายเซ็นขาว ยุค 80–90 ผลิตอเมริกา (ป้ายสีขาว/ดำ ระบุยุคต่างกัน)'],
    red_flags=['Box logo ตัวอักษรชิดกัน ขอบกล่องไม่คม', 'ป้ายวิธีซักภาษา/ฟอนต์ไม่ตรงยุค'], src=['legit_supreme'], conf='general')
add('genre-hawaiian', T, 'genre', 'เสื้อฮาวาย (Aloha shirt)', keywords=['hawaiian', 'aloha', 'reyn spooner', 'kahala', 'sun surf', 'เสื้อฮาวาย'],
    cues=['ผ้าเรยอน (rayon) ยุค 40–50 ราคาสูงสุด', 'กระเป๋าหน้าต่อลายตรงกับตัวเสื้อ = งานดี', 'กระดุมกะลา/ไม้/ยูเรีย (เก่า) แทนพลาสติก',
          'แบรนด์: Kahala, Duke Kahanamoku, Reyn Spooner (ลายกลับด้านผ้า), Sun Surf/Toyo (ญี่ปุ่นทำใหม่ คุณภาพสูง)'],
    red_flags=['ผ้าโพลีเอสเตอร์ลายพิมพ์ดิจิทัล = ของใหม่', 'ป้าย Made in Hawaii เย็บใหม่'], conf='general')
add('genre-sports-us', T, 'genre', 'เสื้อทีมกีฬาอเมริกัน (NBA/NFL/MLB) วินเทจ', keywords=['nba', 'nfl', 'mlb', 'starter', 'salem', 'logo 7', 'nutmeg', 'champion jersey', 'chalk line'],
    cues=['ป้ายยุค 80–90: Salem Sportswear, Logo 7, Nutmeg Mills, Starter, Chalk Line, Trench', 'แจ็คเก็ต Starter ซาติน/พัฟเวอร์ ยุค 90 ขายดี',
          'เสื้อแชมป์ปีที่ทีมแพ้ (ผลิตไว้ล่วงหน้าแล้วถูกส่งบริจาค) เป็นของแปลกที่นักสะสมชอบ', 'Jersey Champion ยุค 90 มีป้ายขนาดเลขที่ชายเสื้อ'],
    red_flags=['ลายรีด/พิมพ์ใหม่บนเสื้อเก่า', 'ทีม/โลโก้ไม่ตรงกับยุคที่อ้าง'], conf='general')
add('genre-disney', T, 'genre', 'เสื้อ Disney / การ์ตูนวินเทจ', keywords=['disney', 'mickey', 'mickey inc', 'velva sheen', 'looney tunes', 'simpsons'],
    cues=['ป้ายยุคเก่า: Mickey Inc., Mickey & Co., Disney Designs, Velva Sheen', 'ลาย Looney Tunes/Simpsons ยุค 90 มีปี © ใต้ลาย'],
    red_flags=['ป้าย Disney ยุคใหม่ (Disney Parks) ราคาต่ำกว่า'], conf='general')
add('rule-japan-brands', T, 'brand', 'แบรนด์ญี่ปุ่นในกระสอบ (ขายดีในไทย)', keywords=['japan', 'ญี่ปุ่น', 'comme des garcons', 'cdg', 'issey miyake', 'yohji', 'beams', 'kapital', 'visvim', 'neighborhood', 'bape', 'evisu'],
    cues=['แบรนด์ดีไซเนอร์ญี่ปุ่น (Comme des Garçons, Issey Miyake/Pleats Please, Yohji Yamamoto) ราคามือสองสูง', 'Kapital, Visvim, Neighborhood, WTAPS, Bape = สตรีทญี่ปุ่นที่มีตลาด',
          'Evisu ยุค 90 ผลิตญี่ปุ่นมีราคา; รุ่นหลังผลิตจีนราคาต่ำกว่า', 'ป้ายภาษาญี่ปุ่น + บริษัทผู้ผลิตในญี่ปุ่นเป็นสัญญาณดี'],
    red_flags=['Bape/CDG Play ปลอมเยอะมาก (โลโก้หัวใจตาเบี้ยว)'], conf='general')

# ====================== เสริม: ยีนส์ ======================
add('denim-levis-orange', D, 'brand', "Levi's แท็บส้ม / รุ่น 505, 517, 550", brand="Levi's", keywords=['orange tab', 'แท็บส้ม', '505', '517', '550', "levi's"],
    cues=['แท็บส้มใช้กับรุ่นแฟชั่น/ราคาย่อมเยา ยุค 60–90', '505 (ขาตรงซิป), 517 (ขาม้า), 550 (ทรงหลวม) ยุค 80–90 ผลิตอเมริกาเป็นที่ต้องการ',
          'ดูปีจากรหัสป้ายวิธีซักเหมือนรุ่น 501'], red_flags=['แท็บถูกเลาะเปลี่ยน'], conf='general')
add('denim-japan', D, 'brand', 'ยีนส์ญี่ปุ่น (Edwin, Big John, Momotaro, Pure Blue Japan)', keywords=['edwin', 'big john', 'momotaro', 'pure blue japan', 'japan denim', 'samurai'],
    cues=['ผ้าริม (selvedge) ญี่ปุ่นทอเครื่องเก่า ขอบริมเป็นเส้นสี', 'แบรนด์เล็กญี่ปุ่นราคามือสองสูงกว่ายีนส์ทั่วไป', 'Edwin รุ่นผลิตญี่ปุ่น vs ผลิตจีนราคาต่างกันมาก'],
    red_flags=['อ้างผ้าญี่ปุ่นแต่ป้ายผลิตประเทศอื่นไม่ระบุ'], conf='general')
add('denim-size', D, 'rule', 'ยีนส์มือสอง: วัดไซส์จริงก่อนขาย', keywords=['ไซส์ยีนส์', 'เอว', 'waist', 'inseam'],
    cues=['ยีนส์เก่าหดตัว ไซส์บนป้ายไม่ตรงตัวจริง วัดเอวจริงทุกครั้ง (วางราบ x2)', 'บอกเอว ความยาวขาด้านใน สะโพก ปลายขา ในประกาศ',
          'เอวเล็ก (28–32) ขายเร็วกว่าเอวใหญ่'], conf='general')

# ====================== เสริม: เสื้อบอล ======================
add('fb-90s-value', F, 'genre', 'เสื้อบอลยุค 90 ที่ราคาสูง', keywords=['manchester united', 'arsenal', 'liverpool', 'ac milan', 'inter', 'juventus', 'barcelona', 'retro'],
    cues=['ทีมดัง + ฤดูกาลที่ได้แชมป์/มีนักเตะดังราคาสูงสุด', 'ไซส์ M–L ขายง่ายที่สุด เด็ก/XS ราคาต่ำ', 'ชื่อเบอร์ติดมาจากยุคนั้น (ฟอนต์ลีกจริง) เพิ่มราคา; ชื่อรีดใหม่ไม่เพิ่ม',
          'ป้ายห้อยครบ (BNWT) เพิ่มราคามาก'],
    red_flags=['ชื่อเบอร์ทีหลังผิดฟอนต์ยุค', 'รุ่นรีเมค/ย้อนยุคที่ผลิตใหม่ (เช่น Score Draw, retro remake) ไม่ใช่ของเก่า ราคาต่ำกว่า'], conf='general')
add('fb-brands-more', F, 'brand', 'แบรนด์เสื้อบอลยุคเก่าอื่น ๆ', keywords=['diadora', 'lotto', 'le coq sportif', 'hummel', 'puma', 'mizuno', 'asics', 'errea', 'reebok'],
    cues=['Diadora/Lotto/Errea = ทีมอิตาลียุค 90', 'Hummel = เดนมาร์ก/ทีมยุค 80 ลายตารางหมากรุกที่ไหล่', 'Mizuno/Asics/Puma = J-League และทีมชาติญี่ปุ่นยุค 90 มีนักสะสม',
          'เสื้อ J-League ยุคแรก (1993–96) ลายจัด ราคาเริ่มสูง'], conf='general')
add('fb-condition', F, 'rule', 'สภาพเสื้อบอลที่มีผลต่อราคา', keywords=['สภาพเสื้อบอล', 'ขุย', 'pilling', 'ชื่อเบอร์ร่อน'],
    cues=['ขุยตามตัวเสื้อลดราคามาก', 'สปอนเซอร์/ตราสโมสรแบบรีดลอกหรือแตก ลดราคา', 'คราบเหลืองคอเสื้อ', 'เสื้อแข่งจริงที่นักเตะใส่ (match worn) ต้องมีหลักฐาน ไม่งั้นตีเป็นรุ่นนักเตะธรรมดา'],
    red_flags=['ซื้อเสื้อ "match worn" โดยไม่มีใบรับรอง/รูปเทียบ'], conf='general')
