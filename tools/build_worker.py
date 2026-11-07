# ใส่ฐานความจำ (knowledge/apparel-kb.json) เข้าไปใน worker/worker.js ระหว่าง /*KB_START*/ ... /*KB_END*/
import json,re,os
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
kb=json.load(open(os.path.join(root,'knowledge','apparel-kb.json'),encoding='utf-8'))
p=os.path.join(root,'worker','worker.js');s=open(p,encoding='utf-8').read()
s2=re.sub(r'/\*KB_START\*/.*?/\*KB_END\*/',lambda m:'/*KB_START*/'+json.dumps(kb['entries'],ensure_ascii=False)+'/*KB_END*/',s,flags=re.S)
open(p,'w',encoding='utf-8').write(s2);print('KB entries:',len(kb['entries']),'worker size',len(s2.encode())//1024,'KB')
