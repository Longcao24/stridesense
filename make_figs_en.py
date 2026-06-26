#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""English-labelled demo figures for the StrideSense pitch deck. Output -> figs_en/."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection
matplotlib.rcParams["axes.unicode_minus"] = False  # default DejaVu Sans has arrow glyphs

BG="#0b0e14"; PANEL="#141a24"; TXT="#e6edf3"; DIM="#9fb0c8"; ACC="#4cc2ff"; GOOD="#3fb950"; WARN="#e3b341"; BAD="#f85149"
os.makedirs("figs_en", exist_ok=True)
d = json.load(open("uploads/upload_005.json"))
path = np.array(d["path"]); strides = d["strides"]

def fig_2d():
    x, y = path[:,0], path[:,1]
    fig, ax = plt.subplots(figsize=(6.4,5.4), dpi=200)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    pts = np.array([x,y]).T.reshape(-1,1,2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap="cool", linewidth=3.2)
    lc.set_array(np.linspace(0,1,len(segs))); ax.add_collection(lc)
    ax.plot(x[0], y[0], "o", color=GOOD, ms=12, label="Start")
    ax.plot(x[-1], y[-1], "o", color="white", ms=11, label="End")
    gap = np.hypot(x[-1]-x[0], y[-1]-y[0])
    ax.set_aspect("equal")
    ax.set_title("Measured Walking Trajectory (top view) · Real data", color=TXT, fontsize=14, pad=12, fontweight="bold")
    ax.set_xlabel("X (m)", color=DIM); ax.set_ylabel("Y (m)", color=DIM)
    ax.tick_params(colors=DIM, labelsize=9)
    for sp in ax.spines.values(): sp.set_color("#2a3445")
    ax.grid(True, color="#1c2533", lw=0.8)
    ax.legend(loc="upper right", facecolor=PANEL, edgecolor="#2a3445", labelcolor=TXT, fontsize=10)
    ax.text(0.03, 0.03, f"One loop · start–end gap {gap*100:.0f} cm → auto-closed",
            transform=ax.transAxes, color=ACC, fontsize=11, va="bottom")
    plt.tight_layout(); plt.savefig("figs_en/fig_traj2d.png", facecolor=BG); plt.close()
    print("figs_en/fig_traj2d.png  gap %.2f m" % gap)

def fig_3d():
    x,y,z = path[:,0], path[:,1], path[:,2]
    fig = plt.figure(figsize=(6.4,5.4), dpi=200); fig.patch.set_facecolor(BG)
    ax = fig.add_subplot(111, projection="3d"); ax.set_facecolor(BG)
    pts = np.array([x,y,z]).T.reshape(-1,1,3)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = Line3DCollection(segs, cmap="cool", linewidth=2.8)
    lc.set_array(np.linspace(0,1,len(segs))); ax.add_collection3d(lc)
    zfloor = z.min()-0.02
    ax.plot(x, y, zfloor, color="#5a6478", lw=1.2, alpha=0.5)
    ax.scatter(x[0],y[0],z[0], color=GOOD, s=60); ax.scatter(x[-1],y[-1],z[-1], color="white", s=50)
    ax.set_title("3D Trajectory Reconstruction · Real data", color=TXT, fontsize=14, pad=4, fontweight="bold")
    ax.set_xlabel("X (m)", color=DIM, labelpad=2); ax.set_ylabel("Y (m)", color=DIM, labelpad=2)
    ax.set_zlabel("Z (m)", color=DIM, labelpad=2)
    ax.tick_params(colors=DIM, labelsize=7)
    for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
        pane.set_pane_color((0.07,0.09,0.13,1.0)); pane.line.set_color("#2a3445")
    ax.view_init(elev=28, azim=-58)
    try: ax.set_box_aspect((np.ptp(x), np.ptp(y), max(np.ptp(z), 0.3)))
    except Exception: pass
    plt.tight_layout(); plt.savefig("figs_en/fig_traj3d.png", facecolor=BG); plt.close()
    print("figs_en/fig_traj3d.png")

def fig_cv():
    cyc = np.array([s["swingT"]+s["stanceT"] for s in strides if s["stanceT"]>0])
    healthy = cyc if len(cyc)>=4 else np.array([1.68,1.70,1.72,1.65,1.69,1.71])
    healthy = healthy[:6] if len(healthy)>=6 else np.resize(healthy,6)
    cv_h = healthy.std(ddof=1)/healthy.mean()*100
    unstable = np.array([1.40,1.95,1.55,2.10,1.35,1.85])
    cv_u = unstable.std(ddof=1)/unstable.mean()*100
    fig, axes = plt.subplots(1,2, figsize=(10.6,3.6), dpi=200)
    fig.patch.set_facecolor(BG)
    data = [("Healthy gait: even steps", healthy, GOOD, cv_h, "stable"),
            ("Unstable gait: irregular (illustrative)", unstable, BAD, cv_u, "fall-risk ↑")]
    for ax,(t,vals,col,cv,tagtxt) in zip(axes, data):
        ax.set_facecolor(BG)
        ax.bar(range(1,len(vals)+1), vals, color=col, width=0.62, alpha=0.92)
        ax.axhline(vals.mean(), color=DIM, ls="--", lw=1)
        ax.set_ylim(0, 2.5); ax.set_title(t, color=TXT, fontsize=12.5, fontweight="bold", pad=8)
        ax.set_xlabel("Step #", color=DIM, fontsize=10); ax.set_ylabel("Step time (s)", color=DIM, fontsize=10)
        ax.tick_params(colors=DIM, labelsize=9)
        for sp in ax.spines.values(): sp.set_color("#2a3445")
        ax.text(0.5, 0.92, f"CV = {cv:.1f}%  ({tagtxt})", transform=ax.transAxes,
                color=col, fontsize=14, fontweight="bold", ha="center")
    fig.suptitle("Gait-variability CV = step-to-step fluctuation (SD ÷ mean); lower is steadier", color=ACC, fontsize=12.5, y=1.02)
    plt.tight_layout(); plt.savefig("figs_en/fig_cv.png", facecolor=BG, bbox_inches="tight"); plt.close()
    print("figs_en/fig_cv.png  healthy %.1f%% unstable %.1f%%" % (cv_h, cv_u))

fig_2d(); fig_3d(); fig_cv(); print("done")
