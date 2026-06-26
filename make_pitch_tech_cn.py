#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""StrideSense technical edition (4 pages): demo device and results -> spec and accuracy comparison table -> lightweight applications."""
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
GREY=RGBColor(0x6b,0x7a,0x90); LGN=RGBColor(0xbf,0xe0,0xc8)
FONT="PingFang SC"; NTOT=6

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
def text(s,x,y,w,h,runs,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP,space=3,lh=1.1):
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
    rect(s,0.55,0.42,0.10,0.55,fill=ACC,shape=MSO_SHAPE.RECTANGLE)
    text(s,0.8,0.36,12,0.4,[[(kicker,11.5,ACC,True)]])
    text(s,0.78,0.66,12.4,0.7,[[(ttl,22,TXT,True)]])
def tag(s,n): text(s,9.6,7.05,3.1,0.3,[[("StrideSense  ·  "+str(n)+"/"+str(NTOT),10.5,DIM,False)]],align=PP_ALIGN.RIGHT)
def keyline(s,txt,col=ACC,y=6.5,fs=13):
    rect(s,0.7,y,11.93,0.6,fill=PANEL2,line=col,lw=1.2)
    text(s,0.95,y,11.45,0.6,[[(txt,fs,TXT,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
def arrow(s,x,y,w,h=0.3,col=ACC):
    a=s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x),Inches(y),Inches(w),Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb=col; a.line.fill.background(); a.shadow.inherit=False
def node(s,x,y,w,h,emo,label,col,es=26,ls=11):
    rect(s,x,y,w,h,fill=PANEL,line=col,lw=1.6)
    text(s,x,y+h*0.1,w,h*0.42,[[(emo,es,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,y+h*0.5,w,h*0.48,[[(ln,ls,TXT,True)] for ln in label.split("\n")],align=PP_ALIGN.CENTER,lh=1.04,space=0)

# ===================================================== 1 Cover
s=slide()
rect(s,0,5.72,13.333,0.06,fill=ACC,shape=MSO_SHAPE.RECTANGLE)
text(s,0.9,1.45,11.5,0.5,[[("手机 Demo · 规格与精度对比",14.5,ACC,True)]])
text(s,0.85,2.05,11.7,1.2,[[("StrideSense",58,TXT,True)]])
text(s,0.9,3.4,11.6,0.6,[[("足部 6 轴 IMU · 手机 Demo 已跑通(可行性)",23,DIM,False)]])
rect(s,0.9,4.14,11.95,0.54,fill=PANEL,line=WARN,lw=1.0)
text(s,1.15,4.14,11.5,0.54,[[("⚠️ 痛点:左右不对称 · 触地过载 · 落地不稳 —— 肉眼看不见,靠感觉练 = 伤 + 停滞",14,TXT,True)]],anchor=MSO_ANCHOR.MIDDLE)
text(s,0.9,4.94,11.8,0.5,[[("现状:一台 iPhone 还原轨迹与步态  →  升级:商用 6 轴 IMU 嵌入 Fitasy 鞋",16,DIM,False)]])
for i,(emo,lab) in enumerate([("📱","Demo 实测"),("📊","精度与能力"),("🚀","未来应用")]):
    x=1.0+i*3.95
    text(s,x,5.98,3.7,0.5,[[(emo+"  ",18,TXT,False),(lab,15,DIM,True)]])
text(s,0.9,6.9,11.5,0.4,[[("张晓宇  ·  2026",13,DIM,False)]])
tag(s,1)

# ===================================================== 2 Demo showcase (video + trajectory reconstruction)
s=slide(); title(s,"① 现有 Demo · 设备与效果","手机 6 轴 IMU(加速度计 + 陀螺仪)记录真人步行,还原 2D / 3D 轨迹")
pic(s,"figs/imu_sensors.png",2.02,1.22,w=9.3)
vy=3.78; vh=2.45; vw=vh*720/1280; ph=2.0; pw=ph*1.185; ly=3.54
tot=vw+0.5+pw+0.42+pw; vx=(13.333-tot)/2
text(s,vx-0.35,ly,vw+0.7,0.26,[[("📹 真人实录",11.5,ACC,True)]],align=PP_ALIGN.CENTER)
s.shapes.add_movie("video.mp4",Inches(vx),Inches(vy),Inches(vw),Inches(vh),poster_frame_image="figs/video_poster.jpg",mime_type="video/mp4")
arrow(s,vx+vw+0.04,vy+vh/2-0.13,0.42,0.26,col=ACC)
g2x=vx+vw+0.5
text(s,g2x,ly,pw,0.26,[[("还原 2D 轨迹 · ●起→○终",11.5,ACC,True)]],align=PP_ALIGN.CENTER)
pic(s,"figs/fig_traj2d.png",g2x,vy,h=ph)
g3x=g2x+pw+0.42
text(s,g3x,ly,pw,0.26,[[("3D 轨迹",11.5,ACC,True)]],align=PP_ALIGN.CENTER)
pic(s,"figs/fig_traj3d.png",g3x,vy,h=ph)
keyline(s,"一台手机(加速度计 + 陀螺仪)就能还原一只脚的完整步态轨迹 —— 换成鞋里的商用 pod,只会更稳、更全。",col=ACC,y=6.31,fs=12.5)
text(s,0.7,6.95,9.0,0.3,[[("口径:单次步行 ~8.6s · 6 步 · 60Hz · 开放路径(非闭环)· 步时 CV≈1.7%;展示可行性与轨迹还原,未做动捕真值标定。",9.6,DIM,False)]])
tag(s,2)

# ===================================================== 3 Comparison: accuracy and capability
s=slide(); title(s,"② Demo 传感器 vs 商用 6 轴 IMU · 精度与能力","各特征精度,够不够当「绝对量化指标」用?")
rect(s,0.7,1.34,5.85,1.12,fill=PANEL,line=WARN,lw=1.3)
text(s,0.92,1.4,5.6,0.32,[[("📱 手机 Demo · iPhone 内置 6 轴(Bosch)",11.5,WARN,True)]])
text(s,0.92,1.76,5.6,0.62,[
  [("~60 Hz · 16-bit · 量程固定 · 软绑 · 弱同步",10.3,DIM,False)],
  [("↔ 与 pod 同类 6 轴、同一套算法,只是采样更低、嵌得软",10.3,ACC,False)],
],lh=1.16,space=2)
rect(s,6.78,1.34,5.85,1.12,fill=PANEL,line=GOOD,lw=1.3)
text(s,6.98,1.4,5.5,0.32,[[("商用 6 轴 IMU pod(实物)",11.5,GOOD,True)]])
pic(s,"figs/chip_imu.png",6.98,1.8,w=3.4)
text(s,10.5,1.5,2.1,1.0,[[("16-bit · ±16g",10.3,TXT,True)],[("±2000 dps",10.3,TXT,True)],[("ODR ≥1 kHz",10.3,TXT,True)],[("刚性嵌鞋·硬时基",9.5,DIM,False)]],lh=1.24,space=1)
# "good enough" conclusion color bar: 7 green usable as absolute metrics / 4 blue track changes
by=2.54; bx=2.7; bw=7.7; bh=0.36; gw=bw*7/11
text(s,0.7,by,1.95,bh,[[("11 项能力 →",10.5,TXT,True)]],align=PP_ALIGN.RIGHT,anchor=MSO_ANCHOR.MIDDLE)
rect(s,bx,by,gw,bh,fill=GOOD,line=GOOD); text(s,bx,by,gw,bh,[[("✓ 7 项 · 可当绝对指标",10.5,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
rect(s,bx+gw,by,bw-gw,bh,fill=ACC,line=ACC); text(s,bx+gw,by,bw-gw,bh,[[("~ 4 项 · 看变化",10.5,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
hy=3.04; rect(s,0.7,hy,11.93,0.36,fill=PANEL2,line=LINE)
for cx,cwd,t,c in [(0.9,2.5,"特征",ACC),(3.45,2.9,"手机 demo 精度",WARN),(6.45,2.9,"商用 pod 精度",GOOD),(9.62,3.0,"能力(够当指标?)",ACC)]:
    text(s,cx,hy,cwd,0.36,[[(t,10.8,c,True)]],anchor=MSO_ANCHOR.MIDDLE)
rows=[("步频 cadence","±2–3 步/分","±1–2 步/分","绝对值",GOOD),
      ("步态周期 stride","±20–40 ms","±5–15 ms","绝对值",GOOD),
      ("步态变异 CV","±1–1.5%","±0.5–1%","绝对值",GOOD),
      ("触地时间 GCT","±30–60 ms","±5–15 ms","绝对值",GOOD),
      ("支撑/摆动相","±5–8%","±2–3%","绝对值",GOOD),
      ("步长 stride length","±8–15%","±2–5%","绝对值",GOOD),
      ("步速 gait speed","±10–20%","±3–8%","变化幅度",ACC),
      ("左右对称 LSI","需双脚","±2–4%(双脚差分)","绝对值",GOOD),
      ("抬脚高度 MTC","±3–6 cm","±1–3 cm","变化幅度",ACC),
      ("足倾角 foot angle","±5–10°","±1–3°(触地)","变化幅度",ACC),
      ("2D / 3D 轨迹","漂移大","高采样+刚性更优","变化幅度",ACC)]
yy=hy+0.40; rh=0.285
for idx,(nm,d,p,cap,cc) in enumerate(rows):
    rect(s,0.7,yy,11.93,rh,fill=PANEL if idx%2==0 else PANEL2,line=None)
    text(s,0.9,yy,2.5,rh,[[(nm,10.3,TXT,True)]],anchor=MSO_ANCHOR.MIDDLE)
    text(s,3.45,yy,2.95,rh,[[(d,10,DIM,False)]],anchor=MSO_ANCHOR.MIDDLE)
    text(s,6.45,yy,2.95,rh,[[(p,10,LGN,False)]],anchor=MSO_ANCHOR.MIDDLE)
    rect(s,9.62,yy+0.03,1.62,rh-0.08,fill=cc,line=cc,lw=1.0)
    text(s,9.62,yy,1.62,rh,[[(cap,9.5,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    yy+=rh
text(s,0.7,yy+0.06,11.93,0.6,[
  [("■ 绝对值",9.6,GOOD,True),(" 可直接当指标     ",9.3,DIM,False),("■ 变化幅度",9.6,ACC,True),(" 需一次校准、但相对变化精准。   足部信号手表测不到。",9.3,DIM,False)],
  [("出处:",9.6,WARN,True),("手机列本机实测,± 为估计(单次·未标定);商用列 = datasheet / 文献上界,对标 Vicon、Plantiga。",9.3,DIM,False)],
],lh=1.22,space=2)
tag(s,3)

# ===================================================== 4 Future applications enabled by commercial IMU + detected features
s=slide(); title(s,"③ 未来 · 商用 6 轴 IMU 能做的应用","同一颗嵌鞋 pod,覆盖运动表现 + 运动康复两大场景")
cw=3.86; cg=0.27; cx0=(13.333-(cw*3+cg*2))/2
def appcard(x,y,emo,nm,feat,col):
    rect(s,x,y,cw,1.94,fill=PANEL,line=col,lw=1.5)
    text(s,x,y+0.12,cw,0.52,[[(emo,28,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,y+0.70,cw,0.36,[[(nm,12,col,True)]],align=PP_ALIGN.CENTER)
    rect(s,x+0.35,y+1.10,cw-0.7,0.014,fill=LINE,shape=MSO_SHAPE.RECTANGLE)
    text(s,x+0.16,y+1.16,cw-0.32,0.7,[[("检测特征",10,DIM,True)],[(feat,10.5,TXT,False)]],align=PP_ALIGN.CENTER,lh=1.16,space=1)
def grouplabel(y,col,txt):
    rect(s,0.6,y+0.02,0.1,0.26,fill=col,shape=MSO_SHAPE.RECTANGLE)
    text(s,0.82,y,11.8,0.3,[[(txt,12.5,col,True)]],anchor=MSO_ANCHOR.MIDDLE)
perf=[("🏃","跑姿与效率优化","步频 · 触地 GCT · 腾空比 · 足倾角 · 对称",WARN),
      ("🗺","跑动路径 · 活动范围","2D / 3D 轨迹 · 步速 · 转身分析",ACC),
      ("🏋","训练负荷管理","累计触地冲击 · 步数 · GCT · 负荷不对称",GREY)]
rehab=[("⚖️","伤后回归 · 对称恢复 LSI","左右对称 · 步长对称 · 单腿负荷 · 落地稳定",PINK),
       ("📉","疲劳 · 落地稳定监测","步态变异 CV · 落地冲击 · 周期波动",GOOD),
       ("🦶","绊倒 / 廓清风险预警","抬脚高度 MTC · 廓清变异 · 足倾角",PURP)]
grouplabel(1.42,WARN,"运动表现 · 跑步效率 / 训练负荷")
for i,a in enumerate(perf): appcard(cx0+i*(cw+cg),1.74,*a)
grouplabel(3.80,PINK,"运动康复 · 伤后回归运动(ACL · 踝 · 过用伤)")
for i,a in enumerate(rehab): appcard(cx0+i*(cw+cg),4.12,*a)
keyline(s,"换报告模板即覆盖两大场景;每个应用 = 一组可量化的足部特征。",col=ACC,y=6.22)
tag(s,4)

# ===================================================== 5 Hardware design - two shoe-embedding routes
s=slide(); title(s,"④ 硬件设计 · 两条嵌鞋路线","完整模块都 ≥10mm,平铺嵌不进薄鞋垫 → 两条可行路,都不碰电路设计")
def photocard(x,y,w,photo,name,spec,col):
    h=1.98
    rect(s,x,y,w,h,fill=PANEL2,line=col,lw=1.0)
    rect(s,x+0.16,y+0.12,w-0.32,1.12,fill=RGBColor(0xee,0xf1,0xf4))
    pic(s,photo,x+w/2-0.58,y+0.18,h=1.0)
    text(s,x,y+1.28,w,0.28,[[(name,10.5,TXT,True)]],align=PP_ALIGN.CENTER)
    text(s,x,y+1.58,w,0.28,[[(spec,10,col,True)]],align=PP_ALIGN.CENTER)
# ---- Route A: complete module + custom midsole slot ----
rect(s,0.5,1.62,6.0,4.55,fill=PANEL,line=WARN,lw=1.6)
text(s,0.72,1.74,5.6,0.32,[[("A · 快路线 — 现成完整模块 + 定制中底卡槽",13,WARN,True)]])
text(s,0.72,2.12,5.6,0.42,[[("买现成完整模块(自带 BLE + 电池)→ Fitasy 3D 打印中底印凹槽嵌入、可拆",10,DIM,False)]],lh=1.12)
photocard(0.72,2.6,2.78,"figs/parts/mod_wit.jpg","WitMotion WT9011DCL","~12mm · $16–30",ACC)
photocard(3.62,2.6,2.78,"figs/parts/mod_mbient.jpg","mbientlab MMS","10mm · $130",PINK)
text(s,0.72,4.72,5.6,0.3,[[("✓ 零电路设计 · 现货 1–2 周试点 · 纯买 + 包装",10.2,GOOD,True)]])
text(s,0.72,5.12,5.6,0.32,[[("✗ 偏厚 ~10–12mm → 靠定制中底凹槽容纳、可拆",10,DIM,False)]])
text(s,0.72,5.6,5.6,0.32,[[("→ 正是「买现成+包装」原思路,定制鞋是关键",10,WARN,True)]])
# ---- Route B: small board + ultra-thin battery ~5mm ----
rect(s,6.83,1.62,6.0,4.55,fill=PANEL,line=GOOD,lw=1.6)
text(s,7.05,1.74,5.6,0.32,[[("B · 薄路线 — 小板 + 超薄电池 ~5mm",13,GOOD,True)]])
text(s,7.05,2.12,5.6,0.42,[[("小板(自带 BLE + 6 轴)+ 超薄锂电 → 叠装 ~5mm,塞进任意薄鞋垫",10,DIM,False)]],lh=1.12)
photocard(7.05,2.6,2.78,"figs/parts/mod_xiao.jpg","Seeed XIAO nRF52840 Sense","21×18×3.5mm · $16",ACC)
photocard(9.95,2.6,2.78,"figs/parts/batt.png","超薄软包锂电","~1mm / 50mAh · $3",WARN)
text(s,7.05,4.72,5.6,0.3,[[("= 叠装 ~5mm pod · 6 轴 + BLE5.4 · 自带充电管理",10.2,GOOD,True)]])
text(s,7.05,5.12,5.6,0.32,[[("✓ ~5mm 最薄无感,任意薄鞋垫可塞",10,GOOD,False)]])
text(s,7.05,5.6,5.6,0.32,[[("✗ 需连一块电池(轻量组装,仍非电路设计)",10,DIM,True)]])
keyline(s,"建议:A 快路线先做真鞋试点验证 → B 薄路线做产品化;两条都现货、都不碰电路设计。",col=ACC,y=6.34,fs=12)
tag(s,5)

# ===================================================== 6 Next steps - delivery path + CTA
s=slide(); title(s,"⑤ 下一步 · 从手机 Demo 到嵌鞋产品","三步兑现:现成模块真鞋试点 → 验证精度与稳定性 → 薄 pod 产品化")
text(s,0.8,1.42,11.8,0.4,[[("手机 demo 已证『6 轴够还原步态』;商用 pod 精度 = 下一步要在鞋上兑现的目标,非已达成。",13,DIM,False)]])
steps=[("🛒","① 现成模块 · 真鞋试点","完整模块(自带 BLE+电池)装\nFitasy 定制中底凹槽 · 可拆",ACC),
       ("🎯","② 验证精度与稳定性","确认测量精度\n与日常使用稳定性",GOOD),
       ("👟","③ 薄 pod · 产品化","做成 ~5mm 薄 pod\n无感嵌入 Fitasy 鞋",PINK)]
sw=3.55; sgap=0.55; sx0=(13.333-(sw*3+sgap*2))/2; sy=2.2; sh=2.45
for i,(emo,ttl,desc,col) in enumerate(steps):
    x=sx0+i*(sw+sgap)
    rect(s,x,sy,sw,sh,fill=PANEL,line=col,lw=1.7)
    text(s,x,sy+0.28,sw,0.7,[[(emo,38,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,sy+1.25,sw,0.4,[[(ttl,14,col,True)]],align=PP_ALIGN.CENTER)
    text(s,x+0.15,sy+1.76,sw-0.3,0.62,[[(ln,11.5,DIM,False)] for ln in desc.split("\n")],align=PP_ALIGN.CENTER,lh=1.2,space=1)
    if i<2: arrow(s,x+sw+0.06,sy+sh/2-0.16,sgap-0.12,0.32,col=col)
cy=5.05
rect(s,0.7,cy,11.93,1.05,fill=PANEL2,line=ACC,lw=1.8)
text(s,1.0,cy+0.13,11.4,0.5,[[("🚀 建议:",15,ACC,True),("先用现成模块 + 定制中底凹槽,在 Fitasy 一款鞋上做一次真鞋联合试点,约定可验证小里程碑。",13.5,TXT,True)]])
text(s,1.0,cy+0.65,11.4,0.36,[[("商业模式与定价见完整版商业 deck。",11,DIM,False)]])
tag(s,6)

out="StrideSense_Tech_CN.pptx"; prs.save(out)
print("saved",out,"·",len(prs.slides._sldIdLst),"slides")
