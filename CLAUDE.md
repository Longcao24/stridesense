# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A gait/motion tracking system with four coupled components:

- **Web app** — `index.html` (Chinese) / `index_en.html` (English): single-file, zero-dependency. Tracks from phone sensors (devicemotion) or a XIAO BLE pod via Web Bluetooth. `index_en.html` is largely generated from `index.html` via `make_index_en.py` — when editing shared logic, edit both (or update the generator).
- **Firmware** — `xiao_ble/firmware/xiao_nrf52840_sense.ino`: Seeed XIAO nRF52840 **Sense Plus** foot pod. Streams 32-byte IMU packets (Madgwick quaternion + accel + gyro) at 50 Hz over BLE.
- **Mobile app** — `mobile/`: Expo React Native (dev-client; not Expo Go). Connects to **two pods simultaneously** (`XIAO-Foot-L`/`XIAO-Foot-R`), walk (PDR) + gesture modes, left/right gait comparison, step-replay simulation, share links.
- **Cloudflare worker** — `cloudflare/worker.js`: upload store (KV) + public share viewer at `/view/<name>`. Deployed at `https://phone-motion-tracker-upload.longcao.workers.dev`.

The `make_*.py` scripts generate the pitch/tech PPTX decks and figures; they are independent of the apps.

## Commands

### Firmware (build + flash)

```bash
# One-time: python shim for the core's tooling, sketch dir named after the .ino
ln -sf "$(which python3)" <scratch>/bin/python && export PATH=<scratch>/bin:$PATH
mkdir -p /tmp/xiao_nrf52840_sense && cp xiao_ble/firmware/xiao_nrf52840_sense.ino /tmp/xiao_nrf52840_sense/

arduino-cli compile -b Seeeduino:nrf52:xiaonRF52840SensePlus \
  --build-property "compiler.cpp.extra_flags=-DTARGET_SEEED_XIAO_NRF52840_SENSE_PLUS" \
  /tmp/xiao_nrf52840_sense
arduino-cli upload -b Seeeduino:nrf52:xiaonRF52840SensePlus -p /dev/cu.usbmodemXXXX /tmp/xiao_nrf52840_sense
```

- **Core**: `Seeeduino:nrf52` (Bluefruit/SoftDevice). Never the `Seeeduino:mbed` core + ArduinoBLE — its Cordio stack leaks subscription state across reconnects and wedges on central writes.
- The `TARGET_SEEED_XIAO_NRF52840_SENSE_PLUS` define is mandatory: without it the Seeed LSM6DS3 library talks to the wrong I2C bus and IMU init fails.
- **L/R variants**: sed the `#define FOOT_NAME "XIAO-Foot-IMU"` line to `XIAO-Foot-L` / `XIAO-Foot-R` in the sketch copy before compiling (passing quoted strings through `--build-property` mangles the quotes into the name).
- If no serial port appears, double-tap the pod's reset button → UF2 bootloader (port + `XIAO-SENSE` volume), then upload against that port. A running healthy app accepts a 1200-baud DTR touch instead. Watch for OpenMV IDE / ArduinoCloudAgent grabbing serial ports.
- See `xiao_ble/README.md` for the full recipe and the packet format.

### Mobile app

```bash
cd mobile
npx tsc --noEmit                 # typecheck (the only fast check; there are no tests)
npm run android                  # dev build + Metro (needs JAVA_HOME=/opt/homebrew/opt/openjdk@17,
                                 #   ANDROID_HOME=/opt/homebrew/share/android-commandlinetools)
cd android && ./gradlew assembleRelease   # standalone APK -> android/app/build/outputs/apk/release/
adb install -r <apk> && adb shell am force-stop com.stridesense.xiao   # install -r does NOT restart the app
```

Dependency versions must match the Expo SDK exactly (`npx expo install --check` / `--fix`); a drifted `react` or `react-native-svg` causes renderer crashes ("Cannot read property 'default'", "Unsupported top level event") that require a **native rebuild**, not just a Metro reload.

### Web app + local upload server

```bash
python3 serve_https.py    # HTTPS on :8443 (self-signed), serves the repo + POST /upload -> uploads/
```

### Cloudflare worker

```bash
npx wrangler deploy       # from repo root; config in wrangler.toml, KV binding MOTION_UPLOADS
```

## Architecture

### The BLE packet contract (change all consumers together)

The 32-byte notification packet defined in the firmware is parsed independently in **four** places: `mobile/src/ble/xiao.ts`, `index.html`, `index_en.html`, `xiao_ble/receiver.html`, plus the share viewer reads derived JSON. Layout: `u32 timestampMs | i16 ax,ay,az (m/s²×1000) | i16 gx,gy,gz (dps×100) | i16 qw,qx,qy,qz (×16384) | u8 calibrated | u8 calibrating | u16 calSamples | u16 calTarget | 2 diag bytes`. Known limitation: gyro clips at ±327.67 dps and accel at ±32.77 m/s² — changing the scale requires updating every parser in the same commit.

Service `12345678-...-def0`, notify `...def1`, command `...def2` (`CAL`/`RESET`/`REBOOT`/`BOOTLOADER`, where `BOOTLOADER` reboots into UF2 DFU for button-free reflash).

### No-GATT-write design

On some hosts (macOS specifically) **any GATT write to the pod drops the BLE link** (the firmware survives and processes the command first; the client must reconnect). Therefore the firmware **auto-calibrates its gyro bias whenever the pod is stationary** (~2.4 s of low gyro spread with |accel| ≈ 1 g) and the apps send no writes during normal operation. The command characteristic is optional/maintenance-only. Don't reintroduce a required write into the connect/calibrate flow.

### Firmware hard rules (violations crash-loop the MCU)

Symptom of a crash-loop: BLE advertising still works (SoftDevice is autonomous) but connect/notify/USB are dead — very misleading.

1. Never touch `Serial` (TinyUSB CDC) at runtime; boot-time only.
2. Keep the auto-calibration logic **inline** in `sampleAndNotify` (a helper-function version hardfaulted at the call; see comment in the sketch).
3. `Bluefruit.configPrphBandwidth(BANDWIDTH_MAX)` before `begin()` (else MTU 23 → truncated packets).
4. LEDs are active-low and Bluefruit's `autoConnLed` assumes active-high — the sketch drives the blue LED manually (blink = advertising, solid = connected; red fast-blink = IMU init failure).

### Tracker algorithm (mirrored web ↔ mobile)

`mobile/src/tracking/tracker.ts` is a TypeScript port of the algorithm inside `index.html` — keep them in sync when tuning:

- **Input**: source-agnostic `ImuFrame` (quaternion from pods, W3C euler from phone sensors), rotated to world frame; fused `userAccel` preferred over manual gravity subtraction when present.
- **Gravity calibration** is app-side (average world-frame accel while still; `unitScale` guesses g-units vs m/s²).
- **Gesture**: live causal integration (high-pass + ZUPT + leak) for preview; on stop, acausal batch reconstruction with rest→move→rest boundary constraints (smooth → zero-mean accel → integrate → linear-detrend velocity → integrate → optional closed-loop) — params `smooth/detrend/closed` re-runnable via `rebuild()`.
- **Walk (PDR)**: stance/swing detection (`|a|-g` and gyro thresholds), per-stride ZUPT with linear velocity detrend, stride gated to 0.1–2 m; per-stride gait features feed `gaitSummary()` (the 11-row clinical table incl. landing position from heel-strike pitch).
- **Dual-pod**: one `MotionTracker` per side; each pod's 6-axis AHRS has arbitrary yaw, so paths are rotated by `alignHeading()` (first displacement → +Y) before display — in the app and in the worker's viewer.
- **Trap**: `MotionTracker.mode` must match the app's initial mode state — a mismatch silently routes samples to the wrong pipeline (this bug shipped once: UI said walk, trackers ran gesture, ground path stayed empty).

### Share flow

Mobile upload → worker stores JSON in KV → app builds `<base>/view/<name>` link. The viewer (`viewerHtml()` in `worker.js`, self-contained HTML string) renders `walk_dual` / `walk` / `gesture_dual` / gesture payloads with step playback and the L/R gait table. Payload shape changes must update `normalizeFeet()`/`table()` there.

### Hardware notes

- Boards: two XIAO nRF52840 **Sense Plus** (IMU = LSM6DS3TR-C at 0x6A on `Wire1`, powered via P1.08).
- macOS caches BLE device names — verify a renamed pod via `advertisement.local_name` (fresh from air), not `device.name`.
- bleak/CoreBluetooth on the dev Mac is flaky (connects time out spuriously); the reliable E2E harness is Chrome + puppeteer-core with `page.waitForDevicePrompt()` for the web app, and `adb` + `uiautomator dump` UI driving for the mobile app.
