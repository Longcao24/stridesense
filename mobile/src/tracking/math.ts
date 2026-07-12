export type Vec3 = [number, number, number];
export type Mat3 = [number, number, number, number, number, number, number, number, number];

export const DEG = Math.PI / 180;

export function mag3(v: Vec3): number {
  return Math.hypot(v[0], v[1], v[2]);
}

export function matVec(r: Mat3, v: Vec3): Vec3 {
  return [
    r[0] * v[0] + r[1] * v[1] + r[2] * v[2],
    r[3] * v[0] + r[4] * v[1] + r[5] * v[2],
    r[6] * v[0] + r[7] * v[1] + r[8] * v[2],
  ];
}

export function quatToMatrix(qw: number, qx: number, qy: number, qz: number): Mat3 {
  const xx = qx * qx;
  const yy = qy * qy;
  const zz = qz * qz;
  const xy = qx * qy;
  const xz = qx * qz;
  const yz = qy * qz;
  const wx = qw * qx;
  const wy = qw * qy;
  const wz = qw * qz;
  return [
    1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy),
    2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx),
    2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy),
  ];
}

// W3C deviceorientation ZXY intrinsic (alpha=Z, beta=X', gamma=Y'') -> device->world
// rotation matrix; same formula as the web app / full-tilt.js.
export function eulerToMatrix(alphaDeg: number, betaDeg: number, gammaDeg: number): Mat3 {
  const a = alphaDeg * DEG;
  const b = betaDeg * DEG;
  const g = gammaDeg * DEG;
  const cA = Math.cos(a), sA = Math.sin(a);
  const cB = Math.cos(b), sB = Math.sin(b);
  const cG = Math.cos(g), sG = Math.sin(g);
  return [
    cA * cG - sA * sB * sG, -sA * cB, cA * sG + sA * sB * cG,
    sA * cG + cA * sB * sG, cA * cB, sA * sG - cA * sB * cG,
    -cB * sG, sB, cB * cG,
  ];
}

export function matrixToEulerZXY(r: Mat3): { alpha: number; beta: number; gamma: number } {
  const radToDeg = 180 / Math.PI;
  const beta = Math.asin(Math.max(-1, Math.min(1, r[7])));
  const cB = Math.cos(beta);
  let alpha = 0;
  let gamma = 0;
  if (Math.abs(cB) > 1e-6) {
    alpha = Math.atan2(-r[1], r[4]);
    gamma = Math.atan2(-r[6], r[8]);
  } else {
    alpha = Math.atan2(r[2], r[0]);
  }
  return { alpha: alpha * radToDeg, beta: beta * radToDeg, gamma: gamma * radToDeg };
}

export function wrap180(deg: number): number {
  return ((deg + 540) % 360) - 180;
}

export function mean(values: number[]): number {
  return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : Number.NaN;
}

export function median(values: number[]): number {
  if (!values.length) return Number.NaN;
  const sorted = values.slice().sort((a, b) => a - b);
  const mid = sorted.length >> 1;
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

export function stat(values: number[]): { n: number; mean: number; cv: number } {
  if (values.length < 2) return { n: values.length, mean: Number.NaN, cv: Number.NaN };
  const m = mean(values);
  const sd = Math.sqrt(values.reduce((sum, value) => sum + (value - m) ** 2, 0) / (values.length - 1));
  return { n: values.length, mean: m, cv: m ? (sd / m) * 100 : Number.NaN };
}
