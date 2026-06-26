#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Intuitive illustration of the ZUPT principle: foot velocity is reset to zero at each footfall -> removes double-integration drift. -> figs/algo_zupt.png"""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
for fp in ["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/STHeiti Medium.ttc"]:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        try: matplotlib.rcParams["font.family"]=font_manager.FontProperties(fname=fp).get_name()
        except Exception: pass
        break
matplotlib.rcParams["axes.unicode_minus"]=False
BG="#0b0e14"; TXT="#e6edf3"; DIM="#9fb0c8"; ACC="#4cc2ff"; GOOD="#3fb950"; WARN="#e3b341"; BAD="#f85149"
os.makedirs("figs",exist_ok=True)

fig,ax=plt.subplots(figsize=(7.2,3.0),dpi=200); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
t=np.linspace(0,6,700)
v=np.abs(np.sin(np.pi*t))**1.3
ax.fill_between(t,0,v,color=ACC,alpha=0.22)
ax.plot(t,v,color=ACC,lw=2.4)
# Footfall points (integer steps) = velocity reset to zero, ZUPT
for k in range(0,7):
    ax.axvline(k,ls=(0,(3,3)),color=GOOD,lw=1.0,alpha=0.55)
    ax.plot(k,0,'o',color=GOOD,ms=8,zorder=5)
ax.annotate("着地:脚静止 → 速度 = 0\n→ ZUPT 把漂移清零",xy=(3,0),xytext=(3.05,0.42),
            color=GOOD,fontsize=10,ha="center",fontweight="bold",
            arrowprops=dict(arrowstyle="-|>",color=GOOD,lw=1.4))
ax.text(2.5,1.12,"摆动相:脚抬起,速度 > 0",color=ACC,fontsize=10,ha="center",fontweight="bold")
ax.set_xlim(0,6); ax.set_ylim(0,1.32)
ax.set_xlabel("时间(每整数 = 一步着地)",color=DIM,fontsize=9.5)
ax.set_ylabel("脚部速度 |v|",color=DIM,fontsize=9.5)
ax.tick_params(colors=DIM,labelsize=8); ax.set_xticks(range(0,7)); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_color("#2a3445")
ax.set_title("ZUPT(零速更新):每步着地把速度拉回 0,消除双积分漂移",color=TXT,fontsize=11.5,fontweight="bold",pad=8)
plt.tight_layout(); plt.savefig("figs/algo_zupt.png",facecolor=BG,bbox_inches="tight"); plt.close()
print("saved figs/algo_zupt.png")
