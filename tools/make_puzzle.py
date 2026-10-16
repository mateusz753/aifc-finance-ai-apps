# Generates a synthetic finance-desk puzzle image (no real data).
import random
from PIL import Image, ImageDraw, ImageFont
random.seed(4471)
W,H=1200,800
im=Image.new("RGB",(W,H),"#3b2f2a"); d=ImageDraw.Draw(im)
def F(s,b=False):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"%("-Bold" if b else ""),s)
    except: return ImageFont.load_default()
# desk wood grain
for y in range(0,H,6): d.line([(0,y),(W,y+random.randint(-3,3))],fill=(60+random.randint(-6,6),47,41))
# monitor with spreadsheet
d.rounded_rectangle([60,40,860,560],18,fill="#111"); d.rectangle([80,60,840,520],fill="white")
d.rectangle([80,60,840,84],fill="#1f7244"); d.text((90,64),"AR_aging_FY26_DEMO.xlsx  (synthetic)",fill="white",font=F(14,True))
cols=[80,150,280,420,560,700,840]; hdr=["#","Invoice","Customer","Amount","Due","Status"]
rows=17; rh=25; y0=88
custs=["Acme Ltd","Globex","Initech","Umbrella","Stark Co","Wayne Ent","Hooli","Vandelay","Soylent","Wonka"]
st=["Paid","Open","Overdue","Disputed","Open","Paid"]
target=(9,1)
used=set()
for r in range(rows+1):
    y=y0+r*rh
    for c in range(6):
        x=cols[c]; fill="#e8f0e8" if r==0 else ("#f7f7f7" if r%2 else "white")
        d.rectangle([x,y,cols[c+1],y+rh],fill=fill,outline="#c8c8c8")
        if r==0: t=hdr[c]
        elif c==0: t=str(r)
        elif c==1:
            if (r,c)==target: t="INV-4471"
            else:
                while True:
                    n=random.choice([4417,4741,4474,4714,4147,4771,4441,4477,4174,4711,1447,7441,4470,4472,4461,4481])
                    if n not in used: used.add(n); break
                t=f"INV-{n}"
        elif c==2: t=random.choice(custs)
        elif c==3: t=f"{random.randint(1,99)},{random.randint(100,999)}.{random.randint(10,99)}"
        elif c==4: t=f"2026-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        else: t=random.choice(st)
        d.text((x+6,y+5),t,fill="#222",font=F(13,r==0))
# tiny gold coin on target cell
tx=cols[2]-18; ty=y0+target[0]*rh+12
d.ellipse([tx-7,ty-7,tx+7,ty+7],fill="#d4a017",outline="#8a6500"); d.text((tx-3,ty-7),"$",fill="#8a6500",font=F(10,True))
# decoys: yellow/orange circles elsewhere (not coins)
for _ in range(6):
    x,y=random.randint(100,820),random.randint(100,510); d.ellipse([x-6,y-6,x+6,y+6],fill=random.choice(["#f4d03f","#e67e22","#f1c40f"]))
d.rectangle([420,560,500,620],fill="#222"); d.rectangle([340,615,580,635],fill="#222")
# desk clutter
for _ in range(14):
    x,y=random.randint(880,1160),random.randint(40,760); w,h=random.randint(40,110),random.randint(30,80)
    d.rectangle([x,y,x+w,y+h],fill=random.choice(["#fff59d","#ffcc80","#b3e5fc","#f8bbd0","#eeeeee"]),outline="#666")
    d.text((x+4,y+4),random.choice(["Q3 close!","call bank","VAT","accruals","FX 4.31","budget","INV-4417?","audit","KPI","coffee"]),fill="#333",font=F(11))
d.ellipse([900,600,1010,710],fill="#6d4c41"); d.ellipse([915,615,995,695],fill="#3e2723")  # coffee
d.rectangle([80,650,560,760],fill="#e0e0e0",outline="#999")  # calculator/keyboard
for i in range(12):
    for j in range(4): d.rectangle([90+i*39,658+j*25,124+i*39,678+j*25],fill="#fafafa",outline="#aaa")
d.text((600,700),"AI Finance Club · synthetic riddle",fill="#d7ccc8",font=F(14))
im.save("../riddle_puzzle.png",optimize=True); print("ok")
