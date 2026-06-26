#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""StrideSense — English PM->CEO pitch (for Fitasy). Visual-first, low-text. 9 slides, dark theme."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

BG=RGBColor(0x0b,0x0e,0x14); PANEL=RGBColor(0x15,0x1c,0x28); PANEL2=RGBColor(0x1b,0x23,0x30)
LINE=RGBColor(0x2a,0x34,0x45); TXT=RGBColor(0xe6,0xed,0xf3); DIM=RGBColor(0x9f,0xb0,0xc8)
ACC=RGBColor(0x4c,0xc2,0xff); GOOD=RGBColor(0x3f,0xb9,0x50); WARN=RGBColor(0xe3,0xb3,0x41)
BAD=RGBColor(0xf8,0x51,0x49); PINK=RGBColor(0xff,0x7a,0xa8); PURP=RGBColor(0xb9,0x8c,0xff)
GREY=RGBColor(0x6b,0x7a,0x90)
FONT="Helvetica Neue"

prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
BLANK=prs.slide_layouts[6]

def setfont(r,name=FONT):
    r.font.name=name; rPr=r._r.get_or_add_rPr()
    for tag in ("a:ea","a:cs"):
        el=rPr.find(qn(tag))
        if el is None: el=rPr.makeelement(qn(tag),{}); rPr.append(el)
        el.set("typeface",name)
def slide():
    s=prs.slides.add_slide(BLANK); s.background.fill.solid(); s.background.fill.fore_color.rgb=BG; return s
def rect(s,x,y,w,h,fill=None,line=None,shape=MSO_SHAPE.ROUNDED_RECTANGLE,lw=1.0):
    sp=s.shapes.add_shape(shape,Inches(x),Inches(y),Inches(w),Inches(h))
    if fill is None: sp.fill.background()
    else: sp.fill.solid(); sp.fill.fore_color.rgb=fill
    if line is None: sp.line.fill.background()
    else: sp.line.color.rgb=line; sp.line.width=Pt(lw)
    sp.shadow.inherit=False; return sp
def text(s,x,y,w,h,runs,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP,space=4,lh=1.12):
    tb=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=tb.text_frame
    tf.word_wrap=True; tf.vertical_anchor=anchor
    for i,para in enumerate(runs):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align; p.space_after=Pt(space); p.space_before=Pt(0); p.line_spacing=lh
        for (t,sz,col,bold) in para:
            r=p.add_run(); r.text=t; r.font.size=Pt(sz); r.font.color.rgb=col; r.font.bold=bold; setfont(r)
    return tb
def pic(s,path,x,y,h=None,w=None):
    kw={}
    if h is not None: kw["height"]=Inches(h)
    if w is not None: kw["width"]=Inches(w)
    return s.shapes.add_picture(path,Inches(x),Inches(y),**kw)
def title(s,kicker,ttl):
    rect(s,0.55,0.46,0.10,0.58,fill=ACC,shape=MSO_SHAPE.RECTANGLE)
    text(s,0.8,0.4,12,0.4,[[(kicker,12,ACC,True)]])
    text(s,0.78,0.7,12.4,0.8,[[(ttl,25,TXT,True)]])
def tag(s,n): text(s,9.6,7.06,3.1,0.32,[[("StrideSense  ·  "+str(n)+"/9",10,DIM,False)]],align=PP_ALIGN.RIGHT)
def arrow(s,x,y,w,h=0.3,col=ACC):
    a=s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x),Inches(y),Inches(w),Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb=col; a.line.fill.background(); a.shadow.inherit=False
def darrow(s,x,y,h,w=0.32,col=ACC):
    a=s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW,Inches(x),Inches(y),Inches(w),Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb=col; a.line.fill.background(); a.shadow.inherit=False
def node(s,x,y,w,h,emo,label,col,es=44,ls=14):
    rect(s,x,y,w,h,fill=PANEL,line=col,lw=1.6)
    text(s,x,y+h*0.14,w,h*0.5,[[(emo,es,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,y+h*0.66,w,h*0.34,[[(label,ls,TXT,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.TOP)
def chip(s,x,y,w,h,emo,label,col=LINE,tcol=TXT,fs=12,bold=True):
    rect(s,x,y,w,h,fill=PANEL2,line=col,lw=1.2)
    text(s,x+0.12,y,w-0.2,h,[[(emo+"  ",fs+3,TXT,False),(label,fs,tcol,bold)]],anchor=MSO_ANCHOR.MIDDLE)
def keyline(s,txt,col=ACC,y=6.55):
    rect(s,0.7,y,11.93,0.62,fill=PANEL2,line=col,lw=1.2)
    text(s,0.9,y,11.5,0.62,[[(txt,14,TXT,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)

# ===================================================== 1 Cover
s=slide()
rect(s,0,5.78,13.333,0.06,fill=ACC,shape=MSO_SHAPE.RECTANGLE)
text(s,0.9,1.5,11.5,0.5,[[("PARTNERSHIP PROPOSAL   ·   FOR FITASY",13,ACC,True)]])
text(s,0.85,2.1,11.7,1.2,[[("StrideSense",60,TXT,True)]])
text(s,0.9,3.55,11.6,0.7,[[("Make every Stride understand how its wearer moves.",22,DIM,False)]])
for i,(emo,lab) in enumerate([("👟","Removable pod"),("🩺","Rehab"),("🏃","Performance"),("✅","Proven today")]):
    x=0.9+i*3.05
    text(s,x,6.05,2.9,0.5,[[(emo+"  ",18,TXT,False),(lab,13,DIM,True)]])
text(s,0.9,6.95,11.5,0.4,[[("Xiaoyu Zhang  ·  2026",12,DIM,False)]])

# ===================================================== 2 The product (flow)
s=slide(); title(s,"① THE PRODUCT","A pop-in pod that makes the shoe sense")
n_w,n_h,g=3.0,2.35,0.85; x0=(13.333-(n_w*3+g*2))/2; y0=2.0
node(s,x0,y0,n_w,n_h,"👟","Stride + pod cavity",ACC)
node(s,x0+(n_w+g),y0,n_w,n_h,"🔌","Removable 6-axis pod",GOOD)
node(s,x0+2*(n_w+g),y0,n_w,n_h,"📱","Phone app",PINK)
arrow(s,x0+n_w+0.12,y0+n_h/2-0.18,g-0.24,0.36,col=ACC)
arrow(s,x0+2*n_w+g+0.12,y0+n_h/2-0.18,g-0.24,0.36,col=GOOD)
# pillars
pw=3.7; px=(13.333-(pw*3+0.3*2))/2; py=4.95
for i,(t) in enumerate(["Custom fit","Single-material recyclable","Single-shoe"]):
    chip(s,px+i*(pw+0.3),py,pw,0.66,"✓",t,col=LINE,tcol=DIM,fs=12.5)
keyline(s,"Removable by design — sensing added, recyclability untouched.",col=ACC,y=6.45)
tag(s,2)

# ===================================================== 3 Two markets, one sensor
s=slide(); title(s,"② WHAT IT'S FOR","Two markets, one sensor")
rect(s,0.55,1.65,5.5,3.45,fill=PANEL,line=GOOD,lw=1.5)
rect(s,0.55,1.65,5.5,0.6,fill=GOOD); text(s,0.55,1.65,5.5,0.6,[[("🩺  REHAB  ·  anchor",14,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
reh=[("🚶","Gait: speed · cadence · stride"),("📉","Fall-risk (variability)"),("🦶","Clearance · ROM"),("🔁","Recovery: return-to-walk")]
for i,(e,t) in enumerate(reh): chip(s,0.85,2.42+i*0.62,4.9,0.5,e,t,col=LINE,fs=12)
rect(s,7.28,1.65,5.5,3.45,fill=PANEL,line=WARN,lw=1.5)
rect(s,7.28,1.65,5.5,0.6,fill=WARN); text(s,7.28,1.65,5.5,0.6,[[("🏃  PERFORMANCE  ·  expansion",14,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
per=[("👟","Running: cadence · contact time"),("💥","Impact · loading"),("↔","Left–right asymmetry"),("🗺","Distance · trajectory")]
for i,(e,t) in enumerate(per): chip(s,7.58,2.42+i*0.62,4.9,0.5,e,t,col=LINE,fs=12)
rect(s,6.02,2.95,1.27,1.27,fill=ACC,shape=MSO_SHAPE.OVAL)
text(s,6.02,2.95,1.27,1.27,[[("ONE",13,BG,True)],[("pod",12,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
keyline(s,"One pod → trajectory + clinical gait.  A category of one — no rival owns both.",col=ACC,y=5.45)
tag(s,3)

# ===================================================== 4 Why Fitasy (before -> after)
s=slide(); title(s,"② WHY IT MATTERS TO FITASY","From a one-time sale to a platform")
rect(s,1.05,1.75,4.6,1.95,fill=PANEL,line=DIM,lw=1.4)
text(s,1.05,2.0,4.6,0.9,[[("👟  💲",34,TXT,False)]],align=PP_ALIGN.CENTER)
text(s,1.05,3.05,4.6,0.55,[[("One-time shoe sale",15,DIM,True)]],align=PP_ALIGN.CENTER)
arrow(s,5.95,2.55,1.45,0.42,col=ACC)
rect(s,7.7,1.75,4.6,1.95,fill=PANEL,line=ACC,lw=1.6)
text(s,7.7,2.0,4.6,0.9,[[("📱  🔁",34,TXT,False)]],align=PP_ALIGN.CENTER)
text(s,7.7,3.05,4.6,0.55,[[("Recurring health platform",15,ACC,True)]],align=PP_ALIGN.CENTER)
badges=[("💵","Recurring revenue",ACC),("📈","Retention · LTV",GOOD),("🏥","B2B channels",PINK),("🛡","Software moat",PURP)]
bw,g=2.85,0.3; bx=(13.333-(bw*4+g*3))/2; by=4.15
for i,(e,t,col) in enumerate(badges):
    x=bx+i*(bw+g)
    rect(s,x,by,bw,1.55,fill=PANEL,line=col,lw=1.4)
    text(s,x,by+0.24,bw,0.6,[[(e,26,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,by+0.95,bw,0.5,[[(t,13,TXT,True)]],align=PP_ALIGN.CENTER)
text(s,0.9,6.25,11.6,0.5,[[("Illustrative: ",12.5,WARN,True),("$[X]/mo tier · +$[Y] Smart-Stride SKU · ~[N]× LTV — we carry firmware/support.",12.5,DIM,False)]],align=PP_ALIGN.CENTER)
tag(s,4)

# ===================================================== 5 How it's used (flow)
s=slide(); title(s,"③ HOW IT'S USED","Wear · walk · see")
steps=[("👟","Wear",ACC),("🚶","Walk / run",GOOD),("📶","BLE → phone",PINK),("📊","Dashboard",WARN),("🤝","Share",PURP)]
sw,g=2.28,0.2; x0=(13.333-(sw*5+g*4))/2; y0=2.25
for i,(e,t,col) in enumerate(steps):
    x=x0+i*(sw+g)
    rect(s,x,y0,sw,2.6,fill=PANEL,line=col,lw=1.4)
    text(s,x,y0+0.42,sw,0.9,[[(e,40,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,y0+1.65,sw,0.6,[[(str(i+1)+". "+t,15,TXT,True)]],align=PP_ALIGN.CENTER)
    if i<4: arrow(s,x+sw,y0+1.1,g,0.28,col=col)
keyline(s,"No calibration. The shareable report opens the B2B door.",col=ACC,y=5.6)
tag(s,5)

# ===================================================== 6 Specs & expected (chips)
s=slide(); title(s,"④ SPECS & EXPECTED","Honest ranges — green / amber / grey")
hw=[("6-axis ×2",ACC),("16-bit",ACC),("±16 g",ACC),("±2000 dps",ACC),("100–500 Hz",ACC),("ZUPT",ACC)]
cw,g=1.92,0.12; hx=(13.333-(cw*6+g*5))/2; hy=1.6
for i,(t,col) in enumerate(hw): chip(s,hx+i*(cw+g),hy,cw,0.6,"·",t,col=col,fs=12.5)
tiers=[(GOOD,"RELIABLE",[("Cadence","<2%"),("Speed","ICC .83–.94"),("Clearance","~8–9 mm"),("Foot pitch","0.6–4°"),("Trajectory","0.5–2%")]),
       (WARN,"SPEED-DEP",[("Stride length","±7–13 cm"),("Run GCT","15–30 ms")]),
       (GREY,"TREND-ONLY",[("Gait CV","ICC ~0–.67"),("L–R symmetry","low")])]
y=2.55
for col,h,metrics in tiers:
    rect(s,0.7,y,11.93,1.18,fill=PANEL,line=LINE)
    rect(s,0.7,y,0.13,1.18,fill=col,shape=MSO_SHAPE.RECTANGLE)
    text(s,1.0,y,2.0,1.18,[[(h,13,col,True)]],anchor=MSO_ANCHOR.MIDDLE)
    mx=3.0; mw=1.74
    for j,(nm,val) in enumerate(metrics):
        cxx=mx+j*(mw+0.04)
        rect(s,cxx,y+0.2,mw,0.78,fill=PANEL2,line=col,lw=1.0)
        text(s,cxx,y+0.26,mw,0.7,[[(nm,10.5,DIM,True)],[(val,12.5,TXT,True)]],align=PP_ALIGN.CENTER,space=1)
    y+=1.32
text(s,0.7,6.6,11.93,0.5,[[("Trend-only metrics = screening signals, never precision medical claims.  Confirmed on real pod in Phase 2.",11.5,DIM,False)]])
tag(s,6)

# ===================================================== 7 Demo (images)
s=slide(); title(s,"⑤ CURRENT DEMO","Real foot data — the loop closes itself")
pic(s,"figs_en/fig_traj2d.png",0.66,1.65,h=3.25)
pic(s,"figs_en/fig_cv.png",4.5,2.4,w=4.6)
pic(s,"figs_en/fig_traj3d.png",9.15,1.65,h=3.25)
# big callouts
calls=[("~94%","loop closure",GOOD),("6-axis","only — no GPS/cam",ACC),("ZUPT","drift resets each step",PINK)]
cw2=3.7; cx=(13.333-(cw2*3+0.4*2))/2; cy=5.25
for i,(big,lab,col) in enumerate(calls):
    x=cx+i*(cw2+0.4)
    rect(s,x,cy,cw2,1.0,fill=PANEL,line=col,lw=1.4)
    text(s,x+0.2,cy,1.7,1.0,[[(big,24,col,True)]],anchor=MSO_ANCHOR.MIDDLE)
    text(s,x+1.85,cy,cw2-1.95,1.0,[[(lab,12.5,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE)
text(s,0.7,6.5,11.93,0.5,[[("Phone = clean 6-axis proxy · same IMU + algorithm as the pod → transfer risk is integration, not algorithm.",11.5,DIM,False)]],align=PP_ALIGN.CENTER)
tag(s,7)

# ===================================================== 8 Timeline
s=slide(); title(s,"⑥ PLAN & TIMELINE","Pilot-first · phase-gated")
phs=[("Phase 0","2026 Q2","Algorithm proven",GOOD,"✓ DONE"),
     ("Phase 1","2026 H2","Pod + cavity prototype",ACC,"BUILD"),
     ("Phase 2","2027 H1","Rehab + sport pilot",PINK,"PILOT"),
     ("Phase 3","2027 H2","9-axis · clinical-grade",PURP,"SCALE"),
     ("Phase 4","2028","Launch + subscription",WARN,"LAUNCH")]
bw,bh,g=2.3,3.0,0.18; x0=(13.333-(bw*5+g*4))/2; y0=2.0
rect(s,x0-0.05,y0+bh+0.18,bw*5+g*4+0.1,0.05,fill=LINE,shape=MSO_SHAPE.RECTANGLE)
for i,(ph,when,d,col,badge) in enumerate(phs):
    x=x0+i*(bw+g)
    rect(s,x,y0,bw,bh,fill=PANEL,line=col,lw=1.5)
    rect(s,x,y0,bw,0.52,fill=col)
    text(s,x,y0,bw,0.52,[[(ph,12.5,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    text(s,x,y0+0.66,bw,0.4,[[(when,12,DIM,True)]],align=PP_ALIGN.CENTER)
    text(s,x+0.15,y0+1.25,bw-0.3,1.2,[[(d,13.5,TXT,True)]],align=PP_ALIGN.CENTER,lh=1.15)
    rect(s,x+bw/2-0.7,y0+bh-0.6,1.4,0.42,fill=col)
    text(s,x+bw/2-0.7,y0+bh-0.6,1.4,0.42,[[(badge,11,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    rect(s,x+bw/2-0.06,y0+bh+0.12,0.18,0.18,fill=col,shape=MSO_SHAPE.DIAMOND)
keyline(s,"Fund one step at a time.  Wellness-first launch — no medical clearance needed.",col=ACC,y=5.7)
tag(s,8)

# ===================================================== 9 The Ask
s=slide(); title(s,"THE ASK","Low risk to your core, high upside")
rect(s,0.9,1.75,5.2,1.7,fill=PANEL,line=PINK,lw=1.5)
text(s,0.9,1.9,5.2,0.5,[[("Fitasy owns",15,PINK,True)]],align=PP_ALIGN.CENTER)
text(s,1.1,2.45,4.8,0.9,[[("Shoe · brand · channel · customer",13,TXT,False)]],align=PP_ALIGN.CENTER,lh=1.15)
rect(s,7.23,1.75,5.2,1.7,fill=PANEL,line=ACC,lw=1.5)
text(s,7.23,1.9,5.2,0.5,[[("We own",15,ACC,True)]],align=PP_ALIGN.CENTER)
text(s,7.43,2.45,4.8,0.9,[[("Sensing · algorithms · app · IP",13,TXT,False)]],align=PP_ALIGN.CENTER,lh=1.15)
rect(s,6.05,2.27,1.2,0.7,fill=GOOD,shape=MSO_SHAPE.OVAL)
text(s,6.05,2.27,1.2,0.7,[[("🤝",20,BG,False)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
asks=[("🔧","Co-design the\npod cavity",ACC),("👟","Provide\npilot units",GOOD),("🔒","Exclusivity +\nco-owned data",PURP)]
aw,g=3.7,0.35; ax=(13.333-(aw*3+g*2))/2; ay=3.95
for i,(e,t,col) in enumerate(asks):
    x=ax+i*(aw+g)
    rect(s,x,ay,aw,1.5,fill=PANEL,line=col,lw=1.4)
    text(s,x+0.25,ay,1.1,1.5,[[(e,28,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE)
    text(s,x+1.3,ay,aw-1.5,1.5,[[(ln,13.5,TXT,True)] for ln in t.split("\n")],anchor=MSO_ANCHOR.MIDDLE,lh=1.1,space=1)
keyline(s,"Next step: scope the cavity + pilot. Bounded to test, high optionality to scale.",col=ACC,y=5.85)
tag(s,9)

out="StrideSense_Pitch.pptx"; prs.save(out)
print("saved",out,"·",len(prs.slides._sldIdLst),"slides")
