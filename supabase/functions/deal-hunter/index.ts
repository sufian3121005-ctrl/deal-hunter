// =============================================================
//  Deal Hunter — หลังบ้าน (Supabase Edge Function: deal-hunter)
//  URL: https://<project>.supabase.co/functions/v1/deal-hunter
//
//  POST /api/scan            สแกนสินค้า
//  GET  /api/kb              ฐานความจำทั้งหมด (จากตาราง knowledge)
//  GET/POST /api/refs        คลังรูปของแท้ (รูปใน storage bucket "refs")
//  GET  /api/refs/img?key=   ดูรูปอ้างอิง
//  GET/POST /api/mistakes    บันทึกของปลอม/ดีลพลาด
//  GET  /api/deals?since=    ดีลทั้งหมด (ซิงก์ข้ามเครื่อง)
//  POST /api/deals           บันทึก/อัปเดตดีล
//  POST /api/deals/images    เก็บรูปดีล   GET /api/deals/images?id=
//
//  Secrets (Supabase → Edge Functions → Secrets):
//    GEMINI_API_KEY (จำเป็น), APP_KEY (จำเป็น), SERPER_API_KEY (แนะนำ)
//    GEMINI_MODEL, USD_THB, DOUBLE_CHECK_ABOVE (ไม่บังคับ)
//  SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY มีให้อัตโนมัติ
// =============================================================
// @ts-nocheck
import { createClient } from "npm:@supabase/supabase-js@2.45.4";

// ค่าตั้งค่า: อ่านจาก Supabase Secrets ก่อน ถ้าไม่มีอ่านจากตาราง app_config (เข้าถึงได้เฉพาะหลังบ้าน)
let CONFIG = {};
let cfgAt = 0;
async function loadConfig() {
  if (Date.now() - cfgAt < 300000) return;
  const { data } = await db.from('app_config').select('key,value');
  CONFIG = Object.fromEntries((data || []).map(r => [r.key, r.value]));
  cfgAt = Date.now();
}
const env = new Proxy({}, { get: (_, k) => (typeof k === 'string' ? (Deno.env.get(k) || CONFIG[k] || undefined) : undefined) });
const db = createClient(Deno.env.get('SUPABASE_URL'), Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'), { auth: { persistSession: false } });

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

// ฐานความจำ: โหลดจากตาราง knowledge (แคชในหน่วยความจำ 10 นาที)
let KB = [];
let kbAt = 0;
async function loadKB() {
  if (KB.length && Date.now() - kbAt < 600000) return KB;
  const { data, error } = await db.from('knowledge').select('id,category,kind,brand,title,era,keywords,cues,red_flags,value_notes,confidence,sources').order('category').order('kind').order('id');
  if (!error && data) { KB = data.map(e => ({ ...e, keywords: e.keywords || [], cues: e.cues || [], red_flags: e.red_flags || [], sources: e.sources || [] })); kbAt = Date.now(); }
  return KB;
}

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

const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'POST, GET, OPTIONS',
  'access-control-allow-headers': 'content-type, x-app-key, authorization, apikey, x-client-info'
};

Deno.serve(async (req) => {
  const cors = CORS;
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  await loadConfig();
  const url = new URL(req.url);
  // ตัดส่วนหน้า /functions/v1/deal-hunter หรือ /deal-hunter ออก
  let path = url.pathname.replace(/^.*?\/deal-hunter/, '') || '/';
  if (!path.startsWith('/')) path = '/' + path;

  if (path === '/' || path === '/api/health') {
    const { count } = await db.from('knowledge').select('id', { count: 'exact', head: true });
    return json({ ok: true, gemini: !!env.GEMINI_API_KEY, serper: !!env.SERPER_API_KEY, db: true, kb: count || 0, locked: !!env.APP_KEY, model: MODEL_OK || env.GEMINI_MODEL || 'gemini-3.8-flash' }, 200, cors);
  }
  const key = req.headers.get('x-app-key') || url.searchParams.get('k');
  if (!env.APP_KEY) return json({ error: 'ยังไม่ได้ตั้ง APP_KEY' }, 500, cors);
  if (key !== env.APP_KEY) return json({ error: 'รหัสแอปไม่ถูกต้อง' }, 401, cors);

  try {
    if (path === '/api/kb' && req.method === 'GET') return json({ entries: await loadKB() }, 200, cors);
    if (path === '/api/scan' && req.method === 'POST') return json(await scan(env, await req.json()), 200, cors);
    if (path === '/api/refs' && req.method === 'GET') return json(await listRefs(env, url.searchParams.get('category')), 200, cors);
    if (path === '/api/refs' && req.method === 'POST') return json(await addRef(env, await req.json()), 200, cors);
    if (path === '/api/refs/img' && req.method === 'GET') {
      const { data: row } = await db.from('refs').select('path').eq('id', url.searchParams.get('key') || '').maybeSingle();
      if (!row) return json({ error: 'not_found' }, 404, cors);
      const { data: signed } = await db.storage.from('refs').createSignedUrl(row.path, 3600);
      return new Response(null, { status: 302, headers: { location: signed.signedUrl, ...cors } });
    }
    if (path === '/api/mistakes' && req.method === 'POST') return json(await addMistake(env, await req.json()), 200, cors);
    if (path === '/api/mistakes' && req.method === 'GET') return json({ items: await getMistakes(env, url.searchParams.get('category')) }, 200, cors);
    if (path === '/api/deals' && req.method === 'GET') return json(await listDeals(url.searchParams.get('since')), 200, cors);
    if (path === '/api/deals' && req.method === 'POST') return json(await saveDeals(await req.json()), 200, cors);
    if (path === '/api/deals/images' && req.method === 'POST') return json(await saveDealImages(await req.json()), 200, cors);
    if (path === '/api/deals/images' && req.method === 'GET') return json(await getDealImages(url.searchParams.get('id') || ''), 200, cors);
    return json({ error: 'not_found', path }, 404, cors);
  } catch (e) {
    return json({ error: String(e.message || e) }, e.status || 500, cors);
  }
});

// =============================================================
//  SCAN
// =============================================================
async function scan(env, body) {
  if (!env.GEMINI_API_KEY) throw new Error('ยังไม่ได้ตั้ง GEMINI_API_KEY');
  await loadKB();
  const images = (body.images || []).slice(0, 10);
  if (!images.length) { const e = new Error('ไม่มีรูป'); e.status = 400; throw e; }
  const labels = body.labels || [];
  const hint = body.hint || {};

  // known fake patterns (จากที่ผู้ใช้เคยบันทึกว่าพลาด)
  const mistakes = await getMistakes(env, null).catch(() => []);

  // 1) ระบุ + เช็คของแท้ + ตำหนิ + คุณภาพรูป
  const item = await identify(env, images, labels, hint, mistakes);
  const cat = CAT_KEYS.includes(item.category) ? item.category : 'generic';
  item.category = cat;
  const catInfo = CATEGORIES[cat] || CATEGORIES.generic;
  let auth = normalizeAuth(item.auth);
  const notes = [];

  // 2) เทียบกับคลังรูปของแท้ (ถ้ามีในหมวดนี้)
  let refsUsed = 0;
  {
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
    try { const { data } = await db.from('price_cache').select('data').eq('key', cacheKey).gt('expires_at', new Date().toISOString()).maybeSingle(); if (data) cached = data.data; } catch (_e) { /* ignore */ }
    if (cached) market = { ...cached, cached: true };
    else {
      market = await marketPrices(env, item);
      if (market.evidence.length) { try { await db.from('price_cache').upsert({ key: cacheKey, data: market, expires_at: new Date(Date.now() + 7 * 864e5).toISOString() }); } catch (_e) { /* ignore */ } }
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
let MODEL_OK = '';
async function gemini(env, parts, what) {
  // ลองรุ่นที่ตั้งไว้ก่อน ถ้า Google เลิกให้บริการ (404) จะลองรุ่นสำรองให้อัตโนมัติ
  // thinkingLevel=low: รุ่น Gemini 3 ถ้าคิดเต็มที่จะช้าเกินเวลาที่ฟังก์ชันรับได้
  const tries = [...new Set([MODEL_OK, env.GEMINI_MODEL, 'gemini-3.8-flash', 'gemini-3.1-flash-lite', 'gemini-flash-latest'].filter(Boolean))];
  let d, model;
  for (model of tries) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-goog-api-key': env.GEMINI_API_KEY },
        body: JSON.stringify({ contents: [{ parts }], generationConfig: { responseMimeType: 'application/json', temperature: 0.2, thinkingConfig: { thinkingLevel: 'low' } } }),
        signal: AbortSignal.timeout(45000)
      });
      d = await r.json();
    } catch (_e) { d = { error: { code: 504, message: 'AI ตอบช้าเกินไป' } }; continue; }
    if (d.error?.code === 404 || d.error?.code === 400) continue;
    break;
  }
  if (d.error) {
    if (d.error.code === 404) throw new Error(`ไม่พบโมเดล Gemini ที่ใช้ได้ — ตั้ง GEMINI_MODEL ในตาราง app_config`);
    if (d.error.code === 504) throw new Error('AI ตอบช้าเกินไป ลองใหม่อีกครั้ง');
    if (d.error.code === 429) throw new Error('โควตา Gemini ฟรีของวันนี้หมดแล้ว ลองใหม่ภายหลัง');
    throw new Error('Gemini: ' + d.error.message);
  }
  MODEL_OK = model;
  const text = (d.candidates?.[0]?.content?.parts || []).filter(p => !p.thought).map(p => p.text || '').join('');
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
function dataUrlToBytes(dataUrl) {
  const m = /^data:(.+?);base64,(.*)$/.exec(dataUrl || '');
  if (!m) { const e = new Error('รูปไม่ถูกต้อง'); e.status = 400; throw e; }
  return { type: m[1], bytes: Uint8Array.from(atob(m[2]), c => c.charCodeAt(0)) };
}
function bytesToDataUrl(type, buf) {
  const u = new Uint8Array(buf); let s = '';
  for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode(...u.subarray(i, i + 0x8000));
  return `data:${type};base64,${btoa(s)}`;
}
async function addRef(env, b) {
  if (!b.image || !b.category) { const e = new Error('ต้องมี category และ image'); e.status = 400; throw e; }
  const { type, bytes } = dataUrlToBytes(b.image);
  const path = `${b.category}/${uid()}.jpg`;
  const up = await db.storage.from('refs').upload(path, bytes, { contentType: type });
  if (up.error) throw new Error('อัปโหลดรูปไม่สำเร็จ: ' + up.error.message);
  const { data, error } = await db.from('refs').insert({ category: b.category, checkpoint: b.checkpoint || '', note: (b.note || '').slice(0, 120), path }).select('id').single();
  if (error) throw new Error(error.message);
  return { ok: true, key: data.id };
}
async function listRefs(env, category) {
  let q = db.from('refs').select('id,category,checkpoint,note,created_at').order('created_at', { ascending: false }).limit(200);
  if (category) q = q.eq('category', category);
  const { data, error } = await q;
  if (error) throw new Error(error.message);
  return { items: (data || []).map(r => ({ key: r.id, category: r.category, checkpoint: r.checkpoint, note: r.note, at: r.created_at })) };
}
async function loadRefImages(env, category, max) {
  const { data } = await db.from('refs').select('path,checkpoint,note').eq('category', category).order('created_at', { ascending: false }).limit(max);
  const out = [];
  for (const r of data || []) {
    const f = await db.storage.from('refs').download(r.path);
    if (f.data) out.push({ image: bytesToDataUrl(f.data.type || 'image/jpeg', await f.data.arrayBuffer()), checkpoint: r.checkpoint, note: r.note });
  }
  return out;
}
async function addMistake(env, b) {
  const { error } = await db.from('mistakes').insert({ category: b.category || 'generic', name: (b.name || '').slice(0, 80), what: (b.what || '').slice(0, 200) });
  if (error) throw new Error(error.message);
  const { count } = await db.from('mistakes').select('id', { count: 'exact', head: true });
  return { ok: true, total: count || 0 };
}
async function getMistakes(env, category) {
  let q = db.from('mistakes').select('category,name,what,created_at').order('created_at', { ascending: false }).limit(100);
  if (category) q = q.eq('category', category);
  const { data } = await q;
  return (data || []).map(m => ({ ...m, at: m.created_at }));
}

// =============================================================
//  DEALS (ซิงก์ข้ามเครื่อง)
// =============================================================
async function listDeals(since) {
  let q = db.from('deals').select('id,data,updated_at,deleted').order('updated_at', { ascending: false }).limit(2000);
  if (since) q = q.gt('updated_at', since);
  const { data, error } = await q;
  if (error) throw new Error(error.message);
  return { deals: data || [], now: new Date().toISOString() };
}
async function saveDeals(b) {
  const rows = (b.deals || []).filter(d => d && d.id).slice(0, 500).map(d => ({
    id: String(d.id), data: d.data || {}, deleted: !!d.deleted, updated_at: d.updated_at || new Date().toISOString()
  }));
  if (!rows.length) return { ok: true, saved: 0 };
  // ไม่เขียนทับข้อมูลที่ใหม่กว่า
  const { data: cur } = await db.from('deals').select('id,updated_at').in('id', rows.map(r => r.id));
  const newer = new Map((cur || []).map(c => [c.id, c.updated_at]));
  const toSave = rows.filter(r => !newer.has(r.id) || new Date(r.updated_at) >= new Date(newer.get(r.id)));
  if (toSave.length) { const { error } = await db.from('deals').upsert(toSave); if (error) throw new Error(error.message); }
  return { ok: true, saved: toSave.length, skipped: rows.length - toSave.length };
}
async function saveDealImages(b) {
  if (!b.id || !Array.isArray(b.images)) { const e = new Error('ต้องมี id และ images'); e.status = 400; throw e; }
  const labels = b.labels || [];
  const saved = [];
  for (let i = 0; i < Math.min(b.images.length, 10); i++) {
    const { type, bytes } = dataUrlToBytes(b.images[i]);
    const path = `${b.id}/${i}.jpg`;
    const up = await db.storage.from('deal-images').upload(path, bytes, { contentType: type, upsert: true });
    if (up.error) throw new Error(up.error.message);
    saved.push({ path, label: labels[i] || '' });
  }
  await db.storage.from('deal-images').upload(`${b.id}/labels.json`, new TextEncoder().encode(JSON.stringify(saved)), { contentType: 'application/json', upsert: true });
  return { ok: true, count: saved.length };
}
async function getDealImages(id) {
  const f = await db.storage.from('deal-images').download(`${id}/labels.json`);
  if (!f.data) return { images: [] };
  const list = JSON.parse(await f.data.text());
  const { data } = await db.storage.from('deal-images').createSignedUrls(list.map(x => x.path), 3600);
  return { images: (data || []).map((d, i) => ({ url: d.signedUrl, label: list[i] ? list[i].label : '' })) };
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
  try { host = new URL(r.url).hostname.replace('www.', ''); } catch (_e) { /* ignore */ }
  return { title: r.title, url: r.url, host, price: r.price ?? null, type: r.type || null };
}
