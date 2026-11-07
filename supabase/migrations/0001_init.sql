-- Deal Hunter schema (ทุกตารางเปิด RLS ไม่มี policy = เข้าถึงได้เฉพาะ Edge Function ที่ใช้ service role)
create table if not exists public.knowledge (
  id text primary key, category text not null, kind text not null, brand text, title text not null, era text,
  keywords text[] default '{}', cues jsonb default '[]', red_flags jsonb default '[]', value_notes text,
  confidence text default 'sourced', sources jsonb default '[]', updated_at timestamptz default now());
create table if not exists public.price_cache (key text primary key, data jsonb not null, expires_at timestamptz not null);
create table if not exists public.refs (id uuid primary key default gen_random_uuid(), category text not null,
  checkpoint text default '', note text default '', path text not null, created_at timestamptz default now());
create table if not exists public.mistakes (id bigserial primary key, category text default 'generic', name text default '',
  what text default '', created_at timestamptz default now());
create table if not exists public.deals (id text primary key, data jsonb not null, updated_at timestamptz not null default now(),
  deleted boolean not null default false);
create table if not exists public.app_config (key text primary key, value text not null, updated_at timestamptz default now());
alter table public.knowledge enable row level security;
alter table public.price_cache enable row level security;
alter table public.refs enable row level security;
alter table public.mistakes enable row level security;
alter table public.deals enable row level security;
alter table public.app_config enable row level security;
insert into storage.buckets (id, name, public) values ('refs','refs',false), ('deal-images','deal-images',false) on conflict do nothing;
-- ค่าตั้งค่า: ใส่เองใน Table Editor (อย่าใส่คีย์จริงในไฟล์นี้)
-- insert into public.app_config(key,value) values ('GEMINI_API_KEY','...'),('APP_KEY','...'),('GEMINI_MODEL','gemini-3.8-flash');
