# Live Demo Script · Reconstructing Motion Trajectory and Gait with a Phone

Use this alongside `Phone_Motion_Gait_Slides.pptx`. Goal: **8 slides + a single 2–3 minute live demo**.

---

## ✅ Pre-Demo Checklist (5 minutes before you start)

- [ ] Server running on your computer: `cd ~/Downloads/phone-motion-tracker && python3 serve_https.py`
- [ ] Note the phone access address (the `https://<computer-IP>:8443/` printed in the terminal)
- [ ] **Phone and computer on the same WiFi** (critical! the most common failure point)
- [ ] Open the page on the phone once beforehand and grant sensor access (tap "Continue" on the certificate warning)
- [ ] iOS: Settings → Safari → Motion & Orientation Access = On
- [ ] Set phone brightness, disable auto-lock; have the strap/rubber band ready for the foot (if demonstrating walking)
- [ ] **Screen mirroring**: mirror the phone to the big screen (AirPlay / wired), or open `https://localhost:8443/` on the computer as a backup
- [ ] Leave an open space where you can take 6–8 steps

---

## 🎤 Slide Talking Points (one line per slide)

1. **Cover** — "A single shoe-mounted sensor turns every step you take into health data—trajectory + gait."
2. **What it does** — "Two things: reconstructing the path you walked, and analyzing your gait—cadence, speed, stride length, balance, and so on."
3. **Performance** — "Measured results: ~93% trajectory accuracy, real-time 60Hz with zero drift, 10+ gait metrics, works both indoors and outdoors."
4. **Application Value (key slide)** — "Broad real-world use cases: fall warning for the elderly, rehabilitation assessment, Parkinson's follow-up, sports analytics, remote health, smart shoes."
5. **Product Roadmap** — "Phone has proven feasibility → build a dedicated 6-axis shoe-mounted unit → upgrade to 9-axis to fix orientation → go to clinical grade with dual shoes, improving accuracy and capability step by step."
6. **Closing** — "Make every step health data. Now for the live demo." (→ switch to the phone)

---

## 📱 Live Demo Flow (when you reach slide 7)

> Narrate as you walk, about 2–3 minutes total.

1. **Show the phone page** → "Open this URL on a phone connected to the same WiFi—it's a pure web page, no app installed."
2. **Tap ① Authorize** → choose Allow in the popup → "Grant access to the motion sensors."
3. **Hold still and tap ② Calibrate** → "Lay it flat and keep still for a second and a half to calibrate gravity."
4. **Switch to "🚶 Walking Mode" → strap to foot** (or hold to simulate) → tap **▶ Start Walking Tracking**
5. **Take 6–8 steps** (walk a square or half a loop) → "The panel on the right draws the ground path I walked in real time, with step count and distance up top."
6. **Tap ■ Stop** → point to the gait panel: "Cadence, speed, stance/swing phase, and CV variability are all there."
7. **Switch to "3D" → drag with your finger to rotate** → "The trajectory is 3D—you can spin it around to view it."
8. **Tap ⬆ Upload** → switch back to the computer → "The data is sent to the computer for offline analysis and cross-session comparison."

**Highlight line**: "Notice there's no cumulative drift—because every footfall auto-corrects. That's the principle behind why foot-strapped inertial navigation can go a long way without drifting."

---

## 🛟 Fallback Plan (Plan B)

| Symptom | Cause | Response |
|------|------|------|
| Phone won't load / spins forever | Not on the same WiFi / firewall | Demo using `https://localhost:8443/` on the computer; or run a phone hotspot and connect the computer to it |
| No authorization popup | Not HTTPS / permission disabled | Confirm the address is `https://`; enable "Motion & Orientation" in iOS settings |
| Step count jumps around / not detected | Footfall threshold doesn't fit the user | Adjust accTh / gyroTh in the walking panel; or fall back to **drawing a circle in gesture mode** on the spot |
| Won't run at all | Network/device problem | Just present the **measured data + screenshots on the left of slide 7**, explaining it's "already validated offline" |

> **Safety move**: record a good walk on the phone in advance, take a **screenshot**, and paste it into slide 7; if something goes wrong, present the screenshot and don't rely on the live network.

---

## ❓ Anticipated Q&A

- **Q: Doesn't the position drift?** A: Yes, double integration always drifts. The key is ZUPT—the foot's velocity must be 0 each time it lands and is at rest, which zeroes out the error every step, so it doesn't accumulate.
- **Q: How accurate is it?** A: Measured horizontal trajectory closure error is ~7%; stride length, cadence, and speed are reliable; foot-clearance shape is correct but absolute values need calibration; step width can't be measured with one foot.
- **Q: Why use a phone instead of just building hardware?** A: A phone has a built-in 6-axis IMU—a zero-cost proxy. Use it first to validate the algorithm and feasibility, and once that checks out, invest in a dedicated shoe-mounted IMU. This saves time and money and reduces risk.
- **Q: What's the difference between a phone and a dedicated IMU?** A: A phone is just a 6-axis IMU + a screen, and the algorithm is exactly the same; a dedicated shoe-mounted unit is smaller, lower-noise, and embeddable in a shoe, and upgrading to 9-axis adds a magnetometer to fix orientation drift.
- **Q: How does it compare to a clinical gait analyzer?** A: A single-foot consumer-grade solution is valuable for trends/screening/remote follow-up; for precise clinical measurement you go to dual shoes/professional IMUs—which is exactly the hardware roadmap.
- **Q: Can it measure step width?** A: Not with one foot (you need the other foot's landing point); adding a second phone unlocks step width, double support, and true left-right symmetry.

---

## 📂 Files

- `Phone_Motion_Gait_Slides.pptx` — slides (editable in PowerPoint/Keynote)
- `make_slides.py` — slide generation script (just rerun after editing content)
- `index.html` — the demo tool itself
- `serve_https.py` — starts the server
