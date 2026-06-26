#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pod isometric exploded assembly view + component selection cards (real component photos). -> figs/pod_assembly.png"""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Polygon, FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import font_manager
for fp in ["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/STHeiti Medium.ttc"]:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        try: matplotlib.rcParams["font.family"]=font_manager.FontProperties(fname=fp).get_name()
        except Exception: pass
        break
matplotlib.rcParams["axes.unicode_minus"]=False
BG="#0b0e14"; PANEL="#141a24"; P2="#1b2330"; LINE="#2a3445"; TXT="#e6edf3"; DIM="#9fb0c8"
ACC="#4cc2ff"; GOOD="#3fb950"; WARN="#e3b341"; PINK="#ff7aa8"; PURP="#b98cff"; GREY="#6b7a90"; ORG="#ff7a3c"
BLUE_T="#2b4cb0"; BLUE_F="#1f3a8a"; BLUE_S="#16265e"  # enclosure
SIL_T="#4a505c"; SIL_F="#3a3f49"; SIL_S="#2a2f38"     # battery/metal
PCB_T="#163a5e"; PCB_F="#10243a"; PCB_S="#0b1a2c"; GOLD="#c8a032"

DX,DY=13.0,6.6   # isometric offset
def p(cx,cy,u,s):  # parametric point on PCB/layer top face
    return (cx+u+s*DX, cy+s*DY)
def iso_layer(ax,cx,cy,w,t,top,face,side,ec=LINE,lw=1.4):
    front=[(cx,cy),(cx+w,cy),(cx+w,cy-t),(cx,cy-t)]
    right=[(cx+w,cy),(cx+w+DX,cy+DY),(cx+w+DX,cy+DY-t),(cx+w,cy-t)]
    topf =[(cx,cy),(cx+w,cy),(cx+w+DX,cy+DY),(cx+DX,cy+DY)]
    ax.add_patch(Polygon(front,closed=True,fc=face,ec=ec,lw=lw))
    ax.add_patch(Polygon(right,closed=True,fc=side,ec=ec,lw=lw))
    ax.add_patch(Polygon(topf,closed=True,fc=top,ec=ec,lw=lw))
def iso_block(ax,cx,cy,u,s,du,ds,fc,ec,lw=1.6):  # small component block on top face (parallelogram)
    pts=[p(cx,cy,u-du,s-ds),p(cx,cy,u+du,s-ds),p(cx,cy,u+du,s+ds),p(cx,cy,u-du,s+ds)]
    ax.add_patch(Polygon(pts,closed=True,fc=fc,ec=ec,lw=lw))
def badge(ax,x,y,n,col,r=1.45,fs=11):
    ax.add_patch(Circle((x,y),r,fc=col,ec="none",zorder=5))
    ax.text(x,y,str(n),ha="center",va="center",color=BG,fontsize=fs,fontweight="bold",zorder=6)
def place_img(ax,path,x,y,disp_px=92):
    img=mpimg.imread(path); h=img.shape[0]
    ax.add_artist(AnnotationBbox(OffsetImage(img,zoom=disp_px/h),(x,y),frameon=False,zorder=4))
def qfn(ax,x,y,sz=3.2,col=ACC):  # for IMU card: draw a QFN package
    ax.add_patch(FancyBboxPatch((x-sz/2,y-sz/2),sz,sz,boxstyle="round,pad=0,rounding_size=0.3",fc="#16181d",ec=col,lw=1.6,zorder=4))
    for i in range(5):
        t=x-sz/2+0.45+(sz-0.9)*i/4
        ax.add_patch(Rectangle((t-0.12,y-sz/2-0.4),0.24,0.4,fc="#c9ced6",ec="none",zorder=4))
        ax.add_patch(Rectangle((t-0.12,y+sz/2),0.24,0.4,fc="#c9ced6",ec="none",zorder=4))
    ax.add_patch(Circle((x-sz/2+0.5,y+sz/2-0.5),0.18,fc=DIM,ec="none",zorder=5))

fig,ax=plt.subplots(figsize=(13.2,7.5),dpi=175); fig.patch.set_facecolor(BG)
ax.set_xlim(0,132); ax.set_ylim(0,78); ax.axis("off"); ax.set_facecolor(BG)

# ====== Left: isometric exploded stack ======
cx,w=10,30
# bottom cover (deep box) + pogo contacts
iso_layer(ax,cx,16,w,3.4,BLUE_T,BLUE_F,BLUE_S)
for i in range(5):  # gold pogo on the front
    ax.add_patch(Circle((cx+5+i*1.7,14.4),0.5,fc=GOLD,ec="#8a6d1f",lw=0.6,zorder=3))
# main PCB (thin, gold edge)
iso_layer(ax,cx,30,w,1.6,PCB_T,PCB_F,PCB_S,ec=GOLD,lw=1.3)
# PCB top-face components (orange block + green frame)
for (u,s,nm) in [(7,0.3,6),(16,0.5,4),(23,0.72,5),(25,0.28,7)]:
    iso_block(ax,cx,30,u,s,1.7,0.16,ORG,GOOD,lw=1.8)
# foam/shield
iso_layer(ax,cx,38,w,0.9,"#1a1d22","#111419","#0c0e11")
# battery (silver-grey)
iso_layer(ax,cx,46,w,2.4,SIL_T,SIL_F,SIL_S)
# top cover
iso_layer(ax,cx,58,w,3.4,BLUE_T,BLUE_F,BLUE_S)
ax.text(cx+w/2+DX/2,58+DY/2+0.3,"StrideSense",ha="center",va="center",color="#cfe0ff",fontsize=8,fontweight="bold",rotation=0,zorder=3)
# assembly guide dashed lines
for xr in [cx+6, cx+w-4]:
    ax.plot([xr,xr+DX*0.5],[16-3.4,62],ls=(0,(3,3)),color=GREY,lw=0.8,zorder=1)
# thickness annotation
ax.annotate("",xy=(cx-3,16-3.4),xytext=(cx-3,58+DY+0.2),arrowprops=dict(arrowstyle="<->",color=DIM,lw=1.3))
ax.text(cx-4.4,38,"整舱 ≈ 4 mm 厚",ha="center",va="center",color=ACC,fontsize=9.5,rotation=90,fontweight="bold")
# layer numbering (left side)
for (n,cy) in [(1,58+1.5),(2,46+1.0),(3,30+0.4),(8,16+0.5)]:
    badge(ax,cx-0.5,cy,n,{1:GREY,2:WARN,3:ACC,8:GREY}[n])
ax.text(cx+w+DX+1.5,58+DY-1,"① 上盖外壳",ha="left",va="center",color=DIM,fontsize=8.5)
ax.text(cx+w+DX+1.5,46+DY-1,"② 超薄电池",ha="left",va="center",color=DIM,fontsize=8.5)
ax.text(cx+w+DX+1.5,38+DY-0.5,"③ 泡棉/屏蔽",ha="left",va="center",color=DIM,fontsize=8.5)
ax.text(cx+w+DX+1.5,30+DY-1,"④⑤⑥⑦ 主 PCB + 元件",ha="left",va="center",color=GOOD,fontsize=8.5,fontweight="bold")
ax.text(cx+w+DX+1.5,16+DY-1,"⑧ 下盖 + 磁吸 pogo 充电",ha="left",va="center",color=DIM,fontsize=8.5)
ax.text(cx+2,75.5,"爆炸装配结构",ha="left",va="center",color=TXT,fontsize=13,fontweight="bold")

# ====== Right: component selection cards ======
ax.text(66,75.5,"重要组件选型(真实型号 · 实物图 · 价格)",ha="left",va="center",color=TXT,fontsize=12.5,fontweight="bold")
P="figs/parts/"
cards=[  # (col,row, n, ncol, category, model, spec, price, image type, image)
 (1,"① 外壳上盖","防水 TPU/PC · IP67","注塑定制",GREY,"swatch",BLUE_T),
 (2,"② 超薄电池","软包 LiPo 例 GM171452","90mAh · 1.7mm","$2–3.5",WARN,"img",P+"batt.png"),
 (3,"③ 主 PCB","柔性/刚柔 + 被动元件","0.3mm","$3.5–6",ACC,"swatch",PCB_T),
 (4,"④ 6 轴 IMU","Bosch BMI270","±16g·±2000dps·0.8mm","$1.5–4",GOOD,"qfn",None),
 (5,"⑤ BLE SoC","Nordic nRF52840","M4F·BLE5.x·WLCSP 0.8mm","$4.5",ACC,"img",P+"ble.jpg"),
 (6,"⑥ 2.4G 天线","Johanson 2450AT18B100E","陶瓷贴片·1206","$0.4",PINK,"img",P+"antenna.jpg"),
 (7,"⑦ 充电+稳压","MCP73831 + TPS7A0233","≤500mA + 3.3V/Iq25nA","$0.7–1.1",PURP,"img",P+"charger.jpg"),
 (8,"⑧ 磁吸充电口","ATTEND 303D-D080M02","2-pin pogo · Φ8mm","$4.0",GREY,"img",P+"pogo.jpg"),
]
# fix card tuple structure (unified to 8 fields)
cards=[
 ("① 外壳上盖","防水 TPU/PC · IP67","注塑定制","",GREY,"swatch",BLUE_T),
 ("⑤ BLE SoC","Nordic nRF52840","M4F·BLE5.x·WLCSP 0.8mm","$4.5",ACC,"img",P+"ble.jpg"),
 ("② 超薄电池","软包 LiPo 例 GM171452","90mAh · 1.7mm 厚","$2–3.5",WARN,"img",P+"batt.png"),
 ("⑥ 2.4G 天线","Johanson 2450AT18B100E","陶瓷贴片 · 1206","$0.4",PINK,"img",P+"antenna.jpg"),
 ("③ 主 PCB","柔性/刚柔 + 被动","0.3mm 基板","$3.5–6",ACC,"swatch",PCB_T),
 ("⑦ 充电 + 稳压","MCP73831 + TPS7A0233","≤500mA · 3.3V/Iq25nA","$0.7–1.1",PURP,"img",P+"charger.jpg"),
 ("④ 6 轴 IMU","Bosch BMI270","±16g·±2000dps·0.8mm","$1.5–4",GOOD,"qfn",None),
 ("⑧ 磁吸充电口","ATTEND 303D-D080M02","2-pin pogo · Φ8mm","$4.0",GREY,"img",P+"pogo.jpg"),
]
colx=[66,99.5]; cw=31; ch=13.0
rowy=[57,42,27,12]
for i,(cat,part,spec,price,col,kind,arg) in enumerate(cards):
    c=colx[i%2]; r=rowy[i//2]
    ax.add_patch(FancyBboxPatch((c,r),cw,ch,boxstyle="round,pad=0,rounding_size=0.8",fc=PANEL,ec=col,lw=1.4,zorder=2))
    ax.add_patch(Rectangle((c,r),0.5,ch,fc=col,ec="none",zorder=3))
    ix,iy=c+7.0,r+ch/2
    if kind=="img": place_img(ax,arg,ix,iy,disp_px=82)
    elif kind=="qfn": qfn(ax,ix,iy,sz=5.0,col=col)
    else:
        ax.add_patch(FancyBboxPatch((ix-3,iy-3),6,6,boxstyle="round,pad=0,rounding_size=0.5",fc=arg,ec=col,lw=1.4,zorder=4))
    tx=c+13.0
    ax.text(tx,r+ch-2.7,cat,ha="left",va="center",color=col,fontsize=9.6,fontweight="bold")
    ax.text(tx,r+ch-5.7,part,ha="left",va="center",color=TXT,fontsize=10.0,fontweight="bold")
    ax.text(tx,r+ch-8.4,spec,ha="left",va="center",color=DIM,fontsize=7.6)
    if price: ax.text(c+cw-1.2,r+1.7,price,ha="right",va="center",color=col,fontsize=10.5,fontweight="bold")

ax.text(66,5.2,"整舱 ≈ 25×20×4 mm · ~6 g · IP67 · BOM $15–22/pod。组件实物图来源 LCSC/厂商官网,仅作选型示意。",
        ha="left",va="center",color=DIM,fontsize=8)
os.makedirs("figs",exist_ok=True)
plt.subplots_adjust(left=0,right=1,top=1,bottom=0)
plt.savefig("figs/pod_assembly.png",facecolor=BG,bbox_inches="tight",pad_inches=0.12); plt.close()
print("saved figs/pod_assembly.png")
