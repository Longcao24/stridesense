#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Industry-style deck (7 slides): diagrams + real trajectory/CV visualizations + terminology + vision schematic."""
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
FONT="PingFang SC"

prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
BLANK=prs.slide_layouts[6]

def cjk(r,name=FONT):
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
            r=p.add_run(); r.text=t; r.font.size=Pt(sz); r.font.color.rgb=col; r.font.bold=bold; cjk(r)
    return tb
def pic(s,path,x,y,h=None,w=None):
    kw={}
    if h is not None: kw["height"]=Inches(h)
    if w is not None: kw["width"]=Inches(w)
    return s.shapes.add_picture(path,Inches(x),Inches(y),**kw)
def title(s,kicker,ttl):
    rect(s,0.55,0.46,0.10,0.58,fill=ACC,shape=MSO_SHAPE.RECTANGLE)
    text(s,0.8,0.4,12,0.4,[[(kicker,12,ACC,True)]])
    text(s,0.78,0.7,12.3,0.8,[[(ttl,26,TXT,True)]])
def tag(s,n): text(s,12.3,7.0,0.8,0.35,[[(str(n),11,DIM,False)]],align=PP_ALIGN.RIGHT)
def arrow(s,x,y,w,h=0.3):
    a=s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(x),Inches(y),Inches(w),Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb=ACC; a.line.fill.background(); a.shadow.inherit=False

# ===================================================== 1 Cover
s=slide()
rect(s,0,5.9,13.333,0.07,fill=ACC,shape=MSO_SHAPE.RECTANGLE)
text(s,0.9,1.85,11.5,0.5,[[("可穿戴感知  ·  智慧健康",16,ACC,True)]])
text(s,0.86,2.4,11.7,1.7,[[("一颗鞋载传感器,",42,TXT,True)],[("把每一步变成健康数据",42,TXT,True)]])
text(s,0.9,4.7,11.5,0.6,[[("足绑 IMU  ·  运动轨迹追踪  +  步态健康分析",18,DIM,False)]])
for i,(emo,lab) in enumerate([("👟","鞋载传感"),("🗺️","轨迹追踪"),("👣","步态分析")]):
    x=0.9+i*2.6
    text(s,x,6.15,1.2,0.7,[[(emo,30,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x-0.3,6.85,1.8,0.4,[[(lab,12,DIM,False)]],align=PP_ALIGN.CENTER)
text(s,9.3,6.95,3.2,0.4,[[("Xiaoyu Zhang · 2026",12,DIM,False)]],align=PP_ALIGN.RIGHT)

# ===================================================== 2 Feature 1: trajectory tracking (real figures)
s=slide(); title(s,"功能 ①","运动轨迹追踪 · 真实效果")
pic(s,"figs/fig_traj2d.png",0.55,1.55,h=4.55)            # 2D top-down view (hero)
text(s,0.55,6.2,5.6,0.5,[[("真实绕圈行走 → 自动闭合,室内无需 GPS",13,ACC,True)]],align=PP_ALIGN.CENTER)
pic(s,"figs/fig_traj3d.png",6.35,1.55,h=2.75)            # 3D
pic(s,"figs/fig_ui.png",10.65,1.55,h=2.75)              # real UI thumbnail
text(s,10.4,4.35,2.6,0.3,[[("↑ 实际 App 界面",10,DIM,False)]],align=PP_ALIGN.CENTER)
for i,(t,d) in enumerate([("走到哪 · 走多远","实时还原行走路径"),
                          ("2D / 3D 视图","可旋转查看立体轨迹"),
                          ("无需 GPS","室内可用 · 自动闭合")]):
    yy=4.75+i*0.62
    rect(s,6.4,yy+0.06,0.14,0.14,fill=ACC,shape=MSO_SHAPE.OVAL)
    text(s,6.72,yy-0.04,6.4,0.55,[[(t+"  ",15,TXT,True),(d,13,DIM,False)]])
tag(s,2)

# ===================================================== 3 Feature 2: gait analysis + CV explanation
s=slide(); title(s,"功能 ②","步态健康分析 · 看懂「变异性 CV」")
text(s,0.8,1.5,11.8,0.5,
     [[("可测 10+ 项:",14,GOOD,True),
       ("步频 · 步速 · 步长 · 支撑/摆动相 · 平衡 · 对称 · 足角度 · 着地冲击 · 转身",14,TXT,False)]])
pic(s,"figs/fig_cv.png",1.25,2.15,w=10.85)              # CV explanation figure (real healthy vs schematic unstable)
text(s,0.8,6.25,11.8,0.7,
     [[("CV(变异系数)= 步与步的波动程度。",14,ACC,True),
       (" 越低越稳;偏高常预示平衡变差、跌倒风险升高 —— 临床最看重的早期信号。",14,TXT,False)]])
tag(s,3)

# ===================================================== 4 Performance + terminology
s=slide(); title(s,"性能","性能表现")
tiles=[("~94%","轨迹闭合精度",ACC),("60 Hz","实时 · 零累积漂移",GOOD),
       ("10+","项步态参数",WARN),("GPS-free","室内 / 户外通用",PINK)]
tw,th,gap=2.85,2.35,0.28; x=(13.333-(tw*4+gap*3))/2
for big,lab,col in tiles:
    rect(s,x,1.85,tw,th,fill=PANEL,line=LINE)
    text(s,x,2.2,tw,1.0,[[(big,38,col,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    text(s,x,3.25,tw,0.6,[[(lab,15,TXT,False)]],align=PP_ALIGN.CENTER)
    x+=tw+gap
rect(s,1.6,4.5,10.13,0.85,fill=PANEL2,line=LINE)
text(s,1.9,4.6,9.6,0.7,
     [[("实测一圈:",14,ACC,True),
       ("约 6 米路线自动闭合,起终点仅差 35 cm(≈6%);步态周期稳定,CV≈3%;每步落地自动校正,误差不累积。",13,TXT,False)]],
     anchor=MSO_ANCHOR.MIDDLE)
rect(s,1.6,5.5,10.13,1.05,fill=PANEL,line=LINE)
text(s,1.9,5.62,9.6,0.9,
     [[("📖 术语:",13,WARN,True)],
      [("IMU = 惯性传感器(陀螺仪 + 加速度计);   CV = 变异系数 = 步与步波动 ÷ 平均,衡量步态稳定性。",13,DIM,False)]],
     anchor=MSO_ANCHOR.MIDDLE)
tag(s,4)

# ===================================================== 5 Application value
s=slide(); title(s,"价值","应用场景与价值")
apps=[("👴","老年照护","跌倒风险预警 · 衰弱评估",ACC),
      ("🏥","康复医疗","术后 / 卒中步态评估 · 疗效追踪",GOOD),
      ("🧠","神经疾病","帕金森随访 · 用药效果监测",PINK),
      ("🏃","运动健身","跑姿分析 · 伤病预防",WARN),
      ("📡","远程健康","居家长期监测 · 数字疗法",ACC),
      ("👟","智能穿戴","智能鞋 · 消费级健康数据",PURP)]
cw,ch,gx,gy=3.75,1.95,0.3,0.3; x0=(13.333-(cw*3+gx*2))/2
for i,(emo,t,d,col) in enumerate(apps):
    cx=x0+(i%3)*(cw+gx); cy=1.95+(i//3)*(ch+gy)
    rect(s,cx,cy,cw,ch,fill=PANEL,line=LINE)
    rect(s,cx,cy,0.09,ch,fill=col,shape=MSO_SHAPE.RECTANGLE)
    text(s,cx+0.28,cy+0.28,1.0,0.9,[[(emo,30,TXT,False)]])
    text(s,cx+1.25,cy+0.32,cw-1.4,0.5,[[(t,17,TXT,True)]])
    text(s,cx+1.25,cy+0.92,cw-1.4,0.8,[[(d,12.5,DIM,False)]])
tag(s,5)

# ===================================================== 6 Product roadmap
s=slide(); title(s,"路线","产品路线 · 精度与功能逐级提升")
stages=[("①","手机验证","算法已跑通\n可行性验证",GOOD,"✓ 已完成"),
        ("②","鞋载 6 轴 IMU","更小 · 低噪\n嵌入鞋内",ACC,"产品化"),
        ("③","升级 9 轴","加磁力计\n治朝向 · 长距离",PINK,"增强"),
        ("④","双鞋方案","步宽 · 双支撑\n左右对称",PURP,"临床级")]
bw,bh,gap=2.7,3.0,0.42; x=(13.333-(bw*4+gap*3))/2; y0=2.25
for i,(num,t,d,col,badge) in enumerate(stages):
    rect(s,x,y0,bw,bh,fill=PANEL,line=col,lw=1.5)
    text(s,x,y0+0.28,bw,0.7,[[(num,30,col,True)]],align=PP_ALIGN.CENTER)
    text(s,x,y0+1.0,bw,0.6,[[(t,16,TXT,True)]],align=PP_ALIGN.CENTER)
    text(s,x,y0+1.65,bw,0.9,[[(d,13,DIM,False)]],align=PP_ALIGN.CENTER)
    rect(s,x+bw/2-0.75,y0+bh-0.55,1.5,0.4,fill=col)
    text(s,x+bw/2-0.75,y0+bh-0.55,1.5,0.4,[[(badge,11,BG,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    if i<3: arrow(s,x+bw+0.04,y0+bh/2-0.15,gap-0.08)
    x+=bw+gap
text(s,0.85,5.85,11.6,0.6,[[("从可行性验证 → 专用硬件 → 临床级,功能与精度持续升级",15,DIM,False)]],align=PP_ALIGN.CENTER)
tag(s,6)

# ===================================================== 7 Vision (schematic)
s=slide(); title(s,"愿景","让步态成为健康的入口")
nodes=[("👟","鞋载 IMU","嵌入鞋 / 鞋垫\n无感佩戴",ACC),
       ("📊","轨迹 + 步态数据","实时 · 连续\n每一步都被记录",GOOD),
       ("❤️","健康洞察","风险预警 · 长期随访",PINK)]
nw,nh=3.3,2.5; gapn=0.95; x=(13.333-(nw*3+gapn*2))/2; y0=2.0
cxs=[]
for i,(emo,t,d,col) in enumerate(nodes):
    rect(s,x,y0,nw,nh,fill=PANEL,line=col,lw=1.5)
    text(s,x,y0+0.25,nw,0.9,[[(emo,40,TXT,False)]],align=PP_ALIGN.CENTER)
    text(s,x,y0+1.25,nw,0.5,[[(t,17,TXT,True)]],align=PP_ALIGN.CENTER)
    text(s,x,y0+1.78,nw,0.7,[[(d,12.5,DIM,False)]],align=PP_ALIGN.CENTER)
    cxs.append(x)
    if i<2: arrow(s,x+nw+0.12,y0+nh/2-0.16,gapn-0.24,0.32)
    x+=nw+gapn
# application chips hanging under health insights
chips=["跌倒预警","康复评估","疾病随访","运动表现"]
cx0=cxs[2]-0.0;
text(s,cxs[0],y0+nh+0.35,nw*3+gapn*2,0.5,
     [[("应用:  ",13,WARN,True),("  ·  ".join(chips),13,TXT,False)]],align=PP_ALIGN.CENTER)
text(s,0.85,6.5,11.6,0.6,[[("一步一数据 —— 让每一步,都成为健康数据。",18,ACC,True)]],align=PP_ALIGN.CENTER)
tag(s,7)

out="Phone_Motion_Gait_Slides.pptx"; prs.save(out)
print("saved",out,"·",len(prs.slides._sldIdLst),"slides")
