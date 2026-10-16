"""Composite the fictional AR aging report + gold coin onto the photoreal desk base (tools/desk_base.jpg).
Output: riddle_puzzle_4k.jpg (3840x2160) and riddle_puzzle_1600.jpg."""
import numpy as np, random, numpy.linalg as la, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(7); rng=np.random.default_rng(7)
D=os.path.dirname(os.path.abspath(__file__)); F="/usr/share/fonts/truetype/dejavu/"
font=lambda n,s: ImageFont.truetype(F+n,s)
W,H=3840,2160
base=Image.open(os.path.join(D,"desk_base.jpg")).convert("RGB")
s=W/base.width
base=base.resize((W,H),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2.2,60,3))
k=s*1280/1024  # corners given at 1024-wide scale
quad=[(x*k,y*k) for x,y in [(396.5,128),(686.5,128),(692.5,511.5),(389.5,511.5)]]
PW,PH=2000,2600
pimg=Image.new("RGB",(PW,PH),(255,255,255)); dr=ImageDraw.Draw(pimg); ink=(28,30,40)
dr.text((120,110),"NORTHWIND HOLLOW TRADING (fictional demo)",font=font("DejaVuSans-Bold.ttf",54),fill=ink)
dr.text((120,190),"Accounts Receivable Aging Report  -  as of 30 Sep  -  page 1 of 3",font=font("DejaVuSans.ttf",38),fill=(70,70,76))
cols=[120,470,880,1130,1380,1630]; hdr=["Invoice","Customer","Current","31-60","61-90","90+"]
fm=font("DejaVuSansMono.ttf",40); fb=font("DejaVuSansMono-Bold.ttf",40)
dr.line((110,300,1890,300),fill=ink,width=4)
for c,h in zip(cols,hdr): dr.text((c,320),h,font=fb,fill=ink)
dr.line((110,385,1890,385),fill=ink,width=3)
invs=["INV-4102","INV-4417","INV-4139","INV-4474","INV-7441","INV-4258","INV-4741","INV-4447","INV-4471","INV-4714","INV-1447","INV-4307","INV-4744","INV-4411","INV-4177","INV-4390","INV-4074","INV-4521","INV-4147","INV-4601","INV-4477","INV-4710"]
custs=["Aldervale Co","Brightmoor","Cinder & Fox","Dunmere Ltd","Elmstone","Fernbrook","Glenhaven","Harrowgate","Ivywick Ltd","Juniper Row","Kestrel Bay","Larchfield","Marrowby","Nettlecombe","Oakhurst","Pinecrest","Quillfield","Rookwood","Saltmarsh","Thornbury","Umberley","Valewind"]
rows={}; ry=410
for i,(v,c) in enumerate(zip(invs,custs)):
    if i%2: dr.rectangle((110,ry-8,1890,ry+82),fill=(238,238,238))
    vals=[random.choice(["",f"{random.randint(1,40)*137:,}.00"]) for _ in range(4)]
    if not any(vals): vals[0]=f"{random.randint(200,9000):,}.00"
    dr.text((cols[0],ry+12),v,font=fm,fill=ink); dr.text((cols[1],ry+12),c,font=fm,fill=ink)
    for j,t in enumerate(vals): dr.text((cols[2+j]+250-dr.textlength(t,font=fm)-10,ry+12),t,font=fm,fill=ink)
    rows[v]=ry; ry+=95
dr.line((110,ry,1890,ry),fill=ink,width=3)
dr.text((120,ry+30),"Totals carried to page 2    Prepared by: AR desk    CONFIDENTIAL - DEMO DATA",font=font("DejaVuSans.ttf",32),fill=(90,90,96))
# highlighter (multiplies like real ink)
hl=Image.new("RGB",pimg.size,(255,255,255)); hd=ImageDraw.Draw(hl)
for v in ["INV-4474","INV-4741","INV-4147"]: hd.rectangle((105,rows[v]+5,420,rows[v]+72),fill=(255,236,90))
hd.rectangle((1370,rows["INV-4417"]+5,1640,rows["INV-4417"]+72),fill=(255,200,120))
# decoy faint round smudges / coffee ring over decoy numbers (printed into paper layer)
hd2=ImageDraw.Draw(hl)
for v,cx,r,c,w in [("INV-4417",250,19,(214,200,170),0),("INV-4741",250,70,(205,180,140),6),("INV-4147",300,16,(230,222,200),0),("INV-4074",230,19,(218,206,180),0)]:
    cy=rows[v]+34
    if w: hd2.ellipse((cx-r,cy-r,cx+r,cy+r),outline=c,width=w)
    else: hd2.ellipse((cx-r,cy-r,cx+r,cy+r),fill=c)
hl=hl.filter(ImageFilter.GaussianBlur(4))
a=np.array(pimg,np.float32)/255*np.array(hl,np.float32)/255
# ink softness + toner grain
a=np.array(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)),np.float32)/255
a=1-(1-a)*(0.88+0.12*rng.random(a.shape[:2]))[...,None]
def coeffs(src,dst):
    A=[];B=[]
    for (X,Y),(u,v) in zip(dst,src):
        A+=[[X,Y,1,0,0,0,-u*X,-u*Y],[0,0,0,X,Y,1,-v*X,-v*Y]]; B+=[u,v]
    return la.solve(np.array(A,float),np.array(B,float))
src=[(0,0),(PW,0),(PW,PH),(0,PH)]; C=tuple(coeffs(src,quad))
ink_l=Image.fromarray((a*255).astype(np.uint8)).transform((W,H),Image.PERSPECTIVE,C,Image.BICUBIC,fillcolor=(255,255,255))
out=np.array(base,np.float32)*np.array(ink_l,np.float32)/255   # multiply: inherits sheet lighting
o=Image.fromarray(np.clip(out,0,255).astype(np.uint8)).convert("RGBA")
Hm=la.inv(np.array(list(C)+[1.0]).reshape(3,3))
def to_scene(px,py):
    q=Hm@np.array([px,py,1.0]); return (q[0]/q[2],q[1]/q[2])
def _old(px,py):  # forward map flat paper -> scene (bilinear approx is fine: near-rectangular quad)
    u,v=px/PW,py/PH; (x0,y0),(x1,y1),(x2,y2),(x3,y3)=quad
    return ((1-v)*((1-u)*x0+u*x1)+v*((1-u)*x3+u*x2),(1-v)*((1-u)*y0+u*y1)+v*((1-u)*y3+u*y2))
sx=(quad[1][0]-quad[0][0])/PW
def obj(layer,pos,sh_off,blur,alpha):
    m=layer.split()[3]; sh=Image.new("RGBA",layer.size,(0,0,0,0)); sh.putalpha(m.point(lambda q:alpha if q>128 else 0))
    pad=Image.new("RGBA",(layer.width+120,layer.height+120),(0,0,0,0)); pad.paste(sh,(60,60))
    o.alpha_composite(pad.filter(ImageFilter.GaussianBlur(blur)),(int(pos[0]-60+sh_off[0]),int(pos[1]-60+sh_off[1])))
    o.alpha_composite(layer,(int(pos[0]),int(pos[1])))
def disc(R,col,spec=0.25):
    S=8*R; yy,xx=np.mgrid[-S//2:S//2,-S//2:S//2]/(S/2); rr=np.hypot(xx,yy)
    sh=np.clip(1.0-0.18*(xx+yy),0.7,1.15)+spec*np.exp(-((xx+.4)**2+(yy+.4)**2)/.08)
    im=np.dstack([np.clip(np.array(col)*sh[...,None],0,255),(rr<1)*255]).astype(np.uint8)
    return Image.fromarray(im,"RGBA").resize((2*R,2*R),Image.LANCZOS)
# decoy sticky dots on paper
for v,dx,col in [("INV-7441",-55,(245,175,40)),("INV-4601",1250,(250,205,50)),("INV-4411",1900,(240,150,40))]:
    X,Y=to_scene(cols[0]+dx,rows[v]+42); R=int(22*sx); obj(disc(R,col,0.12),(X-R,Y-R),(3,4),3,90)
# brass paperclip near INV-4417 (decoy)
clip=Image.new("RGBA",(260,70),(0,0,0,0)); cd=ImageDraw.Draw(clip)
for off,c,w in [(0,(120,85,30,255),9),(-2,(214,170,85,255),6)]:
    cd.rounded_rectangle((6+off,6+off,250+off,62+off),28,outline=c,width=w); cd.rounded_rectangle((36+off,18+off,220+off,50+off),16,outline=c,width=w-1)
clip=clip.resize((int(260*sx*1.25),int(70*sx*1.25)),Image.LANCZOS).rotate(-12,expand=True,resample=Image.BICUBIC)
X,Y=to_scene(PW-300,rows["INV-4417"]-150); obj(clip,(X,Y),(5,6),3,110)
# flat coin hidden ON TOP of the digits of INV-4471, top-down, low-opacity blend
bb=dr.textbbox((cols[0],rows["INV-4471"]+12),"INV-4471",font=fm); X,Y=to_scene(bb[2]-2.2*dr.textlength("4",font=fm),(bb[1]+bb[3])/2)
Dpx=int(round(44*sx*1.25)); S=16*Dpx
yy,xx=np.mgrid[-S//2:S//2,-S//2:S//2]/(S/2); rr=np.hypot(xx,yy); ang=np.arctan2(yy,xx)
h=np.zeros_like(rr)                          # height map
h+=np.where(rr>0.86,1.0,0)                   # raised rim
h+=np.where((rr>0.70)&(rr<0.78)&(np.sin(ang*64)>0.3),0.5,0)   # dotted ring
# five-point star
t=(ang+np.pi/2)%(2*np.pi/5)-np.pi/5; star_r=0.52*np.cos(np.pi/5)/np.cos(t)*0.6+0.12
h+=np.where(rr<np.minimum(star_r,0.55)*(0.55+0.45*np.abs(np.cos(t*2.5))),0.7,0)
h=np.array(Image.fromarray((h*120).astype(np.uint8)).filter(ImageFilter.GaussianBlur(S/250)),np.float32)/120
gy,gx=np.gradient(h); emb=1+(-gx-gy)*S/14            # lamp from upper left
brushed=1+0.04*np.sin(ang*400+rng.random()*6)          # subtle radial brushing
reed=np.where(rr>0.97,0.8+0.2*np.sin(ang*180),1)
k=np.clip(emb*brushed*reed,0.35,1.6)*np.where((rr>0.83)&(rr<0.87),0.7,1)*np.where(rr>0.95,0.72,1)
g=np.stack([214*k,178*k,104*k],-1)          # pale gold close to paper/highlighter tone
coin=Image.fromarray(np.dstack([np.clip(g,0,255),(rr<1)*255]).astype(np.uint8),"RGBA").resize((Dpx,Dpx),Image.LANCZOS)
ca=np.array(coin,np.float32); a=ca[...,3:]/255*0.42
x0,y0=int(X-Dpx/2),int(Y-Dpx/2)
reg=np.array(o,np.float32)[y0:y0+Dpx,x0:x0+Dpx,:3]
sh=np.array(Image.fromarray(((rr<1)*255).astype(np.uint8)).resize((Dpx,Dpx)).filter(ImageFilter.GaussianBlur(1.2)),np.float32)[...,None]/255
reg=reg*(1-0.05*sh)                          # very soft flat contact shadow
mul=reg*ca[...,:3]/255*1.18
reg=reg*(1-a)+np.clip(mul,0,255)*a
arr=np.array(o); arr[y0:y0+Dpx,x0:x0+Dpx,:3]=np.clip(reg,0,255).astype(np.uint8); o=Image.fromarray(arr)
fin=np.array(o.convert("RGB"),np.float32)+rng.normal(0,2.2,(H,W,3))
fin=Image.fromarray(np.clip(fin,0,255).astype(np.uint8))
R0=os.path.dirname(D)
fin.save(os.path.join(R0,"riddle_puzzle_4k.jpg"),quality=90,optimize=True,progressive=True)
fin.resize((1600,900),Image.LANCZOS).save(os.path.join(R0,"riddle_puzzle_1600.jpg"),quality=86,optimize=True)
print("coin at",int(X),int(Y),"diam",Dpx)
