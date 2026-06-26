#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QFN physical illustrations + price tags for three mainstream commercial 6-axis IMUs, as a horizontal narrow strip with a dark theme. -> figs/chip_imu.png"""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
from matplotlib import font_manager
for fp in ["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/STHeiti Medium.ttc"]:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        try: matplotlib.rcParams["font.family"]=font_manager.FontProperties(fname=fp).get_name()
        except Exception: pass
        break
matplotlib.rcParams["axes.unicode_minus"]=False
os.makedirs("figs",exist_ok=True)
BG="#0b0e14"; PCB="#15321f"; PCBE="#2f6b40"; BODY="#16181d"; BODYE="#3a3f49"
PAD="#c9ced6"; TXT="#e6edf3"; DIM="#9fb0c8"; ACC="#4cc2ff"

chips=[("ICM-42688-P","TDK InvenSense","$1.5–3 @1k","TDK","42688"),
       ("LSM6DSO","STMicroelectronics","$2–4 @1k","ST","6DSO"),
       ("BMI270","Bosch Sensortec","$2.5–4 @1k","BOSCH","270")]

fig,axes=plt.subplots(1,3,figsize=(12.6,2.15),dpi=200); fig.patch.set_facecolor(BG)
for ax,(part,brand,price,l1,l2) in zip(axes,chips):
    ax.set_xlim(0,2); ax.set_ylim(0,1); ax.axis("off"); ax.set_facecolor(BG)
    # PCB pad (left)
    ax.add_patch(FancyBboxPatch((0.10,0.10),0.74,0.80,boxstyle="round,pad=0,rounding_size=0.05",fc=PCB,ec=PCBE,lw=1.4))
    bx,by,bw,bh=0.27,0.24,0.40,0.52
    npx,npy=7,7
    for i in range(npx):
        t=bx+0.035+(bw-0.07)*i/(npx-1)
        ax.add_patch(Rectangle((t-0.011,by-0.05),0.022,0.055,fc=PAD,ec="none"))
        ax.add_patch(Rectangle((t-0.011,by+bh-0.005),0.022,0.055,fc=PAD,ec="none"))
    for i in range(npy):
        u=by+0.04+(bh-0.08)*i/(npy-1)
        ax.add_patch(Rectangle((bx-0.05,u-0.011),0.055,0.022,fc=PAD,ec="none"))
        ax.add_patch(Rectangle((bx+bw-0.005,u-0.011),0.055,0.022,fc=PAD,ec="none"))
    ax.add_patch(FancyBboxPatch((bx,by),bw,bh,boxstyle="round,pad=0,rounding_size=0.035",fc=BODY,ec=BODYE,lw=1.3))
    ax.add_patch(Circle((bx+0.06,by+bh-0.07),0.018,fc=DIM,ec="none"))
    ax.text(bx+bw/2,by+bh/2+0.07,l1,ha="center",va="center",color="#cfd6e0",fontsize=8.5,fontweight="bold")
    ax.text(bx+bw/2,by+bh/2-0.07,l2,ha="center",va="center",color="#aeb6c2",fontsize=9.5,fontweight="bold")
    # right text
    ax.text(0.98,0.80,part,ha="left",va="center",color=TXT,fontsize=13,fontweight="bold")
    ax.text(0.98,0.585,brand,ha="left",va="center",color=DIM,fontsize=8.5)
    ax.text(0.98,0.40,"16-bit · ±16g · ±2000dps · 3×3mm",ha="left",va="center",color=DIM,fontsize=7.8)
    ax.add_patch(FancyBboxPatch((0.98,0.10),0.66,0.18,boxstyle="round,pad=0,rounding_size=0.06",fc="#10243a",ec=ACC,lw=1.1))
    ax.text(1.31,0.19,price,ha="center",va="center",color=ACC,fontsize=10.5,fontweight="bold")
plt.tight_layout(pad=0.3)
plt.savefig("figs/chip_imu.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("saved figs/chip_imu.png")
