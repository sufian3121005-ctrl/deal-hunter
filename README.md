# Deal Hunter (ระบบดีล)
ระบบช่วยหาของมือสอง เช็คของแท้ ราคาตลาด และที่ขาย สำหรับมือใหม่

- `site/` — หน้าเว็บ (Cloudflare Pages, output directory = `site`)
- `supabase/functions/deal-hunter/` — หลังบ้าน (Supabase Edge Function)
- `supabase/migrations/` — โครงสร้างฐานข้อมูล
- `knowledge/` — ฐานความรู้
- `app/` — สคริปต์สร้างแอป (patch*.py)

ดูขั้นตอนใน `คู่มือติดตั้ง.md` — รหัสลับทั้งหมดเก็บในตาราง `app_config` ของ Supabase ไม่อยู่ใน repo นี้
