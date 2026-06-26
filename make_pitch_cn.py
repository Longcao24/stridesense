#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""StrideSense — Chinese review edition v4 (11 pages). Removed the parallel-market page; added chip product photos + pricing; revised the gait-speed / foot-clearance / trajectory application sections."""
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
FONT="PingFang SC"; NTOT=11

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
    text(s,0.78,0.66,12.4,0.7,[[(ttl,23,TXT,True)]])
def tag(s,n): text(s,9.6,7.08,3.1,0.3,[[("StrideSense  ·  "+str(n)+"/"+str(NTOT),9.5,DIM,False)]],align=PP_ALIGN.RIGHT)
def arrow(s,x,y,w,h=0.3,col=ACC):
    a=s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x),Inches(y),Inches(w),Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb=col; a.line.fill.background(); a.shadow.inherit=False
def node(s,x,y,w,h,emo,label,col,es=40,ls=13.5):
    rect(s,x,y,w,h,fill=PANEL,line=col,lw=1.6)
    text(s,x,y+h*0.13,w,h*0.5,[[(emo,es,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,y+h*0.64,w,h*0.34,[[(label,ls,TXT,True)]],align=PP_ALIGN.CENTER)
def chip(s,x,y,w,h,emo,label,col=LINE,tcol=TXT,fs=11.5,bold=True):
    rect(s,x,y,w,h,fill=PANEL2,line=col,lw=1.1)
    pre=[(emo+"  ",fs+2,TXT,False)] if emo else []
    text(s,x+0.1,y,w-0.16,h,[pre+[(label,fs,tcol,bold)]],anchor=MSO_ANCHOR.MIDDLE)
def keyline(s,txt,col=ACC,y=6.5,fs=13):
    rect(s,0.7,y,11.93,0.6,fill=PANEL2,line=col,lw=1.2)
    text(s,0.95,y,11.45,0.6,[[(txt,fs,TXT,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
def corow(s,y,emo,name,setting,feat,benefit,col,h=0.84):
    rect(s,0.7,y,11.93,h,fill=PANEL,line=LINE,lw=1.0)
    rect(s,0.7,y,0.09,h,fill=col,shape=MSO_SHAPE.RECTANGLE)
    text(s,0.95,y,0.7,h,[[(emo,24,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE)
    text(s,1.7,y+0.1,2.55,h-0.2,[[(name,12.5,TXT,True)],[(setting,9.5,DIM,False)]],anchor=MSO_ANCHOR.MIDDLE,lh=1.1,space=1)
    text(s,4.45,y,3.95,h,[[(feat,11,col,True)]],anchor=MSO_ANCHOR.MIDDLE,lh=1.12)
    text(s,8.6,y,3.9,h,[[("→ ",11,DIM,True),(benefit,11,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE,lh=1.12)
def pcard(s,x,y,w,h,emo,name,benefit,feats,col):
    rect(s,x,y,w,h,fill=PANEL,line=col,lw=1.5)
    cd=0.92
    rect(s,x+(w-cd)/2,y+0.2,cd,cd,fill=PANEL2,line=col,lw=1.4,shape=MSO_SHAPE.OVAL)
    text(s,x+(w-cd)/2,y+0.2,cd,cd,[[(emo,32,TXT,False)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    text(s,x+0.08,y+1.22,w-0.16,0.46,[[(name,11.5,TXT,True)]],align=PP_ALIGN.CENTER,lh=1.0)
    text(s,x+0.1,y+1.74,w-0.2,1.05,[[(ln,13,col,True)] for ln in benefit.split("\n")],align=PP_ALIGN.CENTER,lh=1.15,space=2)
    rect(s,x+0.32,y+h-0.86,w-0.64,0.02,fill=LINE,shape=MSO_SHAPE.RECTANGLE)
    text(s,x+0.1,y+h-0.74,w-0.2,0.66,[[("测 ",8.5,col,True),(feats,8.5,DIM,False)]],align=PP_ALIGN.CENTER,lh=1.08)

# ===================================================== 1 Cover
s=slide()
rect(s,0,5.78,13.333,0.06,fill=ACC,shape=MSO_SHAPE.RECTANGLE)
text(s,0.9,1.5,11.5,0.5,[[("合作提案   ·   致 FITASY",13,ACC,True)]])
text(s,0.85,2.1,11.7,1.2,[[("StrideSense",60,TXT,True)]])
text(s,0.9,3.55,11.6,0.7,[[("让每一双 Stride 读懂穿者怎么走。",24,DIM,False)]])
for i,(emo,lab) in enumerate([("👟","可拆传感舱"),("🩹","运动康复"),("🏃","运动表现"),("✅","已验证")]):
    x=0.9+i*3.05
    text(s,x,6.05,2.9,0.5,[[(emo+"  ",18,TXT,False),(lab,13,DIM,True)]])
text(s,0.9,6.95,11.5,0.4,[[("张晓宇  ·  2026",12,DIM,False)]])

# ===================================================== 2 Product
s=slide(); title(s,"① 产品","一颗可拆传感舱,让鞋会「感知」")
n_w,n_h,g=3.0,2.3,0.85; x0=(13.333-(n_w*3+g*2))/2; y0=2.0
node(s,x0,y0,n_w,n_h,"👟","Stride + 传感舱槽",ACC)
node(s,x0+(n_w+g),y0,n_w,n_h,"🔌","可拆 6 轴 pod",GOOD)
node(s,x0+2*(n_w+g),y0,n_w,n_h,"📱","手机 App",PINK)
arrow(s,x0+n_w+0.12,y0+n_h/2-0.18,g-0.24,0.36,col=ACC)
arrow(s,x0+2*n_w+g+0.12,y0+n_h/2-0.18,g-0.24,0.36,col=GOOD)
pw=3.7; px=(13.333-(pw*3+0.3*2))/2; py=4.85
for i,(t) in enumerate(["贴合定制","单材料可回收","单只可售"]):
    chip(s,px+i*(pw+0.3),py,pw,0.64,"✓",t,col=LINE,tcol=DIM,fs=12.5)
keyline(s,"可拆设计 —— 加了传感,不动可回收性。",col=ACC,y=6.4)
tag(s,2)

# ===================================================== 3 Rehab cohorts (icon cards)
s=slide(); title(s,"② 运动康复人群","一图看懂:我们测什么 → 帮他们解决什么")
cohorts=[("🦵","ACL/半月板术后","回赛场\n有依据","LSI·单腿负荷·落地稳定",ACC),
         ("🦶","踝扭伤/反复崴脚","落地更稳\n少崴脚","落地稳定·对称·足倾角",WARN),
         ("🏃","跑步过劳伤","降负荷\n防复发","触地冲击·步频·落地角",PINK),
         ("🔁","伤后回归跑","回归进度\n看得见","跑量负荷·对称恢复",GOOD),
         ("🛡","过度训练/防伤","过载预警\n防伤","累计冲击·疲劳变形",PURP)]
cw=2.32; cg=0.24; x0=(13.333-(cw*5+cg*4))/2; cy=1.9; chh=3.7
for i,(emo,nm,bf,ft,col) in enumerate(cohorts):
    pcard(s,x0+i*(cw+cg),cy,cw,chh,emo,nm,bf,ft,col)
keyline(s,"共同点:把过去只有运动医学/步态实验室能测的指标,装进训练鞋,让回归赛场有数据可依。",col=GOOD,y=5.95)
tag(s,3)

# ===================================================== 4 Performance cohorts (icon cards)
s=slide(); title(s,"② 运动表现人群","一图看懂:我们测什么 → 帮他们解决什么")
cohorts=[("🏃","业余跑者/马拉松","改善跑姿\n破成绩","步频·触地·对称·轨迹",WARN),
         ("🏋","健身/健走减脂","从计步到\n步态质量","步态质量·室内轨迹·活动量",ACC),
         ("⚽","球类/团队项目","负荷管理\n表现分析","冲击负荷·失衡·跑动路径",PINK),
         ("🧒","青少年/青训","科学选材\n安全成长","跑姿发育·对称·负荷",GOOD),
         ("🥾","越野/徒步","地形适应\n体能分配","上下坡步态·地形负荷",PURP)]
cw=2.32; cg=0.24; x0=(13.333-(cw*5+cg*4))/2; cy=1.9; chh=3.7
for i,(emo,nm,bf,ft,col) in enumerate(cohorts):
    pcard(s,x0+i*(cw+cg),cy,cw,chh,emo,nm,bf,ft,col)
keyline(s,"鞋是唯一全程接触地面的入口:足部 IMU 比手表/手环更贴近真实发力。",col=WARN,y=5.95)
tag(s,4)

# ===================================================== 5 How to use
s=slide(); title(s,"③ 怎么用","穿上 · 走动 · 查看")
steps=[("👟","穿上",ACC),("🚶","正常走 / 跑",GOOD),("📶","BLE → 手机",PINK),("📊","看板",WARN),("🤝","分享",PURP)]
sw,g=2.28,0.2; x0=(13.333-(sw*5+g*4))/2; y0=2.2
for i,(e,t,col) in enumerate(steps):
    x=x0+i*(sw+g)
    rect(s,x,y0,sw,2.5,fill=PANEL,line=col,lw=1.4)
    text(s,x,y0+0.4,sw,0.9,[[(e,38,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,y0+1.6,sw,0.6,[[(str(i+1)+". "+t,15,TXT,True)]],align=PP_ALIGN.CENTER)
    if i<4: arrow(s,x+sw,y0+1.05,g,0.28,col=col)
keyline(s,"无需校准。可分享报告 = 打开 B2B(诊所/教练)的钥匙。",col=ACC,y=5.55)
tag(s,5)

# ===================================================== 6 Specs -> applications
s=slide(); title(s,"④ 规格 → 性能 → 应用 → 能做到什么程度","商用 6 轴 IMU:指标全可量化使用 —— 给绝对值 / 给精准变化幅度")
hw=["ICM-42688-P / LSM6DSO / BMI270","16-bit","±16 g","±2000 dps","ODR(采样率) 可达 ≥1 kHz"]
g=0.1; ws=[2.95,1.1,1.0,1.35,2.3]; xx=0.7; hy=1.42
for i,(t) in enumerate(hw):
    chip(s,xx,hy,ws[i],0.46,"",t,col=ACC,fs=10.5); xx+=ws[i]+g
text(s,9.5,1.42,3.2,0.46,[[("实体图与价格见硬件成本页",10,DIM,True)]],anchor=MSO_ANCHOR.MIDDLE)
hy=2.05; rect(s,0.7,hy,11.93,0.4,fill=PANEL2,line=LINE)
for (cx,cwd,t) in [(0.85,2.6,"指标"),(3.5,4.0,"可实现精度(到什么程度)"),(7.6,3.4,"对应应用"),(11.2,1.4,"能做到")]:
    text(s,cx,hy,cwd,0.4,[[(t,11,ACC,True)]],anchor=MSO_ANCHOR.MIDDLE)
rows=[("步频","±1–2 步/分","配速节奏 / 跑姿再训练",GOOD,"绝对值"),
      ("步长","±2–5%","步态对称 / 伤侧负荷",GOOD,"绝对值"),
      ("触地时间 GCT","±5–15 ms(需≥200Hz)","跑步经济 / 落地负荷不对称",GOOD,"绝对值"),
      ("支撑/摆动相","占空比 ±2–3%","步态周期 / 回归评估",GOOD,"绝对值"),
      ("步态变异 CV ◆","±0.5–1%","疲劳致变异↑ / 落地稳定性",GOOD,"绝对值"),
      ("左右对称 ◆◆","±2–4%(双脚差分)","ACL/踝术后 LSI · 伤侧负荷",GOOD,"绝对值"),
      ("步速","±3–8%","回归跑配速进展 · 训练配速",ACC,"变化幅度"),
      ("抬脚高度","±1–3 cm","疲劳拖步 / 越野·障碍廓清",ACC,"变化幅度"),
      ("足倾角","±1–3°触地/±3–8°摆动","落地角 / 鞋楦·鞋垫适配",ACC,"变化幅度"),
      ("运动轨迹 ◆","闭合误差 行程 1–5%","跑动路径 · 折返变向 · 场地热区",ACC,"变化幅度")]
yy=hy+0.43
for idx,(nm,ach,app,col,mt) in enumerate(rows):
    rect(s,0.7,yy,11.93,0.345,fill=PANEL if idx%2==0 else PANEL2,line=None)
    text(s,0.85,yy,2.6,0.345,[[(nm,9.5,TXT,True)]],anchor=MSO_ANCHOR.MIDDLE)
    text(s,3.5,yy,4.0,0.345,[[(ach,9,DIM,False)]],anchor=MSO_ANCHOR.MIDDLE)
    text(s,7.6,yy,3.6,0.345,[[(app,9,DIM,False)]],anchor=MSO_ANCHOR.MIDDLE)
    rect(s,11.24,yy+0.025,1.2,0.28,fill=col,line=col,lw=1.1)
    text(s,11.24,yy+0.005,1.2,0.30,[[(mt,9,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    yy+=0.35
text(s,0.7,yy+0.06,11.93,0.7,
  [[("绝对值",10,GOOD,True),(" = 直接给准确的绝对数值(例:步频 168 步/分);    ",9.5,DIM,False),
    ("变化幅度",10,ACC,True),(" = 同样可量化使用 —— 既显示绝对值,也给出「相比上次 / 对侧」的精准变化幅度。",9.5,DIM,False)],
   [("两类都完全能用。",9.5,TXT,True),("差别仅在:变化幅度类(高度/距离/角度/轨迹)绝对值略有波动、需一次校准,但「变化」精准 —— 像恒偏 2kg 的体重秤,称不准绝对值,「这周瘦 1kg」却很准。",9.5,DIM,False)],
   [("◆ = 我们已用手机实测;余为文献上界,需 pod 复核。异常/受限步态(术后跛行、极慢速)下 ZUPT 假设易失效,精度需重验。",9,WARN,True)]],lh=1.2,space=2)
tag(s,6)

# ===================================================== 7 Demo
s=slide(); title(s,"⑤ Demo · 真实步行验证","手机 6 轴绑脚已跑通(算法与商用 pod 通用)")
rect(s,0.7,1.42,11.93,0.5,fill=PANEL2,line=ACC,lw=1.1)
text(s,0.95,1.42,11.5,0.5,[[("CV(步态变异系数)",11.5,ACC,True),(" = 步与步的波动 ÷ 平均;越低越稳。运动中 CV 升高 = 疲劳 / 落地失稳的信号。",11.5,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE)
pic(s,"figs/fig_traj2d.png",0.7,2.05,h=2.95)
pic(s,"figs/fig_cv.png",4.32,2.74,w=4.6)
pic(s,"figs/fig_traj3d.png",9.05,2.05,h=2.95)
rect(s,0.7,5.2,11.93,0.62,fill=PANEL,line=ACC,lw=1.2)
text(s,0.7,5.2,11.93,0.62,[[("手机 → pod 升级:    ",10.5,ACC,True),
  ("同档传感器",10.5,GOOD,True),("    ·    ",10.5,DIM,False),
  ("采样率 100→≥500Hz",10.5,TXT,True),("    ·    ",10.5,DIM,False),
  ("软绑→刚性安装",10.5,TXT,True),("    ·    ",10.5,DIM,False),
  ("弱→硬时基同步",10.5,TXT,True)]],anchor=MSO_ANCHOR.MIDDLE,align=PP_ALIGN.CENTER)
text(s,0.7,5.98,11.93,0.42,[[("CV 图:",11,ACC,True),
  ("绿 = 你的真实步行(很稳,CV 2.6%);红 = 我做的「不稳」示意对照,",11,TXT,False),("不是你的数据。",11,WARN,True)]],anchor=MSO_ANCHOR.MIDDLE,align=PP_ALIGN.CENTER)
tag(s,7)

# ===================================================== 8 Value - hardware cost (+ chip product photos)
s=slide(); title(s,"⑥ 价值 · 硬件成本","商用 6 轴 IMU 仅几美元,一双双脚成本可控")
pic(s,"figs/chip_imu.png",1.15,1.35,w=11.0)   # photos of three mainstream IMUs + pricing
items=[("BLE MCU/模组","$2.5–4"),("电池 40–100mAh","$1.2–1.8"),("PCB+被动+电源","$2–3.5"),("外壳/防水","$0.8–1.5"),("装配+测试+校准","$1.5–3")]
cw,g=2.28,0.12; x0=(13.333-(cw*5+g*4))/2; y0=3.45
for i,(nm,c) in enumerate(items):
    x=x0+i*(cw+g)
    rect(s,x,y0,cw,0.78,fill=PANEL,line=LINE,lw=1.0)
    text(s,x,y0+0.1,cw,0.4,[[(nm,9.5,DIM,True)]],align=PP_ALIGN.CENTER,lh=1.0)
    text(s,x,y0+0.42,cw,0.32,[[(c,13,TXT,True)]],align=PP_ALIGN.CENTER)
rect(s,1.6,4.55,4.9,1.05,fill=PANEL,line=GOOD,lw=1.5)
text(s,1.6,4.66,4.9,0.4,[[("出厂直接成本(物料+装配)",11.5,GOOD,True)]],align=PP_ALIGN.CENTER)
text(s,1.6,5.05,4.9,0.5,[[("$9–15 / pod → $18–30 / 双",16,TXT,True)]],align=PP_ALIGN.CENTER)
rect(s,6.85,4.55,4.9,1.05,fill=PANEL,line=WARN,lw=1.5)
text(s,6.85,4.66,4.9,0.4,[[("落地成本(+模具/认证/物流/良率)",11.5,WARN,True)]],align=PP_ALIGN.CENTER)
text(s,6.85,5.05,4.9,0.5,[[("约 $30–45 / 双",16,TXT,True)]],align=PP_ALIGN.CENTER)
keyline(s,"对照 Smart-Stride 溢价 $99–199/双 —— 硬件每双净贡献毛利约 $60–150。",col=ACC,y=5.8)
text(s,0.7,6.62,11.93,0.35,[[("注:1k 量级采购价;未含渠道。均为示意,需与 Fitasy 共建真实报价。",9.5,DIM,False)]],align=PP_ALIGN.CENTER)
tag(s,8)

# ===================================================== 9 Value - business model (three icons: shoe -> App -> value-added)
s=slide(); title(s,"⑥ 价值 · 商业模式","买鞋赚硬件钱 · App 免费帮你卖鞋 · 增值服务赚经常性钱")
cards=[("👟","智能鞋 Smart-Stride",ACC,"硬件收入",
        [[("售价 ",10.5,DIM,False),("+$99–199 / 双",12,TXT,True)],
         [("成本 ",10.5,DIM,False),("出厂$18–30·落地$30–45",10.5,TXT,False)],
         [("毛利 ",10.5,DIM,False),("≈ $60–150 / 双",12,GOOD,True)]]),
       ("📱","手机 App",GOOD,"免费 = 卖鞋利器",
        [[("买鞋即会员",12,TXT,True),("(仅买鞋者)",9.5,DIM,False)],
         [("核心指标 ",10.5,DIM,False),("永久免费",12.5,GOOD,True)],
         [("步频·GCT·对称 LSI·CV",10.5,TXT,False)]]),
       ("🩺","增值服务",PINK,"经常性收入 · 毛利引擎",
        [[("个人 Pro ",10.5,DIM,False),("$7.99–9.99 / 月",12,TXT,True)],
         [("专业 B2B ",10.5,DIM,False),("$50–200 / 席·月",12,PINK,True)],
         [("运动医学 / 理疗 / 球队",10,DIM,False)]])]
cw=3.78; cg=0.55; x0=(13.333-(cw*3+cg*2))/2; cy=2.0; ch=3.4
for i,(emo,ttl,col,tg,lines) in enumerate(cards):
    x=x0+i*(cw+cg)
    rect(s,x,cy,cw,ch,fill=PANEL,line=col,lw=1.7)
    text(s,x,cy+0.18,cw,0.9,[[(emo,46,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,cy+1.08,cw,0.4,[[(ttl,15,col,True)]],align=PP_ALIGN.CENTER)
    text(s,x+0.2,cy+1.62,cw-0.4,1.2,lines,align=PP_ALIGN.CENTER,lh=1.3,space=5)
    rect(s,x+0.45,cy+ch-0.55,cw-0.9,0.42,fill=PANEL2,line=col,lw=1.0)
    text(s,x+0.4,cy+ch-0.55,cw-0.8,0.42,[[(tg,10.5,col,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    if i<2: arrow(s,x+cw+0.07,cy+ch/2-0.16,cg-0.14,0.32,col=col)
text(s,x0+cw,cy+ch/2-0.6,cg,0.3,[[("解锁",9.5,DIM,True)]],align=PP_ALIGN.CENTER)
text(s,x0+2*cw+cg,cy+ch/2-0.6,cg,0.3,[[("升级",9.5,DIM,True)]],align=PP_ALIGN.CENTER)
keyline(s,"软件帮你卖鞋:消费端免费、不靠订阅;经常性收入 = Pro + B2B(B2B 解耦,不被「买鞋」挡住)。",col=ACC,y=5.62)
text(s,0.7,6.48,11.93,0.4,[[("我们的回报 = 每双软件授权分成 + B2B 收入分成 → 投入随销量增长。",10,DIM,True)]],align=PP_ALIGN.CENTER)
tag(s,9)

# ===================================================== 10 Timeline (integration -> trial -> rollout)
s=slide(); title(s,"⑦ 时间线 · 三步走","集成验证 → 试用稳定 → 商业推广")
phs=[("🔧","① 集成 + 验证","0–4 月",ACC,
      [("👟","6 轴 pod 嵌入 Fitasy 鞋(共建舱槽)"),("🧪","实验室/跑步机受控测试·对照动捕"),("✅","验证精度:步频·GCT·LSI·CV·轨迹")]),
     ("👥","② 试用 + 稳定","4–8 月",GOOD,
      [("🏃","招测试者(跑者/伤后回归)长期试用"),("⏳","日常佩戴数周–数月·真实场景"),("✅","稳定可用:续航·蓝牙·耐久·数据一致")]),
     ("🚀","③ 商业推广","8–12 月",WARN,
      [("🛒","Smart-Stride 上市·渠道铺开"),("💰","会员 / Pro / B2B 变现开启"),("📈","规模·复购·订阅转化")])]
bw=3.92; g=0.24; x0=(13.333-(bw*3+g*2))/2; y0=1.85; bh=3.55
for i,(emo,ph,when,col,chips) in enumerate(phs):
    x=x0+i*(bw+g)
    rect(s,x,y0,bw,bh,fill=PANEL,line=col,lw=1.7)
    rect(s,x,y0,bw,0.5,fill=col,shape=MSO_SHAPE.RECTANGLE)
    text(s,x+0.2,y0,bw-1.4,0.5,[[(ph,13.5,BG,True)]],anchor=MSO_ANCHOR.MIDDLE)
    text(s,x+bw-1.25,y0,1.1,0.5,[[(when,11,BG,True)]],align=PP_ALIGN.RIGHT,anchor=MSO_ANCHOR.MIDDLE)
    text(s,x,y0+0.6,bw,0.92,[[(emo,42,TXT,False)]],align=PP_ALIGN.CENTER)
    ccy=y0+1.72
    for ic,txt in chips:
        rect(s,x+0.25,ccy,bw-0.5,0.52,fill=PANEL2,line=LINE,lw=0.8)
        text(s,x+0.42,ccy,bw-0.62,0.52,[[(ic+"  ",12.5,col,False),(txt,10,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE,lh=1.0)
        ccy+=0.58
    if i<2: arrow(s,x+bw+0.03,y0+bh/2-0.15,g-0.08,0.3,col=col)
keyline(s,"投入随阶段递进:先验证「测得准」→ 再验证「用得稳」→ 才商业推广,风险可控。",col=ACC,y=5.7)
tag(s,10)

# ===================================================== 11 The ask
s=slide(); title(s,"我们的请求","对你核心低风险,平台高回报")
rect(s,0.9,1.7,5.2,1.6,fill=PANEL,line=PINK,lw=1.5)
text(s,0.9,1.85,5.2,0.5,[[("Fitasy 拥有",15,PINK,True)]],align=PP_ALIGN.CENTER)
text(s,1.1,2.4,4.8,0.8,[[("鞋 · 品牌 · 渠道 · 客户",13,TXT,False)]],align=PP_ALIGN.CENTER)
rect(s,7.23,1.7,5.2,1.6,fill=PANEL,line=ACC,lw=1.5)
text(s,7.23,1.85,5.2,0.5,[[("我们拥有",15,ACC,True)]],align=PP_ALIGN.CENTER)
text(s,7.43,2.4,4.8,0.8,[[("传感 · 算法 · App · IP",13,TXT,False)]],align=PP_ALIGN.CENTER)
rect(s,6.05,2.2,1.2,0.7,fill=GOOD,shape=MSO_SHAPE.OVAL)
text(s,6.05,2.2,1.2,0.7,[[("🤝",20,BG,False)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
asks=[("🔧","共同设计\n传感舱槽",ACC),("👟","提供\n试点鞋",GOOD),("🔒","品类独占 +\n数据共管",PURP)]
aw,g=3.7,0.35; ax=(13.333-(aw*3+g*2))/2; ay=3.75
for i,(e,t,col) in enumerate(asks):
    x=ax+i*(aw+g)
    rect(s,x,ay,aw,1.5,fill=PANEL,line=col,lw=1.4)
    text(s,x+0.25,ay,1.1,1.5,[[(e,28,TXT,False)]],anchor=MSO_ANCHOR.MIDDLE)
    text(s,x+1.3,ay,aw-1.5,1.5,[[(ln,13.5,TXT,True)] for ln in t.split("\n")],anchor=MSO_ANCHOR.MIDDLE,lh=1.15,space=1)
keyline(s,"下一步:敲定传感舱槽 + 试点。投入可控、扩展弹性大。",col=ACC,y=5.7)
tag(s,11)

out="StrideSense_Pitch_CN.pptx"; prs.save(out)
print("saved",out,"·",len(prs.slides._sldIdLst),"slides")
