#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phone 6-axis IMU diagram (EN): accelerometer (3-axis linear accel a) + gyroscope (3-axis angular rate ω). -> figs/imu_sensors_en.png"""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch, Arc
from matplotlib import font_manager
for fp in ["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/STHeiti Medium.ttc"]:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        try: matplotlib.rcParams["font.family"]=font_manager.FontProperties(fname=fp).get_name()
        except Exception: pass
        break
matplotlib.rcParams["axes.unicode_minus"]=False
BG="#0b0e14"; PANEL="#141a24"; LINE="#2a3445"; TXT="#e6edf3"; DIM="#9fb0c8"
ACC="#4cc2ff"; GOOD="#3fb950"; WARN="#e3b341"; PINK="#ff7aa8"; PURP="#b98cff"
XC="#f85149"; YC="#3fb950"; ZC="#4cc2ff"
os.makedirs("figs",exist_ok=True)

fig,ax=plt.subplots(figsize=(11.8,2.7),dpi=200); fig.patch.set_facecolor(BG)
ax.set_xlim(0,118); ax.set_ylim(0,24); ax.axis("off"); ax.set_facecolor(BG)

# ---- iPhone ----
ax.add_patch(FancyBboxPatch((4,4.5),10,15,boxstyle="round,pad=0,rounding_size=1.4",fc=PANEL,ec=ACC,lw=2))
ax.add_patch(Rectangle((5.6,6.6),6.8,10.4,fc="#0e2336",ec=ACC,lw=1))
ax.text(9,2.4,"iPhone · 6-axis IMU",ha="center",va="center",color=ACC,fontsize=13,fontweight="bold")
ax.text(20,12,"contains",ha="center",va="center",color=DIM,fontsize=12.5)
ax.add_patch(FancyArrowPatch((15,12),(25,12),arrowstyle="-|>",mutation_scale=18,lw=2.4,color=DIM))

# ---- accelerometer: three axes ----
cx,cy,L=37,12,6.4
ax.add_patch(Circle((cx,cy),0.6,fc=TXT,ec="none",zorder=5))
for (dx,dy,col,lab) in [(L,0,XC,"x"),(0,L,YC,"y"),(-L*0.62,-L*0.62,ZC,"z")]:
    ax.add_patch(FancyArrowPatch((cx,cy),(cx+dx,cy+dy),arrowstyle="-|>",mutation_scale=15,lw=2.8,color=col))
    ax.text(cx+dx*1.14,cy+dy*1.14,lab,ha="center",va="center",color=col,fontsize=13,fontweight="bold")
ax.text(cx,22.3,"Accelerometer",ha="center",va="center",color=TXT,fontsize=15.5,fontweight="bold")
ax.text(cx,2.2,"Linear accel  a = (ax, ay, az) · w/ gravity",ha="center",va="center",color=DIM,fontsize=12.5)

ax.text(57,12,"+",ha="center",va="center",color=DIM,fontsize=26,fontweight="bold")

# ---- gyroscope: three rotations ----
gx,gy=78,12
ax.add_patch(Arc((gx,gy),17,6.5,angle=0,theta1=0,theta2=300,color=ZC,lw=2.8))
ax.add_patch(Arc((gx,gy),6.5,17,angle=0,theta1=20,theta2=320,color=YC,lw=2.8))
ax.add_patch(Arc((gx,gy),13,13,angle=35,theta1=20,theta2=300,color=XC,lw=2.4,alpha=0.85))
ax.add_patch(FancyArrowPatch((gx+8.3,gy+0.6),(gx+8.2,gy-1.1),arrowstyle="-|>",mutation_scale=14,lw=2.6,color=ZC))
ax.add_patch(FancyArrowPatch((gx+0.6,gy+8.2),(gx-1.1,gy+8.0),arrowstyle="-|>",mutation_scale=14,lw=2.6,color=YC))
ax.add_patch(Circle((gx,gy),0.5,fc=TXT,ec="none",zorder=5))
ax.text(gx,22.3,"Gyroscope",ha="center",va="center",color=TXT,fontsize=15.5,fontweight="bold")
ax.text(gx,2.2,"Angular rate  ω = (ωx, ωy, ωz)",ha="center",va="center",color=DIM,fontsize=12.5)

# right note
ax.text(107,15,"~60 Hz",ha="center",va="center",color=WARN,fontsize=15,fontweight="bold")
ax.text(107,10,"6-axis: a + ω",ha="center",va="center",color=DIM,fontsize=13)

plt.tight_layout(pad=0.2); plt.savefig("figs/imu_sensors_en.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("saved figs/imu_sensors_en.png")
