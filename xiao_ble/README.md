# XIAO nRF52840 Sense Shoe Pod Prototype

This folder contains a reference firmware and Web Bluetooth receiver for a shoe-mounted XIAO nRF52840 Sense IMU pod.

## What is included

- `firmware/xiao_nrf52840_sense.ino`
  - Arduino sketch for the XIAO nRF52840 Sense.
  - Reads onboard accelerometer + gyroscope.
  - Runs Madgwick IMU sensor fusion to estimate orientation.
  - Streams timestamped sensor packets over BLE notifications.

- `receiver.html`
  - A Web Bluetooth page to connect to the XIAO pod.
  - Receives IMU packets, displays live values, and exports JSON / CSV.

## How to use

1. Install the required Arduino board support and library:
   - Board package: **`Seeeduino:nrf52`** (non-mbed core; Bluefruit/SoftDevice is bundled).
     Do NOT use the `Seeeduino:mbed` core + ArduinoBLE: its Cordio BLE stack leaks
     per-connection subscription state (duplicated/truncated notifications after
     reconnects) and wedges when a central writes during notification streaming.
   - `Seeed Arduino LSM6DS3` (the onboard IMU is an LSM6DS3TR-C on `Wire1`, not an LSM6DSOX)
   - Board index URL: `https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json`

2. Flash `firmware/xiao_nrf52840_sense.ino` to the XIAO with arduino-cli:
   ```bash
   # Sketch must live in a folder named after the .ino for arduino-cli.
   # The core's post-build tooling needs a `python` on PATH (alias python3).
   mkdir -p /tmp/xiao_nrf52840_sense && cp firmware/xiao_nrf52840_sense.ino /tmp/xiao_nrf52840_sense/
   arduino-cli compile -b Seeeduino:nrf52:xiaonRF52840SensePlus \
     --build-property "compiler.cpp.extra_flags=-DTARGET_SEEED_XIAO_NRF52840_SENSE_PLUS" \
     /tmp/xiao_nrf52840_sense
   arduino-cli upload -b Seeeduino:nrf52:xiaonRF52840SensePlus -p /dev/cu.usbmodemXXXX /tmp/xiao_nrf52840_sense
   ```
   The extra define is required on the Sense **Plus**: the LSM6DS3 library only
   remaps its bus to `Wire1` when `TARGET_SEEED_XIAO_NRF52840_SENSE_PLUS` is
   defined, and neither Seeed core defines it — without it the library talks to
   the wrong I2C bus and IMU init fails. On the non-Plus Sense use board
   `Seeeduino:nrf52:xiaonRF52840Sense` (the define is also accepted there).
   If no serial port shows up, double-tap the reset button to enter the UF2
   bootloader and flash against the port that appears.

   Firmware hard-won rules (violating either hardfaults the MCU into a
   crash-reset loop where BLE advertising still works but nothing else does):
   - Never touch `Serial` (TinyUSB CDC) at runtime — boot-time only, ideally never.
   - Keep the auto-calibration logic inline in `sampleAndNotify` (see the
     comment in the sketch; a helper-function version faulted at the call).

3. Start the project HTTPS server from the repo root:
   ```bash
   cd /Users/longcao/phone-motion-tracker
   python3 serve_https.py
   ```

4. Open the receiver page on a compatible browser:
   - `https://localhost:8443/xiao_ble/receiver.html`
   - Web Bluetooth works best in Chrome/Edge on desktop or Android Chrome.

5. Tap **Connect**, then select the device named `XIAO-Foot-IMU`.

6. After connection, data will stream live. Use **Download CSV** or **Download JSON** to save recordings.

## Notes

- The packets include:
  - `timestamp_ms`
  - `ax, ay, az` in m/s²
  - `gx, gy, gz` in deg/s
  - `qw, qx, qy, qz` quaternion raw orientation
  - firmware calibration flags in bytes 24-29

- **Calibration is automatic**: the firmware continuously detects when the pod
  is stationary (~2.4 s of low gyro spread with |accel| ≈ 1 g) and re-estimates
  the gyro bias. No BLE command is needed — important because on some hosts
  (macOS in particular) any GATT write to the pod drops the BLE link (the
  firmware survives; the client just reconnects).

- The main web app and the React Native mobile app both consume these BLE packets. The command characteristic accepts (optional; see the macOS caveat above):
  - `CAL` to force a fresh calibration window and re-seed the AHRS
  - `RESET` to clear firmware calibration state
  - `REBOOT` to reset the MCU remotely
  - `BOOTLOADER` to reboot into the UF2/DFU bootloader for reflashing without
    pressing the physical reset button

- The onboard IMU I2C address is 0x6A. If IMU init fails, check that the
  `TARGET_SEEED_XIAO_NRF52840_SENSE_PLUS` build flag is set (see step 2).
