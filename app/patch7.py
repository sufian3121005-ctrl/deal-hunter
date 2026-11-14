# patch7: ผลวิเคราะห์แบบสรุปสั้น (การ์ดเดียว) + รายละเอียดทั้งหมดพับไว้
import sys
s=open('deal-hunter-v2.html',encoding='utf-8').read()
def rep(old,new):
    global s
    if old not in s: sys.exit('NOT FOUND: '+old[:90])
    s=s.replace(old,new,1)
rep("""function Result(a){const b=bm(a.score);const srcLabel={blended:'🧠 ผสม AI + ประวัติจริง',history:'🧠 ประวัติจริงล้วน',ai:'AI/ตลาด',none:'ไม่มีข้อมูล'};
 return`<div class="pagefade space-y-3">""",
"""let detailOpen=false;
function Summary(a){const b=bm(a.score);const au=a.auth;const m=au?(AUTHM[au.level]||AUTHM.suspicious):null;const D=a.defects||[];
 const warn=[];if(a.provenanceFlag)warn.push('🚩 ราคาต่ำผิดปกติ ถามที่มาก่อนซื้อ');if(a.soldN<3&&a.low)warn.push('ข้อมูลราคาขายจริงยังน้อย ใช้เป็นแนวทาง');
 const box=(l,v,c)=>`<div class="rounded-2xl bg-black/[.04] p-2.5 text-center dark:bg-white/[.05]"><div class="text-[10px] text-slate-500">${l}</div><div class="mt-0.5 text-[15px] font-extrabold ${c||''}">${v}</div></div>`;
 return Card(`<div class="flex items-center gap-3"><div class="min-w-0 flex-1">
  <div class="text-xl font-extrabold ${b.tx}">${ic(b.e,'w-5 h-5 inline-block align-[-3px]')} ${T.decision[a.decision]}</div>
  <div class="truncate text-[13px] font-semibold">${a.name||''}</div>
  <div class="truncate text-[11px] text-slate-500">${[a.brand,a.era,a.size?'ไซซ์ '+a.size:''].filter(x=>x&&x!=='unknown').join(' · ')}</div></div>${Ring(a.score,56)}</div>
 <div class="mt-3 grid grid-cols-3 gap-2">${box('ราคาตลาด',money(a.mid))}${box('ซื้อไม่เกิน',money(a.maxBuy),'text-amber-500')}${box('กำไรประมาณ',sgn(a.profit),a.profit>=0?'text-emerald-500':'text-rose-500')}</div>
 <div class="mt-3 space-y-1 text-[13px]">
  ${m?`<div><b class="${m.c}">${m.e} ${m.l}</b></div>`:''}
  <div>${D.length?`⚠️ ตำหนิ ${D.length} จุด${a.defectPct?` (หักราคา ${a.defectPct.toFixed(0)}%)`:''}: <span class="text-slate-500">${D.slice(0,2).map(x=>x.what).join(', ')}${D.length>2?' …':''}</span>`:'✨ ไม่พบตำหนิในรูป'}</div>
  ${a.why&&a.why[0]?`<div class="text-slate-500">💬 ${a.why[0]}</div>`:''}
  ${warn.length?`<div class="text-[11px] text-amber-600">${warn.join(' · ')}</div>`:''}</div>
 <div class="mt-4 flex gap-2"><button onclick="saveDeal()" class="tapscale flex-1 rounded-2xl bg-ink-900 py-3 text-sm font-bold text-white dark:bg-white dark:text-ink-950">💾 บันทึกเป็นดีล</button>
 <button onclick="ana=null;imgs=[];thumbs=[];labels=[];photoWarn=[];scan=null;pending=[];render()" class="tapscale rounded-2xl bg-black/5 px-4 text-sm font-semibold dark:bg-white/5">ชิ้นต่อไป</button></div>`,`ring-2 ${b.ring} ${b.bg}`);}
function Result(a){const b=bm(a.score);const srcLabel={blended:'🧠 ผสม AI + ประวัติจริง',history:'🧠 ประวัติจริงล้วน',ai:'AI/ตลาด',none:'ไม่มีข้อมูล'};
 return`<div class="pagefade space-y-3">${Summary(a)}
 <details ${detailOpen?'open':''} ontoggle="detailOpen=this.open" class="group">
 <summary class="tapscale cursor-pointer list-none rounded-2xl bg-black/5 py-3 text-center text-sm font-semibold text-slate-600 dark:bg-white/5 dark:text-slate-300"><span class="group-open:hidden">ดูรายละเอียดทั้งหมด ▾</span><span class="hidden group-open:inline">ซ่อนรายละเอียด ▴</span></summary>
 <div class="mt-3 space-y-3">""")
rep("""<div class="flex gap-2.5"><button onclick="saveDeal()" class="tapscale flex-1 rounded-2xl bg-ink-900 py-3 text-sm font-bold text-white dark:bg-white dark:text-ink-950">💾 บันทึกเป็นดีล</button>
 <button onclick="ana=null;imgs=[];thumbs=[];scan=null;pending=[];render()" class="tapscale rounded-2xl bg-black/5 px-5 text-sm font-semibold dark:bg-white/5">ล้าง</button></div></div>`;}""",
"""</div></details></div>`;}""")
open('deal-hunter-v2.html','w',encoding='utf-8').write(s)
print('patch7 ok')
