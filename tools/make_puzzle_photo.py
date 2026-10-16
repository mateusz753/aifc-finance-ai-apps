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
def to_scene(px,py):  # forward map flat paper -> scene (bilinear approx is fine: near-rectangular quad)
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
for v,dx,col in [("INV-7441",-55,(245,175,40)),("INV-4714",410,(250,205,50)),("INV-4411",1900,(240,150,40))]:
    X,Y=to_scene(cols[0]+dx,rows[v]+42); R=int(22*sx); obj(disc(R,col,0.12),(X-R,Y-R),(3,4),3,90)
# brass paperclip near INV-4417 (decoy)
clip=Image.new("RGBA",(260,70),(0,0,0,0)); cd=ImageDraw.Draw(clip)
for off,c,w in [(0,(120,85,30,255),9),(-2,(214,170,85,255),6)]:
    cd.rounded_rectangle((6+off,6+off,250+off,62+off),28,outline=c,width=w); cd.rounded_rectangle((36+off,18+off,220+off,50+off),16,outline=c,width=w-1)
clip=clip.resize((int(260*sx*1.25),int(70*sx*1.25)),Image.LANCZOS).rotate(-12,expand=True,resample=Image.BICUBIC)
X,Y=to_scene(PW-300,rows["INV-4417"]-150); obj(clip,(X,Y),(5,6),3,110)
# gold coin next to INV-4471, lamp at upper left -> shadow to lower right
R=int(26*sx*1.0); S=8*R; yy,xx=np.mgrid[-S//2:S//2,-S//2:S//2]/(S/2); rr=np.hypot(xx,yy); ang=np.arctan2(yy,xx)
lit=np.clip(0.85-0.35*(xx+yy)/1.4,0.45,1.2)
rim=(rr>0.84); ridge=0.9+0.1*np.sin(ang*120)
relief=1+0.08*np.sin(rr*34)*(rr<0.6)+0.1*np.exp(-((rr-0.78)/0.03)**2)
kk=np.where(rim,lit*ridge*(1.15-0.4*(rr-0.84)/0.16*(xx+yy>0)),lit*relief)
spec=np.exp(-((xx+.42)**2+(yy+.42)**2)/.05)*0.55
g=np.stack([226*kk+255*spec,172*kk+230*spec,62*kk+140*spec],-1)
coin=Image.fromarray(np.dstack([np.clip(g,0,255),(rr<1)*255]).astype(np.uint8),"RGBA").resize((2*R,2*R),Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
X,Y=to_scene(cols[0]+305,rows["INV-4471"]+30)
for off,b,al in [((4,5),3,170),((12,14),10,90)]:  # contact + soft cast shadow
    sh=Image.new("RGBA",(2*R+80,2*R+80),(0,0,0,0)); ImageDraw.Draw(sh).ellipse((40,40,40+2*R,40+2*R),fill=(20,12,5,al))
    o.alpha_composite(sh.filter(ImageFilter.GaussianBlur(b)),(int(X-R-40+off[0]),int(Y-R-40+off[1])))
o.alpha_composite(coin,(int(X-R),int(Y-R)))
fin=np.array(o.convert("RGB"),np.float32)+rng.normal(0,2.2,(H,W,3))
fin=Image.fromarray(np.clip(fin,0,255).astype(np.uint8))
R0=os.path.dirname(D)
fin.save(os.path.join(R0,"riddle_puzzle_4k.jpg"),quality=90,optimize=True,progressive=True)
fin.resize((1600,900),Image.LANCZOS).save(os.path.join(R0,"riddle_puzzle_1600.jpg"),quality=86,optimize=True)
print("coin at",int(X),int(Y))
