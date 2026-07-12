# Motion Tracker Mobile App

React Native (Expo dev-client) app with full feature parity with the web demo
(`index.html` / `index_en.html`): gesture trajectory reconstruction and
foot-mounted gait tracking, from either the phone's own IMU or the XIAO
nRF52840 Sense BLE foot pod.

## Features (mirrors the web app)

- **Two sensor sources**
  - Phone IMU via `expo-sensors` DeviceMotion (attitude + acceleration, prefers
    the platform's fused gravity-free acceleration when available).
  - XIAO BLE foot pod (`XIAO-Foot-IMU`): 50 Hz quaternion + accel + gyro
    packets. Requests MTU 64 on Android so the 32-byte packets are not truncated.
- **Gravity calibration** on the phone side (hold still 1.5 s / 2.8 s for BLE).
  No BLE command is sent — the XIAO firmware auto-calibrates its gyro bias
  whenever the pod is stationary (GATT writes drop the link on some hosts).
- **Gesture mode**: record → acausal batch reconstruction with rest→move→rest
  boundary constraints (smoothing window, de-drift toggle, closed-gesture
  toggle, rebuild button), replay animation, live attitude plate, 3D trajectory
  view with drag-to-rotate and XY/XZ/YZ projections.
- **Walk mode (PDR)**: per-stride ZUPT, ground path view, gait metrics grid
  (cadence, speed, stride time/length + CV, stance %, clearance, turning).
- **Export** JSON/CSV via the system share sheet; **upload** to the local
  HTTPS server (`https://<mac-ip>:8443/upload`) or the Cloudflare Worker.

## BLE contract

Firmware: `xiao_ble/firmware/xiao_nrf52840_sense.ino` (Bluefruit build — see
`xiao_ble/README.md`).

```text
service  12345678-1234-5678-1234-56789abcdef0
notify   12345678-1234-5678-1234-56789abcdef1   32-byte packet, 50 Hz
command  12345678-1234-5678-1234-56789abcdef2   CAL / RESET / REBOOT / BOOTLOADER (optional)
```

Packet bytes 24/25 carry the pod's auto-calibration state (calibrated /
calibrating), shown in the app as the "Pod cal" metric.

## Run

Uses `react-native-ble-plx` and `expo-sensors`, so it needs a native build /
Expo dev client — it will not work in plain Expo Go.

```bash
cd mobile
npm install
npm run ios      # or: npm run android
```

(iOS needs a signing team in Xcode the first time; Android needs the SDK.)

## First use

1. Flash the XIAO firmware (or just use the phone's own sensors).
2. Tap **① Phone sensors** or **② Connect XIAO**.
3. Hold the sensor still, tap **③ Calibrate**.
4. Gesture mode: Record → draw in the air → Stop → tweak reconstruction params.
   Walk mode: Start walking with the pod on a shoe.
5. Export or upload the result for analysis.

## Upload endpoints

- Local dev server: run `python3 serve_https.py` on the Mac, then use
  `https://<mac-lan-ip>:8443/upload` (self-signed cert: iOS ATS may require the
  Cloudflare Worker instead for uploads from the app).
- Cloudflare: deploy with `CLOUDFLARE_DEPLOY.md`, use
  `https://your-worker.workers.dev/upload`.
