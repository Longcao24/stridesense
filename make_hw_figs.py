#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sensor hardware technical figures: (1) system block diagram (modules + price) (2) layered structure (3) in-shoe cross-section. Dark theme."""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch, Polygon, Arc
from matplotlib import font_manager
for fp in ["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/STHeiti Medium.ttc"]:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        try: matplotlib.rcParams["font.family"]=font_manager.FontProperties(fname=fp).get_name()
        except Exception: pass
        break
matplotlib.rcParams["axes.unicode_minus"]=False
os.makedirs("figs",exist_ok=True)
BG="#0b0e14"; PANEL="#141a24"; P2="#1b2330"; LINE="#2a3445"; TXT="#e6edf3"; DIM="#9fb0c8"
ACC="#4cc2ff"; GOOD="#3fb950"; WARN="#e3b341"; PINK="#ff7aa8"; PURP="#b98cff"; GREY="#6b7a90"; BAD="#f85149"

def box(ax,x,y,w,h,ec,title,sub=None,price=None,tfs=12,sfs=8.6,fc=PANEL):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0,rounding_size=1.4",fc=fc,ec=ec,lw=2.0))
    cy=y+h-(h*0.30 if (sub or price) else h*0.5)
    ax.text(x+w/2,y+h-h*0.27,title,ha="center",va="center",color=TXT,fontsize=tfs,fontweight="bold")
    if sub: ax.text(x+w/2,y+h*0.46,sub,ha="center",va="center",color=DIM,fontsize=sfs,linespacing=1.35)
    if price: ax.text(x+w/2,y+h*0.16,price,ha="center",va="center",color=ec,fontsize=tfs-1.5,fontweight="bold")

def arrow(ax,p0,p1,col,label=None,lfs=8.5,rad=0.0,loff=(0,2.2)):
    ax.add_patch(FancyArrowPatch(p0,p1,arrowstyle="-|>",mutation_scale=14,lw=2.0,color=col,
        connectionstyle=f"arc3,rad={rad}",shrinkA=2,shrinkB=2))
    if label:
        mx,my=(p0[0]+p1[0])/2+loff[0],(p0[1]+p1[1])/2+loff[1]
        ax.text(mx,my,label,ha="center",va="center",color=DIM,fontsize=lfs)

# ============================== (1) System block diagram ==============================
def fig_block():
    fig,ax=plt.subplots(figsize=(12.8,5.0),dpi=200); fig.patch.set_facecolor(BG)
    ax.set_xlim(0,128); ax.set_ylim(0,50); ax.axis("off"); ax.set_facecolor(BG)
    # Waterproof enclosure, dashed bounding box
    ax.add_patch(FancyBboxPatch((2.5,3),98,44,boxstyle="round,pad=0,rounding_size=2.5",
        fc="none",ec=GREY,lw=1.6,linestyle=(0,(6,4))))
    ax.text(6,45.4,"防水外壳 TPU/PC · IP67 · $0.8–1.5",ha="left",va="center",color=GREY,fontsize=9.5,fontweight="bold")
    # Modules
    box(ax,8,27,28,13,ACC,"6 轴 IMU","ICM-42688-P / LSM6DSO\n16-bit·±16g·±2000dps","$1.5–4")
    box(ax,52,27,28,13,GOOD,"BLE SoC / MCU","nRF52832/840·BLE 5.x\n板载 ZUPT/步态算法","$4–5")
    box(ax,8,7,28,13,WARN,"锂电 LiPo","65 mAh(LP401230)\n续航数天·可充","$2–3.5")
    box(ax,52,7,28,13,PURP,"充电管理 PMIC","充电 IC + LDO 稳压\n5V→3.3/1.8V","$0.5–1")
    # PCB antenna (top-right) + charging port (bottom-right) small blocks
    box(ax,86,28,12.5,11,PINK,"PCB/陶瓷天线","板载/贴片","$0.3–0.5",tfs=10,sfs=7.5)
    box(ax,86,8,12.5,11,GREY,"磁吸充电","pogo-pin","$1–4.5",tfs=10.5,sfs=8)
    # Phone (right side, outside the enclosure)
    ax.add_patch(FancyBboxPatch((110,20),12,16,boxstyle="round,pad=0,rounding_size=1.6",fc=P2,ec=ACC,lw=2))
    ax.add_patch(Rectangle((112,23.5),8,9.2,fc="#0e2336",ec=ACC,lw=1))
    ax.text(116,15.5,"手机 App",ha="center",va="center",color=ACC,fontsize=10.5,fontweight="bold")
    # Connections
    arrow(ax,(36,33.5),(52,33.5),ACC,"SPI / I²C",lfs=9)            # IMU->MCU data
    arrow(ax,(80,33.5),(86,33.5),GOOD,"RF",lfs=9)                   # MCU->antenna
    # Antenna -> phone (BLE waves)
    for k,r in enumerate([2.2,3.4,4.6]):
        ax.add_patch(Arc((99.5,33.5),r*2,r*2,angle=0,theta1=-55,theta2=55,color=PINK,lw=1.6))
    ax.text(105.5,39.5,"BLE 5.x",ha="center",va="center",color=PINK,fontsize=9)
    arrow(ax,(101.5,30),(110,27),PINK,None,rad=-0.15)
    # Power: battery->PMIC, charging port->PMIC, PMIC->IMU/MCU
    arrow(ax,(36,13.5),(52,13.5),WARN,"3.7V",lfs=9)                 # battery->PMIC
    arrow(ax,(86,13.5),(80,13.5),GREY,"5V",lfs=9)                   # charging->PMIC
    arrow(ax,(60,20),(60,27),PURP,None,rad=0.0)                     # PMIC->MCU power
    arrow(ax,(56,20),(20,27),PURP,"供电 1.8/3.3V",lfs=8.5,rad=0.12,loff=(0,-2)) # PMIC->IMU
    # PCB footnote
    ax.text(64,1.0,"主板:柔性/刚性 PCB + 被动元件 + 装配测试 ≈ $3.5–6",ha="center",va="center",color=DIM,fontsize=9)
    plt.tight_layout(pad=0.2); plt.savefig("figs/pod_block.png",facecolor=BG,bbox_inches="tight"); plt.close()
    print("saved figs/pod_block.png")

# ============================== (2) Layered structure (exploded view) ==============================
def fig_explode():
    fig,ax=plt.subplots(figsize=(6.4,5.2),dpi=200); fig.patch.set_facecolor(BG)
    ax.set_xlim(0,64); ax.set_ylim(0,100); ax.axis("off"); ax.set_facecolor(BG)
    lx,lw=6,38
    layers=[(78,"上盖 · 防水外壳",GREY,P2),
            (55,"主 PCB(柔性/刚性)",ACC,PANEL),
            (32,"锂电 LiPo 40–100mAh",WARN,PANEL),
            (9,"下盖 · 防水外壳",GREY,P2)]
    for y,lab,ec,fc in layers:
        ax.add_patch(FancyBboxPatch((lx,y),lw,15,boxstyle="round,pad=0,rounding_size=1.8",fc=fc,ec=ec,lw=2))
        ax.text(lx+lw/2,y+11.5,lab,ha="center",va="center",color=TXT,fontsize=9.5,fontweight="bold")
    # Small component blocks on the PCB
    for cx,cl,cc in [(13,"IMU",ACC),(24,"MCU",GOOD),(34,"天线",PINK)]:
        ax.add_patch(Rectangle((cx,58),7.5,5,fc="#0e1a26",ec=cc,lw=1.5))
        ax.text(cx+3.75,60.5,cl,ha="center",va="center",color=cc,fontsize=7.2,fontweight="bold")
    # Dashed assembly arrows between layers
    for y in [73,50,27]:
        ax.add_patch(FancyArrowPatch((lx+lw/2,y),(lx+lw/2,y-4),arrowstyle="-|>",mutation_scale=11,
            lw=1.4,color=DIM,linestyle=(0,(2,2))))
    # Dimension annotation on the right
    ax.annotate("",xy=(48,9),xytext=(48,93),arrowprops=dict(arrowstyle="<->",color=DIM,lw=1.4))
    ax.text(50,51,"≈ 8 mm 厚",ha="left",va="center",color=DIM,fontsize=9,rotation=90)
    ax.text(32,97.5,"整舱 ≈ 25 × 20 × 8 mm · ~6 g · IP67",ha="center",va="center",color=ACC,fontsize=9.5,fontweight="bold")
    plt.tight_layout(pad=0.2); plt.savefig("figs/pod_explode.png",facecolor=BG,bbox_inches="tight"); plt.close()
    print("saved figs/pod_explode.png")

# ============================== (3) In-shoe cross-section ==============================
def fig_shoe():
    fig,ax=plt.subplots(figsize=(7.4,5.2),dpi=200); fig.patch.set_facecolor(BG)
    ax.set_xlim(0,100); ax.set_ylim(0,72); ax.axis("off"); ax.set_facecolor(BG)
    # Shoe upper (toe pointing right, single main instep peak, collar opening behind the instep)
    up=[(18,27),(88,27),(85,33),(74,44),(62,51),(56,49.5),(52,43),(48,43),(44,46),(40,44),(28,39),(20,30)]
    ax.add_patch(Polygon(up,closed=True,fc="#141d29",ec=ACC,lw=2,alpha=0.95))
    ax.text(70,37,"鞋面 upper",ha="center",va="center",color=ACC,fontsize=10,fontweight="bold")
    ax.text(50,46,"鞋口",ha="center",va="center",color=DIM,fontsize=8)
    # Midsole
    mid=[(16,20),(92,20),(93,27),(17,27)]
    ax.add_patch(Polygon(mid,closed=True,fc="#19222e",ec=LINE,lw=1.6))
    # Outsole (upturned toe)
    out=[(15,12),(82,11),(94,16),(92,20),(16,20),(13,16)]
    ax.add_patch(Polygon(out,closed=True,fc="#10151d",ec=GREY,lw=2))
    ax.text(66,23.4,"中底(EVA / 3D 打印晶格)",ha="center",va="center",color=DIM,fontsize=8.5)
    ax.text(62,15.4,"外底",ha="center",va="center",color=GREY,fontsize=8.5)
    # Heel slot + pod
    ax.add_patch(FancyBboxPatch((19,20.5),21,6.2,boxstyle="round,pad=0,rounding_size=0.7",
        fc="#0b0e14",ec=WARN,lw=1.8,linestyle=(0,(4,3))))
    ax.add_patch(FancyBboxPatch((21,21.2),17,4.9,boxstyle="round,pad=0,rounding_size=0.7",fc=P2,ec=GOOD,lw=2))
    ax.text(29.5,23.6,"可拆传感舱 pod",ha="center",va="center",color=GOOD,fontsize=9,fontweight="bold")
    ax.annotate("中底卡槽 · 可整体取出 / 换鞋复用",xy=(30,26.8),xytext=(40,33.5),color=WARN,fontsize=9,
        arrowprops=dict(arrowstyle="-|>",color=WARN,lw=1.5))
    # BLE from pod -> phone
    for r in [2.6,4.0,5.4]:
        ax.add_patch(Arc((38,26),r*2,r*2,angle=0,theta1=10,theta2=80,color=PINK,lw=1.5))
    ax.add_patch(FancyBboxPatch((80,46),12,18,boxstyle="round,pad=0,rounding_size=1.6",fc="#0e1a26",ec=ACC,lw=2))
    ax.add_patch(Rectangle((82,49),8,11,fc="#0e2336",ec=ACC,lw=1))
    ax.text(86,43.5,"手机 App",ha="center",va="center",color=ACC,fontsize=9.5,fontweight="bold")
    ax.add_patch(FancyArrowPatch((40,30),(79,50),arrowstyle="-|>",mutation_scale=13,lw=1.7,color=PINK,
        connectionstyle="arc3,rad=-0.34"))
    ax.text(66,40,"BLE 无线",ha="center",va="center",color=PINK,fontsize=9)
    # Footnote
    ax.text(50,5,"嵌入中底卡槽 · 可拆卸 · 防水 · 不影响鞋的单材料回收",ha="center",va="center",color=DIM,fontsize=9.5)
    plt.tight_layout(pad=0.2); plt.savefig("figs/shoe_integ.png",facecolor=BG,bbox_inches="tight"); plt.close()
    print("saved figs/shoe_integ.png")

fig_block(); fig_explode(); fig_shoe()
print("done")
