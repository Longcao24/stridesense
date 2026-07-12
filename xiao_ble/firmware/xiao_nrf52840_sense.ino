// XIAO nRF52840 Sense (Plus) foot-pod firmware.
//
// Stack: Seeed non-mbed core (Seeeduino:nrf52) + Bluefruit (SoftDevice S140).
// The mbed core's ArduinoBLE/Cordio stack leaks per-connection subscription
// state (duplicated + truncated notifications after reconnects) and wedges the
// link when a central writes while notifications stream, so it is not used.
//
// IMU: onboard LSM6DS3TR-C at 0x6A on Wire1 via the Seeed LSM6DS3 library.
// Build with -DTARGET_SEEED_XIAO_NRF52840_SENSE_PLUS so the library picks
// Wire1 (see xiao_ble/README.md).

#include <Adafruit_TinyUSB.h> // required for USB CDC (Serial) on this core
#include <Wire.h>
#include <LSM6DS3.h> // Seeed Arduino LSM6DS3: onboard LSM6DS3TR-C on Wire1, handles IMU power pin
#include <bluefruit.h>

// A lightweight Madgwick AHRS implementation for 6-axis IMU.
class MadgwickAHRS {
public:
  float beta;
  float q0, q1, q2, q3;
  MadgwickAHRS(float betaDef = 0.041f) : beta(betaDef), q0(1), q1(0), q2(0), q3(0) {}
  void updateIMU(float gx, float gy, float gz, float ax, float ay, float az, float dt) {
    if (dt <= 0) return;
    float recipNorm;
    float s0, s1, s2, s3;
    float qDot1, qDot2, qDot3, qDot4;

    gx *= 0.017453292519943295f; // deg/s to rad/s
    gy *= 0.017453292519943295f;
    gz *= 0.017453292519943295f;

    qDot1 = 0.5f * (-q1 * gx - q2 * gy - q3 * gz);
    qDot2 = 0.5f * ( q0 * gx + q2 * gz - q3 * gy);
    qDot3 = 0.5f * ( q0 * gy - q1 * gz + q3 * gx);
    qDot4 = 0.5f * ( q0 * gz + q1 * gy - q2 * gx);

    recipNorm = invSqrt(ax * ax + ay * ay + az * az);
    if (recipNorm <= 0.0f) return;
    ax *= recipNorm;
    ay *= recipNorm;
    az *= recipNorm;

    float _2q0 = 2.0f * q0;
    float _2q1 = 2.0f * q1;
    float _2q2 = 2.0f * q2;
    float _2q3 = 2.0f * q3;
    float _4q0 = 4.0f * q0;
    float _4q1 = 4.0f * q1;
    float _4q2 = 4.0f * q2;
    float _8q1 = 8.0f * q1;
    float _8q2 = 8.0f * q2;
    float q0q0 = q0 * q0;
    float q1q1 = q1 * q1;
    float q2q2 = q2 * q2;
    float q3q3 = q3 * q3;

    float s0_temp = _4q0 * q2q2 + _2q2 * ax + _4q0 * q1q1 - _2q1 * ay;
    float s1_temp = _4q1 * q3q3 - _2q3 * ax + 4.0f * q0q0 * q1 - _2q0 * ay - _4q1 + _8q1 * q1q1 + _8q1 * q2q2 + _4q1 * az;
    float s2_temp = 4.0f * q0q0 * q2 + _2q0 * ax + _4q2 * q3q3 - _2q3 * ay - _4q2 + _8q2 * q1q1 + _8q2 * q2q2 + _4q2 * az;
    float s3_temp = 4.0f * q1q1 * q3 - _2q1 * ax + 4.0f * q2q2 * q3 - _2q2 * ay;

    recipNorm = invSqrt(s0_temp * s0_temp + s1_temp * s1_temp + s2_temp * s2_temp + s3_temp * s3_temp);
    if (recipNorm <= 0.0f) return;

    s0 = s0_temp * recipNorm;
    s1 = s1_temp * recipNorm;
    s2 = s2_temp * recipNorm;
    s3 = s3_temp * recipNorm;

    qDot1 -= beta * s0;
    qDot2 -= beta * s1;
    qDot3 -= beta * s2;
    qDot4 -= beta * s3;

    q0 += qDot1 * dt;
    q1 += qDot2 * dt;
    q2 += qDot3 * dt;
    q3 += qDot4 * dt;

    recipNorm = invSqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);
    q0 *= recipNorm;
    q1 *= recipNorm;
    q2 *= recipNorm;
    q3 *= recipNorm;
  }
private:
  static float invSqrt(float x) {
    return x > 0.0f ? 1.0f / sqrt(x) : 0.0f;
  }
};

LSM6DS3 imu(I2C_MODE, 0x6A);
MadgwickAHRS ahrs;

// 12345678-1234-5678-1234-56789abcdefX, little-endian byte order for the SoftDevice.
static const uint8_t SERVICE_UUID_LE[16]  = {0xF0,0xDE,0xBC,0x9A,0x78,0x56,0x34,0x12,0x78,0x56,0x34,0x12,0x78,0x56,0x34,0x12};
static const uint8_t IMU_CHAR_UUID_LE[16] = {0xF1,0xDE,0xBC,0x9A,0x78,0x56,0x34,0x12,0x78,0x56,0x34,0x12,0x78,0x56,0x34,0x12};
static const uint8_t CMD_CHAR_UUID_LE[16] = {0xF2,0xDE,0xBC,0x9A,0x78,0x56,0x34,0x12,0x78,0x56,0x34,0x12,0x78,0x56,0x34,0x12};

BLEService imuService(SERVICE_UUID_LE);
BLECharacteristic imuChar(IMU_CHAR_UUID_LE);
BLECharacteristic cmdChar(CMD_CHAR_UUID_LE);

uint32_t lastSampleMs = 0;
const uint32_t samplePeriodMs = 20;

volatile bool calibrating = false;
volatile bool calibrated = false;
uint16_t calibrationSamples = 0;
const uint16_t requiredCalibrationSamples = 120;
float gyroBiasX = 0.0f;
float gyroBiasY = 0.0f;
float gyroBiasZ = 0.0f;
float gyroBiasSumX = 0.0f;
float gyroBiasSumY = 0.0f;
float gyroBiasSumZ = 0.0f;

void startCalibration();
void onCommand(uint16_t conn_hdl, BLECharacteristic* chr, uint8_t* data, uint16_t len);
void onDisconnect(uint16_t conn_hdl, uint8_t reason);
void handleCommand();
void sampleAndNotify(uint32_t timestampMs, float dt, bool notify);

// Stationary detector state for auto-calibration.
float gMinX, gMinY, gMinZ, gMaxX, gMaxY, gMaxZ;
const float stillGyroSpreadDps = 4.0f;  // max-min per axis over the window
const float stillAccelTolMs2 = 0.6f;    // | |a| - g | tolerance

void startCalibration() {
  // Force a fresh auto-calibration window and re-seed the AHRS. Keep the old
  // gyro bias until the new window completes so orientation stays usable.
  calibrating = true;
  calibrated = false;
  calibrationSamples = 0;
  gyroBiasSumX = 0.0f;
  gyroBiasSumY = 0.0f;
  gyroBiasSumZ = 0.0f;
  ahrs.q0 = 1.0f;
  ahrs.q1 = 0.0f;
  ahrs.q2 = 0.0f;
  ahrs.q3 = 0.0f;
}

// The write callback runs on the SoftDevice/BLE task: it must not print,
// block, or do I2C work there, or the connection drops. It only records the
// command; loop() executes it.
volatile bool commandPending = false;
char pendingCommand[21];
volatile uint16_t lastDisconnectReason = 0xFFFF;
volatile uint8_t commandCount = 0;
uint8_t diagStage = 0;
__attribute__((section(".noinit"))) uint32_t bootCount; // survives MCU resets

void onCommand(uint16_t conn_hdl, BLECharacteristic* chr, uint8_t* data, uint16_t len) {
  (void)conn_hdl;
  (void)chr;
  uint16_t n = len > 20 ? 20 : len;
  memcpy(pendingCommand, data, n);
  pendingCommand[n] = '\0';
  commandPending = true;
  commandCount++;
}

void onDisconnect(uint16_t conn_hdl, uint8_t reason) {
  (void)conn_hdl;
  lastDisconnectReason = reason;
}

void handleCommand() {
  if (!commandPending) return;
  commandPending = false;
  const char* command = pendingCommand;

  if (!strcmp(command, "CAL") || !strcmp(command, "CALIBRATE")) {
    startCalibration();
  } else if (!strcmp(command, "RESET")) {
    calibrated = false;
    calibrating = false;
    gyroBiasX = gyroBiasY = gyroBiasZ = 0.0f;
    ahrs.q0 = 1.0f;
    ahrs.q1 = 0.0f;
    ahrs.q2 = 0.0f;
    ahrs.q3 = 0.0f;
  } else if (!strcmp(command, "REBOOT")) {
    // Remote escape hatch: a full MCU reset always recovers the BLE stack.
    NVIC_SystemReset();
  } else if (!strcmp(command, "BOOTLOADER")) {
    // Reboot into the UF2/DFU bootloader so firmware can be reflashed over
    // USB without pressing the physical reset button (DFU_MAGIC_UF2_RESET).
    NRF_POWER->GPREGRET = 0x57;
    NVIC_SystemReset();
  }
}

void setup() {
  bootCount++;
  Serial.begin(115200);
  // Red LED is reserved for the IMU-failure blink; keep it off otherwise.
  // Connection status uses Bluefruit's blue LED: blinking = advertising
  // (waiting for a connection), solid = connected.
  pinMode(LED_RED, OUTPUT);
  digitalWrite(LED_RED, HIGH); // active-low: HIGH = off

  imu.settings.accelRange = 4;        // g
  imu.settings.gyroRange = 2000;      // dps
  imu.settings.accelSampleRate = 104; // Hz
  imu.settings.gyroSampleRate = 104;  // Hz
  // Cold boot on battery: the IMU power rail needs longer to settle than a
  // warm USB boot, so retry init for up to ~5 s before declaring failure.
  int imuTries = 0;
  while (imu.begin() != 0) {
    if (++imuTries >= 25) {
      // IMU init failure: fast red blink forever. No Serial anywhere at
      // runtime: touching the TinyUSB CDC object while USB isn't fully
      // enumerated can hardfault the MCU into a reset loop.
      while (1) {
        digitalWrite(LED_RED, !digitalRead(LED_RED));
        delay(120);
      }
    }
    delay(200);
  }

  // Must precede begin(): raises ATT MTU to 247 and deepens the notify queue,
  // otherwise notifications truncate to 20 bytes and drop to ~16 Hz.
  Bluefruit.configPrphBandwidth(BANDWIDTH_MAX);
  Bluefruit.begin();
  // Drive the blue LED ourselves: Bluefruit's autoConnLed assumes active-high
  // LEDs and shows "solid on" as off on the XIAO (active-low).
  Bluefruit.autoConnLed(false);
  pinMode(LED_BLUE, OUTPUT);
  digitalWrite(LED_BLUE, HIGH); // off
  Bluefruit.setTxPower(4);
  // Per-foot identity: build with -DFOOT_NAME='"XIAO-Foot-L"' (or -R) so the
  // app can tell the two pods apart. Default keeps the single-pod name.
#ifndef FOOT_NAME
#define FOOT_NAME "XIAO-Foot-IMU"
#endif
  Bluefruit.setName(FOOT_NAME);
  Bluefruit.Periph.setDisconnectCallback(onDisconnect);

  imuService.begin();

  imuChar.setProperties(CHR_PROPS_READ | CHR_PROPS_NOTIFY);
  imuChar.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  imuChar.setFixedLen(32);
  imuChar.begin();

  cmdChar.setProperties(CHR_PROPS_WRITE | CHR_PROPS_WRITE_WO_RESP);
  cmdChar.setPermission(SECMODE_NO_ACCESS, SECMODE_OPEN);
  cmdChar.setMaxLen(20);
  // useAdaCallback=false: run directly on the BLE task. The callback only
  // records the command, and this sidesteps the Ada callback deferral queue.
  cmdChar.setWriteCallback(onCommand, false);
  cmdChar.begin();

  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addService(imuService);
  Bluefruit.ScanResponse.addName();
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(32, 244); // fast, then slower (0.625 ms units)
  Bluefruit.Advertising.setFastTimeout(30);
  Bluefruit.Advertising.start(0); // advertise forever
}

void loop() {
  handleCommand();

  // Blue LED (active-low): blink while waiting for a connection, solid on
  // while a central is connected.
  static uint32_t lastLedMs = 0;
  if (Bluefruit.connected()) {
    digitalWrite(LED_BLUE, LOW);
  } else if (millis() - lastLedMs >= 500) {
    lastLedMs = millis();
    digitalWrite(LED_BLUE, !digitalRead(LED_BLUE));
  }

  uint32_t now = millis();
  if (now - lastSampleMs >= samplePeriodMs) {
    uint32_t elapsed = now - lastSampleMs;
    float dt = (lastSampleMs && elapsed < 200) ? elapsed / 1000.0f : samplePeriodMs / 1000.0f;
    lastSampleMs = now;
    // Keep sampling (AHRS + calibration progress) even with no subscriber,
    // but only push notifications when a central is connected.
    sampleAndNotify(now, dt, Bluefruit.connected());
  }
  delay(1); // yield to the SoftDevice/FreeRTOS scheduler
}

void sampleAndNotify(uint32_t timestampMs, float dt, bool notify) {
  // Seeed LSM6DS3 returns accel in g and gyro in dps; packet carries m/s2 and dps.
  float ax = imu.readFloatAccelX() * 9.80665f;
  float ay = imu.readFloatAccelY() * 9.80665f;
  float az = imu.readFloatAccelZ() * 9.80665f;
  float gxRaw = imu.readFloatGyroX();
  float gyRaw = imu.readFloatGyroY();
  float gzRaw = imu.readFloatGyroZ();

  // Stationary auto-calibration: no BLE command needed (host->device GATT
  // writes are unreliable on some hosts). Collect a window of samples; if the
  // device stayed still for the whole window (low gyro spread, |accel| near
  // 1 g), take the window mean as the gyro bias. Re-runs whenever the pod is
  // still again, so the bias tracks drift. The CAL command just forces a
  // fresh window.
  // Stationary auto-calibration, deliberately inline: an earlier revision had
  // this in a helper function and the first call into it hardfaulted the MCU
  // into a reset loop (bisected live over BLE; inline stages were fine).
  {
    float aMag = sqrtf(ax * ax + ay * ay + az * az);
    bool accelStill = fabsf(aMag - 9.80665f) < stillAccelTolMs2;

    if (calibrationSamples == 0) {
      gMinX = gMaxX = gxRaw;
      gMinY = gMaxY = gyRaw;
      gMinZ = gMaxZ = gzRaw;
    } else {
      gMinX = min(gMinX, gxRaw); gMaxX = max(gMaxX, gxRaw);
      gMinY = min(gMinY, gyRaw); gMaxY = max(gMaxY, gyRaw);
      gMinZ = min(gMinZ, gzRaw); gMaxZ = max(gMaxZ, gzRaw);
    }

    bool gyroStill = (gMaxX - gMinX) < stillGyroSpreadDps &&
                     (gMaxY - gMinY) < stillGyroSpreadDps &&
                     (gMaxZ - gMinZ) < stillGyroSpreadDps;

    if (!accelStill || !gyroStill) {
      calibrationSamples = 0;
      gyroBiasSumX = gyroBiasSumY = gyroBiasSumZ = 0.0f;
      calibrating = false;
    } else {
      calibrating = !calibrated;
      gyroBiasSumX += gxRaw;
      gyroBiasSumY += gyRaw;
      gyroBiasSumZ += gzRaw;
      calibrationSamples++;

      if (calibrationSamples >= requiredCalibrationSamples) {
        // Multiply by the constant reciprocal instead of dividing: samples is
        // always exactly requiredCalibrationSamples here, and this keeps the
        // hot path free of VDIV (crash bisection pointed at the completion
        // block; division and the function call were the untested suspects).
        const float invN = 1.0f / (float)requiredCalibrationSamples;
        gyroBiasX = gyroBiasSumX * invN;
        gyroBiasY = gyroBiasSumY * invN;
        gyroBiasZ = gyroBiasSumZ * invN;
        calibrating = false;
        calibrated = true;
        calibrationSamples = 0;
        gyroBiasSumX = gyroBiasSumY = gyroBiasSumZ = 0.0f;
      }
    }
  }

  float gx = gxRaw - gyroBiasX;
  float gy = gyRaw - gyroBiasY;
  float gz = gzRaw - gyroBiasZ;

  ahrs.updateIMU(gx, gy, gz, ax, ay, az, dt);

  int16_t ax_i = constrain((int32_t)round(ax * 1000.0f), -32767, 32767);
  int16_t ay_i = constrain((int32_t)round(ay * 1000.0f), -32767, 32767);
  int16_t az_i = constrain((int32_t)round(az * 1000.0f), -32767, 32767);
  int16_t gx_i = constrain((int32_t)round(gx * 100.0f), -32767, 32767);
  int16_t gy_i = constrain((int32_t)round(gy * 100.0f), -32767, 32767);
  int16_t gz_i = constrain((int32_t)round(gz * 100.0f), -32767, 32767);
  int16_t q0_i = constrain((int32_t)round(ahrs.q0 * 16384.0f), -32767, 32767);
  int16_t q1_i = constrain((int32_t)round(ahrs.q1 * 16384.0f), -32767, 32767);
  int16_t q2_i = constrain((int32_t)round(ahrs.q2 * 16384.0f), -32767, 32767);
  int16_t q3_i = constrain((int32_t)round(ahrs.q3 * 16384.0f), -32767, 32767);

  uint8_t packet[32];
  packet[0] = (timestampMs >> 0) & 0xFF;
  packet[1] = (timestampMs >> 8) & 0xFF;
  packet[2] = (timestampMs >> 16) & 0xFF;
  packet[3] = (timestampMs >> 24) & 0xFF;
  memcpy(packet + 4, &ax_i, 2);
  memcpy(packet + 6, &ay_i, 2);
  memcpy(packet + 8, &az_i, 2);
  memcpy(packet + 10, &gx_i, 2);
  memcpy(packet + 12, &gy_i, 2);
  memcpy(packet + 14, &gz_i, 2);
  memcpy(packet + 16, &q0_i, 2);
  memcpy(packet + 18, &q1_i, 2);
  memcpy(packet + 20, &q2_i, 2);
  memcpy(packet + 22, &q3_i, 2);
  packet[24] = calibrated ? 1 : 0;
  packet[25] = calibrating ? 1 : 0;
  packet[26] = calibrationSamples & 0xFF;
  packet[27] = (calibrationSamples >> 8) & 0xFF;
  packet[28] = requiredCalibrationSamples & 0xFF;
  packet[29] = (requiredCalibrationSamples >> 8) & 0xFF;
  // Diagnostics (receivers ignore these bytes): active bisection stage and a
  // reset-surviving boot counter to detect crash-reset loops.
  packet[30] = diagStage;
  packet[31] = (uint8_t)bootCount;

  if (notify) {
    imuChar.notify(packet, sizeof(packet)); // no-op if the central hasn't subscribed
  }
}
