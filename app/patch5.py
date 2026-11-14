# patch5: เอาดีลตัวอย่าง (ข้อมูลปลอม) ออก — เริ่มจากว่างเปล่า และลบตัวอย่างที่เคยโหลดไว้ในเครื่อง
import sys
s=open('deal-hunter-v2.html',encoding='utf-8').read()
def rep(old,new):
    global s
    if old not in s: sys.exit('NOT FOUND: '+old[:80])
    s=s.replace(old,new,1)
rep("  if(!this.d||!this.d.deals)this.d=this.seed();\n  this.d.usage=this.d.usage||{used:0,saved:0};this.d.stats=this.d.stats||{totalAnalyzed:9};",
    "  if(!this.d||!this.d.deals)this.d={deals:[]};\n  if(this.d.deals.some(x=>x.demo)){this.d.deals=this.d.deals.filter(x=>!x.demo);if(this.d.stats&&this.d.stats.totalAnalyzed===9)this.d.stats.totalAnalyzed=0;localStorage.setItem(this.k,JSON.stringify(this.d));}\n  this.d.usage=this.d.usage||{used:0,saved:0};this.d.stats=this.d.stats||{totalAnalyzed:0};")
rep("reset(){if(confirm('ล้างข้อมูลทั้งหมดและโหลดตัวอย่างใหม่?')){localStorage.removeItem(this.k);this.d=this.seed();this.save()}},",
    "reset(){if(confirm('ล้างดีลทั้งหมดในเครื่องนี้? (ดีลที่ซิงก์ขึ้นคลาวด์แล้วจะยังอยู่ในฐานข้อมูล)')){localStorage.removeItem(this.k);this.d={deals:[],usage:{used:0,saved:0},stats:{totalAnalyzed:0},settings:{capital:50000}};this.save()}},")
open('deal-hunter-v2.html','w',encoding='utf-8').write(s)
print('patch5 ok')
