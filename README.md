# 📱 Phone Motion Tracker

Use your phone's built-in **gyroscope + accelerometer** to reconstruct two things in real time:

1. **Rotation / orientation** (left view): however you turn the phone, the 3D phone on screen turns the same way. **Reliable, almost no drift.**
2. **In-air drawing trajectory** (right view): draws the path your hand traces through the air. **Shape is only recognizable for short gestures (2–4 seconds).**

A single `index.html`, zero external dependencies, pure Canvas rendering. Runs in both phone and desktop browsers.

---

## 🚀 Quickest start (same WiFi + self-signed HTTPS)

> iOS only prompts for motion sensor permission under **HTTPS (a secure context)**. Plain HTTP won't work.

On your computer (inside the project directory), run:

```bash
cd ~/phone-motion-tracker
python3 serve_https.py
```

The terminal will print something like:

```
Phone:  https://192.168.1.203:8443/        <- use this one
```

On your **phone (connected to the same WiFi)**, open that `https://192.168.1.203:8443/`.
If you hit "certificate is not trusted" → choose **Continue / Visit anyway** (this is normal for a self-signed certificate, and it's safe).

Then:

1. Tap **① Authorize and start sensors** (iOS will pop up a dialog; choose "Allow").
2. Lay the phone flat and still, then tap **② Calibrate gravity** (keep it still for about 1.5 seconds).
3. Tap **③ Start recording** → pick up the phone and **draw a circle / write a character in the air (2–4 seconds)** → tap **■ Stop recording**.
4. The right view shows the trajectory; **▶ Replay** animates it again; **⬇ Export JSON/CSV** saves the data.

---

## 🎛 Doesn't look right? Tune the parameters (the "Trajectory reconstruction parameters" at the bottom of the page)

After you stop recording, the whole dataset is reconstructed with a **start/end zero-velocity boundary constraint**. Changing parameters recomputes automatically; if you're not satisfied, just tap "↻ Rebuild" — no need to redraw.

| Parameter | What it does | How to adjust |
|------|------|----------|
| **Start/end stillness de-drift** (on by default) | Assumes the gesture starts and ends at rest, canceling out gravity residual / drift | Strongly recommended to keep checked |
| **Closed gesture** | Forces the start and end to connect | Check it when drawing circles / closed characters |
| **Smooth** | Moving-average denoising | Jittery → increase; blurry → decrease |
| leak / ZUPT / high-pass (collapsible section) | Only affects the real-time coarse preview during recording | Usually no need to touch |

Tip: **draw one gesture, then stop → clear → draw again** — don't draw continuously for a dozen seconds (it will definitely drift).

> Note: there's a "Gesture mode / Walking mode" switch at the top of the page. Everything above describes **Gesture mode** (short gestures, 2–4 seconds).

---

## 🚶 Walking mode (foot-strapped PDR) — good for demoing a walking trajectory

Switch to **🚶 Walking mode PDR** at the top, **strap the phone to the top of your foot / ankle** (screen facing outward, strapped tight), keep it still and ② calibrate,
then tap **▶ Start walking tracking** and walk normally. The right view draws the **ground path** in real time from a top-down view, and the top shows **step count + distance**.

**Why walking works but in-air drawing doesn't**: every step **is necessarily motionless at the moment the foot lands**, and the program automatically detects the landing and performs a **ZUPT zero-velocity update**,
zeroing out that step's drift on the spot → drift resets to zero every step instead of accumulating. This is the classic principle in inertial navigation behind "strap it to your foot, walk tens of meters, and the path still closes,"
and each step also applies an "end velocity = 0" boundary constraint to de-drift.

Landing-detection parameters (tune them in the walking panel when steps aren't detected / jump around erratically):

| Parameter | What it does | How to adjust |
|------|------|----------|
| **accTh** | Acceleration deviation threshold for landing | Steps not detected → increase |
| **gyroTh** | Gyroscope threshold for landing | Steps not detected → increase; counts steps while still → decrease |
| **Window N** | How many consecutive samples confirm a landing | Jitter misfires → increase |

⚠️ **Limitation**: the path's heading relies on the yaw angle, and with no magnetometer on the phone to correct it, yaw drifts slowly, so over a long walk the whole path gradually rotates.
A short-distance demo (one loop around a room) looks very accurate; over a long walk a square may not close completely.

### Gait analysis (updates in real time as you walk)

The "📊 Gait analysis" panel below Walking mode computes the following automatically for each stride:

- **Temporal**: stride frequency (strides/min, ≈½ step rate), stride time / gait cycle, swing time, stance phase ratio
- **Spatial**: gait speed (with 1.0/0.8/0.6 m/s health color scale), stride length, foot clearance (proxy)
- **Kinematics**: foot strike / toe-off inclination angle, peak swing angular velocity, heel-strike impact
- **Variability CV** (⭐ most clinically sensitive): coefficient of variation of stride time / stride length, green <3% yellow 3–6% red >6%, requires ≥12 strides to display
- **Turning**: number of turn steps, cumulative turn angle
- **Gray rows**: double support, step width, left/right symmetry — these can't be measured with one foot, and **require a second foot**

> Key point: a foot-strapped IMU swings only once per gait cycle = **one stride**, so all metrics are counted per stride; everyday step count ≈ 2× strides.
> Clinical CV thresholds are defined precisely per stride, so they can be compared directly. Walk 20–30 strides to give the CV enough samples, and when you're done you can "⬆ Upload gait data."

---

## ⬆️ Upload to the computer (let Claude analyze)

After recording a gesture, tap the green **⬆ Upload to computer** button to send the **raw world-frame linear acceleration + reconstructed trajectory** back to the computer running
`serve_https.py`, saved as `uploads/upload_NNN.json`. This lets you hand a real recording to Claude for offline
recomputation / diagnosis / parameter tuning. Data is only sent back when **you actively tap upload**; otherwise everything stays local on the phone.

---

## ⚠️ Physical limitations (an honest disclosure)

- **Orientation (rotation)** comes from the gyroscope + the vendor's orientation fusion, and is **reliable**.
- **Position (trajectory)** is a **double integration** of acceleration, so error accumulates **quadratically** over time.
  This tool uses "**world-frame gravity removal + high-pass bias removal + zero-velocity update (ZUPT) + velocity leak**" to make **short-gesture shapes recognizable**,
  but it is **not centimeter-accurate in scale**, and beyond ~5–10 seconds it will inevitably drift away.
- For true centimeter-level position, you need visual / magnetic / RF / UWB assistance (which is exactly the approach behind freehand-US-tracking).

---

## 🔬 Reconstruction principle (for people who want to modify the algorithm)

```
a_world = R(orientation) · a_device        # rotate gravity-inclusive accel into the world frame
a_lin   = a_world − g_world                # subtract calibrated world-frame gravity (constant, downward)
a_hp    = a_lin − EMA_slow(a_lin)          # high-pass to remove residual bias
v      += a_hp · dt · gain                 # integrate to velocity
  if stationary (|a_lin|<thr and slow rotation) persists: v = 0   # ZUPT
  else: v *= (1 − leak·dt)                 # velocity leak
p      += v · dt                           # integrate to position
```

- Euler orientation angles → rotation matrix: the W3C `deviceorientation` `ZXY` intrinsic-rotation convention (consistent with full-tilt.js).
- Gravity is **not assumed** to be `[0,0,9.81]`; instead the world-frame gravity vector is **measured during calibration** and then subtracted → automatically absorbing axis sign / unit differences.
- Unit auto-adaptation: if calibration measures `|g|≈1`, acceleration is judged to be in units of G, and is automatically multiplied by 9.81 to normalize to m/s².

---

## 📂 Exported data format

**JSON**: `{ meta:{rateHz, gWorld, unitScale, params}, samples:[...] }`
**CSV** columns: `t, alpha, beta, gamma, ax, ay, az, vx, vy, vz, px, py, pz`

- Angles in **degrees**; acceleration in **m/s²**; position in **m** (drift-sensitive); coordinate frame is the world frame (Z up).
- Can be fed directly into Python for offline recomputation / filtering experiments:

```python
import pandas as pd, matplotlib.pyplot as plt
df = pd.read_csv("motion_xxx.csv")
plt.plot(df.px, df.py); plt.axis("equal"); plt.show()   # top-down trajectory
```

---

## ❓ FAQ

- **No permission prompt / no sensor data**: make sure you opened it over `https://` (check whether there's a yellow warning bar at the top of the page); on iOS, "Settings → Safari → Motion & Orientation Access" must be enabled.
- **Certificate warning**: this is normal for a self-signed certificate; choose continue. To avoid the warning, you can use a tunnel like `cloudflared tunnel --url http://localhost:8000` (requires a separate install).
- **`acceleration` is empty on some Android models**: this tool uses `accelerationIncludingGravity` + world-frame gravity removal and doesn't depend on it, so it usually works fine.
- **The trajectory is flat / planar**: the right view defaults to the XY top-down view; you can switch to XZ / YZ to see other planes.
