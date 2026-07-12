import { BleError, BleManager, Characteristic, Device, Subscription } from "react-native-ble-plx";

export const XIAO_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0";
export const XIAO_NOTIFY_UUID = "12345678-1234-5678-1234-56789abcdef1";
export const XIAO_COMMAND_UUID = "12345678-1234-5678-1234-56789abcdef2";

export type FootSide = "L" | "R";

// The legacy single-pod firmware name maps to L so one-pod setups keep working.
const NAME_TO_SIDE: Record<string, FootSide> = {
  "XIAO-Foot-L": "L",
  "XIAO-Foot-R": "R",
  "XIAO-Foot-IMU": "L",
};

export type PodInfo = { id: string; name: string; side: FootSide };

export type XiaoSample = {
  timestampMs: number;
  ax: number;
  ay: number;
  az: number;
  gx: number;
  gy: number;
  gz: number;
  qw: number;
  qx: number;
  qy: number;
  qz: number;
  calibrated: boolean;
  calibrating: boolean;
  calibrationSamples: number;
  calibrationTarget: number;
};

const BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

function decodeBase64(value: string): Uint8Array {
  const clean = value.replace(/=+$/, "");
  const out: number[] = [];
  let buffer = 0;
  let bits = 0;

  for (const char of clean) {
    const idx = BASE64_ALPHABET.indexOf(char);
    if (idx < 0) continue;
    buffer = (buffer << 6) | idx;
    bits += 6;
    if (bits >= 8) {
      bits -= 8;
      out.push((buffer >> bits) & 0xff);
    }
  }

  return new Uint8Array(out);
}

function encodeBase64(bytes: Uint8Array): string {
  let out = "";
  for (let i = 0; i < bytes.length; i += 3) {
    const a = bytes[i];
    const b = bytes[i + 1] ?? 0;
    const c = bytes[i + 2] ?? 0;
    const triple = (a << 16) | (b << 8) | c;
    out += BASE64_ALPHABET[(triple >> 18) & 63];
    out += BASE64_ALPHABET[(triple >> 12) & 63];
    out += i + 1 < bytes.length ? BASE64_ALPHABET[(triple >> 6) & 63] : "=";
    out += i + 2 < bytes.length ? BASE64_ALPHABET[triple & 63] : "=";
  }
  return out;
}

function encodeAscii(value: string): Uint8Array {
  const bytes = new Uint8Array(value.length);
  for (let i = 0; i < value.length; i++) bytes[i] = value.charCodeAt(i) & 0xff;
  return bytes;
}

function readInt16LE(bytes: Uint8Array, offset: number): number {
  const value = bytes[offset] | (bytes[offset + 1] << 8);
  return value & 0x8000 ? value - 0x10000 : value;
}

function readUint16LE(bytes: Uint8Array, offset: number): number {
  return bytes[offset] | (bytes[offset + 1] << 8);
}

function readUint32LE(bytes: Uint8Array, offset: number): number {
  return (
    bytes[offset] |
    (bytes[offset + 1] << 8) |
    (bytes[offset + 2] << 16) |
    (bytes[offset + 3] << 24)
  ) >>> 0;
}

export function parseXiaoPacket(base64Value: string): XiaoSample {
  const bytes = decodeBase64(base64Value);
  if (bytes.length < 24) {
    throw new Error(`XIAO packet too short: ${bytes.length} bytes`);
  }

  return {
    timestampMs: readUint32LE(bytes, 0),
    ax: readInt16LE(bytes, 4) / 1000,
    ay: readInt16LE(bytes, 6) / 1000,
    az: readInt16LE(bytes, 8) / 1000,
    gx: readInt16LE(bytes, 10) / 100,
    gy: readInt16LE(bytes, 12) / 100,
    gz: readInt16LE(bytes, 14) / 100,
    qw: readInt16LE(bytes, 16) / 16384,
    qx: readInt16LE(bytes, 18) / 16384,
    qy: readInt16LE(bytes, 20) / 16384,
    qz: readInt16LE(bytes, 22) / 16384,
    calibrated: bytes.length >= 25 ? bytes[24] === 1 : false,
    calibrating: bytes.length >= 26 ? bytes[25] === 1 : false,
    calibrationSamples: bytes.length >= 28 ? readUint16LE(bytes, 26) : 0,
    calibrationTarget: bytes.length >= 30 ? readUint16LE(bytes, 28) : 0,
  };
}

export type PodCallbacks = {
  onSample: (side: FootSide, sample: XiaoSample) => void;
  onError: (side: FootSide, message: string) => void;
  onDisconnected: (side: FootSide) => void;
};

// Multi-pod BLE manager: one BleManager instance for the whole app (ble-plx
// requirement), scanning once for every foot pod and holding a connection per
// side. A single L pod behaves exactly like the old single-pod client.
export class XiaoPodManager {
  private manager = new BleManager();
  private devices = new Map<FootSide, Device>();
  private subs = new Map<FootSide, Subscription>();

  get connectedSides(): FootSide[] {
    return [...this.devices.keys()].sort();
  }

  async destroy(): Promise<void> {
    await this.disconnectAll();
    this.manager.destroy();
  }

  async disconnectAll(): Promise<void> {
    for (const sub of this.subs.values()) sub.remove();
    this.subs.clear();
    for (const device of this.devices.values()) {
      try {
        await this.manager.cancelDeviceConnection(device.id);
      } catch {
        // Already disconnected.
      }
    }
    this.devices.clear();
  }

  // Scan until both sides are found or the timeout elapses; resolves with
  // whatever pods showed up (possibly just one).
  scanPods(timeoutMs = 10000): Promise<PodInfo[]> {
    return new Promise((resolve, reject) => {
      const found = new Map<FootSide, PodInfo>();
      let done = false;
      const finish = (error?: BleError) => {
        if (done) return;
        done = true;
        clearTimeout(timer);
        this.manager.stopDeviceScan();
        if (error && found.size === 0) reject(error);
        else resolve([...found.values()].sort((a, b) => a.side.localeCompare(b.side)));
      };
      const timer = setTimeout(() => finish(), timeoutMs);

      this.manager.startDeviceScan([XIAO_SERVICE_UUID], null, (error, device) => {
        if (error) {
          finish(error);
          return;
        }
        if (!device?.name) return;
        const side = NAME_TO_SIDE[device.name];
        if (!side || found.has(side)) return;
        found.set(side, { id: device.id, name: device.name, side });
        if (found.size >= 2) finish();
      });
    });
  }

  async connectPod(pod: PodInfo, callbacks: PodCallbacks): Promise<void> {
    const device = await this.manager.connectToDevice(pod.id, {
      timeout: 15000,
      // Android does not negotiate MTU automatically; without ~64 the 32-byte
      // packets get truncated to 20 and parsing fails.
      requestMTU: 64,
    });
    this.manager.onDeviceDisconnected(device.id, () => {
      this.subs.get(pod.side)?.remove();
      this.subs.delete(pod.side);
      this.devices.delete(pod.side);
      callbacks.onDisconnected(pod.side);
    });
    const discovered = await device.discoverAllServicesAndCharacteristics();
    this.devices.set(pod.side, discovered);
    const sub = discovered.monitorCharacteristicForService(
      XIAO_SERVICE_UUID,
      XIAO_NOTIFY_UUID,
      (error: BleError | null, characteristic: Characteristic | null) => {
        if (error) {
          callbacks.onError(pod.side, error.message);
          return;
        }
        if (!characteristic?.value) return;
        try {
          callbacks.onSample(pod.side, parseXiaoPacket(characteristic.value));
        } catch (parseError) {
          callbacks.onError(pod.side, parseError instanceof Error ? parseError.message : String(parseError));
        }
      },
    );
    this.subs.set(pod.side, sub);
  }

  async writeCommand(side: FootSide, command: string): Promise<void> {
    const device = this.devices.get(side);
    if (!device) throw new Error(`Pod ${side} is not connected`);
    await device.writeCharacteristicWithResponseForService(
      XIAO_SERVICE_UUID,
      XIAO_COMMAND_UUID,
      encodeBase64(encodeAscii(command)),
    );
  }
}
