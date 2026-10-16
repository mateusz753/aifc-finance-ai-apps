"""Procedurally render a fictional 4K desk scene with a printed AR aging report and a tiny gold coin next to INV-4471.
Output: riddle_puzzle_4k.jpg (3840x2160) + riddle_puzzle_1600.jpg. Pure PIL+numpy, no AI text."""
import numpy as np, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(7); rng=np.random.default_rng(7)
W,H=3840,2160; F="/usr/share/fonts/truetype/dejavu/"
def font(n,s): return ImageFont.truetype(F+n,s)
def noise(h,w,scale):
    a=rng.random((h//scale+2,w//scale+2)).astype(np.float32)
    return np.array(Image.fromarray((a*255).astype(np.uint8)).resize((w,h),Image.BICUBIC),np.float32)/255
# --- wood desk
y=np.linspace(0,1,H)[:,None]; x=np.linspace(0,1,W)[None,:]
grain=np.sin((y*1.0+x*0.08+noise(H,W,500)*0.05+noise(H,W,60)*0.004)*260)*0.5+0.5; grain=grain**3*0.6+noise(H,W,3)*0.15+noise(H,W,900)*0.25
base=np.stack([70+40*grain,42+25*grain,24+14*grain],-1)*(0.75+0.35*noise(H,W,600)[...,None])
# night lighting: warm lamp pool top-left, vignette
d=np.sqrt((x-0.35)**2+(y-0.4)**2*1.6); light=np.clip(1.25-d*1.5,0.25,1.25)[...,None]
img=Image.fromarray(np.clip(base*light,0,255).astype(np.uint8)).convert("RGBA")
def shadow_paste(layer,pos,off=(28,34),blur=30,alpha=150):
    a=layer.split()[3]; sh=Image.new("RGBA",layer.size,(0,0,0,0)); sh.putalpha(a.point(lambda v:alpha if v>0 else 0))
    pad=Image.new("RGBA",(layer.width+200,layer.height+200),(0,0,0,0)); pad.paste(sh,(100,100)); pad=pad.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(pad,(pos[0]-100+off[0],pos[1]-100+off[1])); img.alpha_composite(layer,pos)
# --- report paper (flat), then perspective
PW,PH=2000,2600; paper=np.full((PH,PW,3),246,np.float32)*(0.97+0.04*noise(PH,PW,6)[...,None])*np.array([1,0.99,0.96])
pimg=Image.fromarray(np.clip(paper,0,255).astype(np.uint8)); dr=ImageDraw.Draw(pimg)
ink=(28,30,36)
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
    if i%2: dr.rectangle((110,ry-8,1890,ry+82),fill=(236,236,232))
    vals=[random.choice(["",f"{random.randint(1,40)*137:,}.00"]) for _ in range(4)]
    if not any(vals): vals[0]=f"{random.randint(200,9000):,}.00"
    dr.text((cols[0],ry+12),v,font=fm,fill=ink); dr.text((cols[1],ry+12),c,font=fm,fill=ink)
    for k,t in enumerate(vals): dr.text((cols[2+k]+250-dr.textlength(t,font=fm)-10,ry+12),t,font=fm,fill=ink)
    rows[v]=ry; ry+=95
dr.line((110,ry,1890,ry),fill=ink,width=3)
dr.text((120,ry+30),"Totals carried to page 2    Prepared by: AR desk    CONFIDENTIAL - DEMO DATA",font=font("DejaVuSans.ttf",32),fill=(90,90,96))
pimg=pimg.filter(ImageFilter.GaussianBlur(0.8))
# highlighter decoys
hl=Image.new("RGBA",pimg.size,(0,0,0,0)); hd=ImageDraw.Draw(hl)
for v in ["INV-4474","INV-4741","INV-4147"]: hd.rectangle((105,rows[v]+5,520,rows[v]+72),fill=(255,214,0,95))
hd.rectangle((1520,rows["INV-4417"]+5,1890,rows["INV-4417"]+72),fill=(255,150,0,80))
pimg=Image.alpha_composite(pimg.convert("RGBA"),hl.filter(ImageFilter.GaussianBlur(3)))
pd=ImageDraw.Draw(pimg)
for v,off,col in [("INV-4417",470,(255,190,20)),("INV-7441",-60,(255,140,30)),("INV-4714",470,(255,200,40)),("INV-4744",-60,(240,160,20))]:
    cx,cy=cols[0]+off+20,rows[v]+40; pd.ellipse((cx-24,cy-24,cx+24,cy+24),fill=col)  # sticky dots
# coin on flat paper next to INV-4471 (right of the number, before customer)
cx,cy,R=cols[0]+350,rows["INV-4471"]+42,30
pimg=pimg.convert("RGBA")
sh=Image.new("RGBA",pimg.size,(0,0,0,0)); ImageDraw.Draw(sh).ellipse((cx-R+6,cy-R+9,cx+R+10,cy+R+13),fill=(0,0,0,150))
pimg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
S=4*R; yy,xx=np.mgrid[-S//2:S//2,-S//2:S//2]/(S/2); rr=np.sqrt(xx**2+yy**2)
ang=np.arctan2(yy,xx); shade=0.85+0.3*np.cos(ang+2.4)*np.clip(rr,0,1)
rim=(rr>0.82)&(rr<1); ridge=0.85+0.15*np.sin(ang*90)
rel=0.9+0.1*np.sin(rr*40)*(rr<0.7)
k=np.where(rim,shade*ridge*1.1,shade*rel*0.95)
spec=np.exp(-((xx+0.35)**2+(yy+0.4)**2)/0.03)*0.6
gold=np.stack([250*k+255*spec,200*k+235*spec,80*k+160*spec],-1)
coin=np.dstack([np.clip(gold,0,255),(rr<1)*255]).astype(np.uint8)
coin=Image.fromarray(coin,"RGBA").resize((2*R,2*R),Image.LANCZOS)
pimg.alpha_composite(coin,(cx-R,cy-R))
# brass paperclip decoy
cd=ImageDraw.Draw(pimg); px,py=1500,rows["INV-4521"]
for o,c in [(0,(140,100,30)),(-2,(225,185,90))]: cd.rounded_rectangle((px+o,py+o,px+380+o,py+70+o),radius=35,outline=c,width=7); cd.rounded_rectangle((px+40+o,py+15+o,px+330+o,py+55+o),radius=20,outline=c,width=6)
# perspective warp onto desk: quad corners (tl,tr,br,bl) in scene
quad=[(1180,170),(2780,260),(2900,2120),(1020,2060)]
import numpy.linalg as la
def coeffs(src,dst):
    A=[];B=[]
    for (X,Y),(u,v) in zip(dst,src):
        A+=[[X,Y,1,0,0,0,-u*X,-u*Y],[0,0,0,X,Y,1,-v*X,-v*Y]]; B+=[u,v]
    return la.solve(np.array(A,float),np.array(B,float))
src=[(0,0),(PW,0),(PW,PH),(0,PH)]
warped=pimg.transform((W,H),Image.PERSPECTIVE,tuple(coeffs(src,quad)),Image.BICUBIC)
# curl shading across paper
g=(0.9+0.12*np.sin(x*9+1)+0.0*y)*np.clip(1.15-d*0.6,0.7,1.1); wa=np.array(warped,np.float32); wa[...,:3]*=g[...,None]
shadow_paste(Image.fromarray(np.clip(wa,0,255).astype(np.uint8),"RGBA"),(0,0),off=(22,30),blur=25,alpha=140)
# laptop (top right, dark), coffee mug, calculator, sticky notes, pens, receipts
L=Image.new("RGBA",(1100,760),(0,0,0,0)); ld=ImageDraw.Draw(L)
ld.rounded_rectangle((0,0,1100,760),40,fill=(48,50,56)); ld.rounded_rectangle((40,40,1060,560),20,fill=(30,32,36))
for r in range(6):
    for c in range(14): ld.rounded_rectangle((60+c*70,80+r*75,118+c*70,140+r*75),8,fill=(22,23,26))
ld.rounded_rectangle((380,600,720,730),16,fill=(40,42,47)); L=L.rotate(-8,expand=True,resample=Image.BICUBIC)
shadow_paste(L,(2900,-120))
M=Image.new("RGBA",(520,520),(0,0,0,0)); md=ImageDraw.Draw(M)
md.ellipse((10,10,510,510),fill=(232,232,228)); md.ellipse((50,50,470,470),fill=(205,205,200)); md.ellipse((70,70,450,450),fill=(52,30,16)); md.ellipse((140,130,250,190),fill=(110,80,55))
shadow_paste(M.filter(ImageFilter.GaussianBlur(1.5)),(260,1180))
C=Image.new("RGBA",(560,820),(0,0,0,0)); kd=ImageDraw.Draw(C); kd.rounded_rectangle((0,0,560,820),40,fill=(38,38,42)); kd.rectangle((50,50,510,200),fill=(150,165,140))
kd.text((90,90),"18,442.70",font=font("DejaVuSansMono-Bold.ttf",64),fill=(30,35,30))
for r in range(5):
    for c in range(4): kd.rounded_rectangle((50+c*118,250+r*110,148+c*118,335+r*110),14,fill=(225,140,40) if (c==3 and r<2) else (70,70,76))
shadow_paste(C.rotate(14,expand=True,resample=Image.BICUBIC),(3020,1120))
for (px,py,a,col) in [(250,250,8,(255,225,90)),(520,330,-12,(255,170,60)),(3150,820,6,(255,215,70))]:
    N=Image.new("RGBA",(380,380),col+(255,)); nd=ImageDraw.Draw(N); nd.text((40,60),"call\nUmberley\nre: 4447?" if px==250 else "chase\n90+",font=font("DejaVuSans.ttf",52),fill=(40,50,120))
    shadow_paste(N.rotate(a,expand=True,resample=Image.BICUBIC),(px,py),blur=14,alpha=110)
for (px,py,a,col) in [(760,1700,32,(25,40,130)),(820,1820,26,(170,20,20)),(2950,2000,-5,(30,30,30))]:
    P=Image.new("RGBA",(900,46),(0,0,0,0)); ppd=ImageDraw.Draw(P); ppd.rounded_rectangle((0,0,900,46),23,fill=col); ppd.rectangle((700,0,720,46),fill=(200,190,150)); ppd.line((20,12,680,12),fill=(255,255,255,70),width=6)
    shadow_paste(P.rotate(a,expand=True,resample=Image.BICUBIC),(px,py),off=(10,14),blur=8)
R2=Image.new("RGBA",(560,900),(250,248,240,255)); rd=ImageDraw.Draw(R2)
for i in range(16): rd.text((40,40+i*50),random.choice(["ITEM ...... 12.40","TAX ........ 2.10","TOTAL ..... 48.90","COFFEE ...... 4.50","REF 4771"]),font=font("DejaVuSansMono.ttf",34),fill=(90,90,95))
shadow_paste(R2.rotate(-20,expand=True,resample=Image.BICUBIC),(30,1500),blur=16,alpha=110)
# global: slight grade, grain, vignette, lens softness
out=np.array(img.convert("RGB"),np.float32)
vig=np.clip(1.25-np.sqrt((x-0.5)**2+(y-0.5)**2)*1.1,0.45,1)[...,None]
out=out*vig*np.array([1.04,0.98,0.9]); out+=rng.normal(0,4,out.shape)
o=Image.fromarray(np.clip(out,0,255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(2,40,2))
o.save("riddle_puzzle_4k.jpg",quality=90,optimize=True,progressive=True)
o.resize((1600,900),Image.LANCZOS).save("riddle_puzzle_1600.jpg",quality=85,optimize=True)
