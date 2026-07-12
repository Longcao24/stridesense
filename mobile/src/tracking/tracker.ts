import { eulerToMatrix, mag3, Mat3, matVec, matrixToEulerZXY, mean, median, quatToMatrix, stat, Vec3, wrap180 } from "./math";

// One IMU frame, source-agnostic: the XIAO BLE pod supplies a quaternion, the
// phone's own sensors supply W3C-style euler angles + optional fused
// gravity-free acceleration (preferred when present, like the web app).
export type ImuFrame = {
  tMs: number;
  aDev: Vec3; // acceleration including gravity, device frame
  quat?: { w: number; x: number; y: number; z: number };
  euler?: { alpha: number; beta: number; gamma: number };
  userAccel?: Vec3 | null; // gravity-free acceleration, device frame
  rotRateMag: number; // deg/s
};

type RawSample = { t: number; dt: number; aw: Vec3; alpha: number; beta: number; gamma: number };
export type PathPoint = { x: number; y: number; z: number };
export type Mode = "gesture" | "walk";

export type TrackerParams = {
  gain: number;
  leak: number;
  zupt: number;
  hp: number;
  smooth: number;
  detrend: boolean;
  closed: boolean;
  walkAccTh: number;
  walkGyroTh: number;
  walkN: number;
};

export type GaitStride = {
  t: number;
  swingT: number;
  stanceT: number;
  len: number;
  peakV: number;
  peakGyro: number;
  peakAcc: number;
  clearance: number;
  heading: number;
  pitchHS: number;
  pitchTO: number;
};

export type GaitSummary = {
  strides: number;
  steps: number;
  distanceM: number;
  cadence: number;
  speed: number;
  strideTimeMean: number;
  strideTimeCv: number;
  strideLengthMean: number;
  strideLengthCv: number;
  stancePct: number;
  clearance: number;
  turnSteps: number;
  totalTurn: number;
  // Clinical hallway-walking table (per foot):
  stepCount: number; // strides committed by this foot
  stepPace: number; // steps/min derived from the gait cycle
  swingTimeMean: number; // s
  stanceTimeMean: number; // s
  gaitCycleMean: number; // s (swing + stance)
  maxFootVelocity: number; // mm/s, max over strides (IMU analog of max COP velocity)
  avgFootVelocity: number; // mm/s, stride length / gait cycle (analog of avg COP velocity)
  pitchHSMean: number; // deg, foot pitch at heel strike (relative to flat)
  pitchTOMean: number; // deg, foot pitch at toe off (relative to flat)
  landingPosition: string; // heel-first / flat / toe-first, from pitch at landing
};

type WalkState = {
  active: boolean;
  v: Vec3;
  p: Vec3;
  pLive: Vec3;
  path: Vec3[];
  pathT: number[]; // seconds since walk start, parallel to path (for replay)
  startT: number;
  swing: { aw: Vec3; dt: number; t: number }[];
  inStance: boolean;
  stanceCount: number;
  moveCount: number;
  steps: number;
  dist: number;
  strides: GaitStride[];
  stanceStartT: number;
  pendingStanceT: number;
  peakGyro: number;
  peakAcc: number;
  pitchTO: number;
  pitchHS: number;
  alphaTO: number;
  headingChange: number;
  flatPitch: number | null;
};

function freshWalk(active: boolean): WalkState {
  return {
    active,
    v: [0, 0, 0],
    p: [0, 0, 0],
    pLive: [0, 0, 0],
    path: [[0, 0, 0]],
    pathT: [0],
    startT: 0,
    swing: [],
    inStance: true,
    stanceCount: 0,
    moveCount: 0,
    steps: 0,
    dist: 0,
    strides: [],
    stanceStartT: 0,
    pendingStanceT: 0,
    peakGyro: 0,
    peakAcc: 0,
    pitchTO: 0,
    pitchHS: 0,
    alphaTO: 0,
    headingChange: 0,
    flatPitch: null,
  };
}

export class MotionTracker {
  mode: Mode = "walk"; // must match the app's initial mode selection
  params: TrackerParams = {
    gain: 1.0,
    leak: 1.2,
    zupt: 0.3,
    hp: 0.02,
    smooth: 2,
    detrend: true,
    closed: false,
    walkAccTh: 2.0,
    walkGyroTh: 40,
    walkN: 4,
  };

  calibrated = false;
  calibrating = false;
  calibrationStartedAt = 0;
  calibrationMs = 1500;
  calibrationBuffer: Vec3[] = [];
  gWorld: Vec3 = [0, 0, 0];
  unitScale = 1;
  r: Mat3 = [1, 0, 0, 0, 1, 0, 0, 0, 1];
  ori = { alpha: 0, beta: 0, gamma: 0 };
  accelSrc = "—";
  bias: Vec3 = [0, 0, 0];
  vel: Vec3 = [0, 0, 0];
  pos: Vec3 = [0, 0, 0];
  stillCount = 0;
  lastTMs = 0;
  dtEma = 0.02;
  rateHz = 0;
  hasMotion = false;
  recording = false;
  rawGesture: RawSample[] = [];
  gesturePath: PathPoint[] = [];
  walk: WalkState = freshWalk(false);

  startCalibration(nowMs: number, durationMs: number): void {
    this.unitScale = 1; // reset first, otherwise repeated calibration compounds the scale
    this.calibrated = false;
    this.calibrating = true;
    this.calibrationStartedAt = nowMs;
    this.calibrationMs = durationMs;
    this.calibrationBuffer = [];
    this.bias = [0, 0, 0];
    this.vel = [0, 0, 0];
    this.pos = [0, 0, 0];
    this.stillCount = 0;
    this.rawGesture = [];
    this.gesturePath = [];
    this.walk = freshWalk(false);
  }

  setMode(mode: Mode): void {
    this.mode = mode;
    if (mode === "gesture") this.stopWalk();
    else this.stopRecording();
  }

  startRecording(): void {
    if (!this.calibrated) throw new Error("Calibrate before recording");
    this.recording = true;
    this.rawGesture = [];
    this.gesturePath = [];
    this.vel = [0, 0, 0];
    this.pos = [0, 0, 0];
    this.bias = [0, 0, 0];
    this.stillCount = 0;
  }

  stopRecording(): void {
    if (!this.recording) return;
    this.recording = false;
    this.rebuild();
  }

  startWalk(): void {
    if (!this.calibrated) throw new Error("Calibrate before walking");
    this.walk = freshWalk(true);
    this.walk.flatPitch = this.ori.beta;
    this.walk.startT = this.lastTMs / 1000;
  }

  stopWalk(): void {
    this.walk.active = false;
  }

  clearWalk(): void {
    this.walk = freshWalk(this.walk.active);
    if (this.walk.active) this.walk.flatPitch = this.ori.beta;
  }

  clearGesture(): void {
    this.rawGesture = [];
    this.gesturePath = [];
    this.vel = [0, 0, 0];
    this.pos = [0, 0, 0];
  }

  process(frame: ImuFrame): void {
    this.hasMotion = true;
    if (frame.quat) {
      this.r = quatToMatrix(frame.quat.w, frame.quat.x, frame.quat.y, frame.quat.z);
      this.ori = matrixToEulerZXY(this.r);
    } else if (frame.euler) {
      this.ori = frame.euler;
      this.r = eulerToMatrix(frame.euler.alpha, frame.euler.beta, frame.euler.gamma);
    }

    const t = frame.tMs / 1000;
    let dt = this.lastTMs ? (frame.tMs - this.lastTMs) / 1000 : 0.016;
    this.lastTMs = frame.tMs;
    if (dt <= 0 || dt > 0.2) dt = 0.016;
    this.dtEma = this.dtEma * 0.9 + dt * 0.1;
    this.rateHz = 1 / Math.max(this.dtEma, 1e-3);

    const aWorld = matVec(this.r, [
      frame.aDev[0] * this.unitScale,
      frame.aDev[1] * this.unitScale,
      frame.aDev[2] * this.unitScale,
    ]);

    if (this.calibrating) {
      this.calibrationBuffer.push(aWorld);
      if (Date.now() - this.calibrationStartedAt >= this.calibrationMs && this.calibrationBuffer.length >= 20) {
        this.finishCalibration();
      }
      return;
    }
    if (!this.calibrated) return;

    // Prefer the platform's fused gravity-free acceleration when present: a 1°
    // orientation error only rotates that small vector, whereas manual gravity
    // subtraction leaves a ~0.17 m/s² constant drift per degree.
    let aLin: Vec3;
    const ua = frame.userAccel;
    if (ua && Number.isFinite(ua[0] + ua[1] + ua[2])) {
      aLin = matVec(this.r, [ua[0] * this.unitScale, ua[1] * this.unitScale, ua[2] * this.unitScale]);
      this.accelSrc = "fused userAccel";
    } else {
      aLin = [aWorld[0] - this.gWorld[0], aWorld[1] - this.gWorld[1], aWorld[2] - this.gWorld[2]];
      this.accelSrc = "gravity-subtracted";
    }

    if (this.mode === "walk") {
      if (this.walk.active) this.walkStep(aLin, mag3(aWorld), frame.rotRateMag, dt, t);
      return;
    }
    this.gestureStep(aLin, frame.rotRateMag, dt, t);
  }

  path(): PathPoint[] {
    if (this.mode === "walk") {
      const pts = this.walk.active ? this.walk.path.concat([this.walk.pLive]) : this.walk.path;
      return pts.map((p) => ({ x: p[0], y: p[1], z: p[2] }));
    }
    return this.gesturePath;
  }

  // Committed walk path with per-point elapsed seconds (for step replay).
  walkTimeline(): { points: PathPoint[]; times: number[] } {
    return {
      points: this.walk.path.map((p) => ({ x: p[0], y: p[1], z: p[2] })),
      times: this.walk.pathT,
    };
  }

  gaitSummary(): GaitSummary {
    const all = this.walk.strides;
    const core = all.length >= 4 ? all.slice(1, -1) : all;
    const valid = core.filter((s) => s.stanceT > 0);
    const stepTimes = valid.map((s) => s.swingT + s.stanceT).filter(Number.isFinite);
    const speeds = valid.map((s) => s.len / (s.swingT + s.stanceT)).filter(Number.isFinite);
    const stancePct = valid.map((s) => (s.stanceT / (s.swingT + s.stanceT)) * 100).filter(Number.isFinite);
    const strideTime = stat(stepTimes);
    const strideLength = stat(core.map((s) => s.len));
    const swingMean = mean(valid.map((s) => s.swingT));
    const stanceMean = mean(valid.map((s) => s.stanceT));
    const cycleMean = strideTime.mean;
    const peakVs = core.map((s) => s.peakV).filter(Number.isFinite);
    const pitchHS = mean(core.map((s) => s.pitchHS));
    const pitchTO = mean(core.map((s) => s.pitchTO));
    // Landing style from foot pitch at heel strike (relative to flat stance):
    // toe up (positive) = heel strikes first, near zero = flat, toe down = toe first.
    const landing = !Number.isFinite(pitchHS) ? "--" : pitchHS > 5 ? "heel-first" : pitchHS < -5 ? "toe-first" : "flat";
    return {
      strides: core.length,
      steps: this.walk.steps * 2,
      distanceM: this.walk.dist,
      cadence: stepTimes.length ? 60 / median(stepTimes) : Number.NaN,
      speed: speeds.length ? median(speeds) : Number.NaN,
      strideTimeMean: strideTime.mean,
      strideTimeCv: strideTime.cv,
      strideLengthMean: strideLength.mean,
      strideLengthCv: strideLength.cv,
      stancePct: mean(stancePct),
      clearance: mean(core.map((s) => s.clearance)),
      turnSteps: core.filter((s) => Math.abs(s.heading) >= 20).length,
      totalTurn: all.reduce((sum, s) => sum + Math.abs(s.heading), 0),
      stepCount: this.walk.steps,
      stepPace: Number.isFinite(cycleMean) && cycleMean > 0 ? 120 / cycleMean : Number.NaN,
      swingTimeMean: swingMean,
      stanceTimeMean: stanceMean,
      gaitCycleMean: cycleMean,
      maxFootVelocity: peakVs.length ? Math.max(...peakVs) * 1000 : Number.NaN,
      avgFootVelocity: speeds.length ? median(speeds) * 1000 : Number.NaN,
      pitchHSMean: pitchHS,
      pitchTOMean: pitchTO,
      landingPosition: landing,
    };
  }

  exportPayload(source: string): unknown {
    if (this.mode === "walk") {
      return {
        kind: "walk",
        meta: { source, rateHz: this.rateHz, gWorld: this.gWorld },
        summary: this.gaitSummary(),
        strides: this.walk.strides,
        path: this.path(),
      };
    }
    return {
      kind: "gesture",
      meta: { source, rateHz: this.rateHz, gWorld: this.gWorld, params: this.params },
      samples: this.gesturePath,
      raw: this.rawGesture,
    };
  }

  exportCsv(): string {
    if (this.mode === "walk") {
      const header = "t,swingT,stanceT,len,peakV,peakGyro,peakAcc,clearance,heading,pitchHS,pitchTO\n";
      const rows = this.walk.strides
        .map((s) => [s.t, s.swingT, s.stanceT, s.len, s.peakV, s.peakGyro, s.peakAcc, s.clearance, s.heading, s.pitchHS, s.pitchTO]
          .map((v) => Number(v).toFixed(4)).join(","))
        .join("\n");
      return header + rows;
    }
    const header = "t,dt,ax,ay,az,alpha,beta,gamma,px,py,pz\n";
    const rows = this.rawGesture
      .map((r, i) => {
        const p = this.gesturePath[i] || { x: 0, y: 0, z: 0 };
        return [r.t, r.dt, r.aw[0], r.aw[1], r.aw[2], r.alpha, r.beta, r.gamma, p.x, p.y, p.z]
          .map((v) => Number(v).toFixed(5)).join(",");
      })
      .join("\n");
    return header + rows;
  }

  private finishCalibration(): void {
    const n = this.calibrationBuffer.length;
    const avg: Vec3 = [0, 0, 0];
    for (const v of this.calibrationBuffer) {
      avg[0] += v[0];
      avg[1] += v[1];
      avg[2] += v[2];
    }
    avg[0] /= n;
    avg[1] /= n;
    avg[2] /= n;
    const gm = mag3(avg);
    // Some Android devices report g-units instead of m/s²; rescale if |g| looks like 1.
    this.unitScale = gm > 0.3 && gm < 3 ? 9.80665 / gm : 1;
    this.gWorld = [avg[0] * this.unitScale, avg[1] * this.unitScale, avg[2] * this.unitScale];
    this.calibrating = false;
    this.calibrated = true;
  }

  private gestureStep(aLin: Vec3, rotRateMag: number, dt: number, t: number): void {
    const k = this.params.hp;
    this.bias = [
      this.bias[0] + (aLin[0] - this.bias[0]) * k,
      this.bias[1] + (aLin[1] - this.bias[1]) * k,
      this.bias[2] + (aLin[2] - this.bias[2]) * k,
    ];
    const aHp: Vec3 = [aLin[0] - this.bias[0], aLin[1] - this.bias[1], aLin[2] - this.bias[2]];
    const still = mag3(aHp) < this.params.zupt && mag3(this.vel) < 0.15 && rotRateMag < 12;
    this.stillCount = still ? this.stillCount + 1 : 0;
    const gain = this.params.gain;
    this.vel = [this.vel[0] + aHp[0] * dt * gain, this.vel[1] + aHp[1] * dt * gain, this.vel[2] + aHp[2] * dt * gain];
    if (this.stillCount > 6) this.vel = [0, 0, 0];
    else {
      const decay = Math.max(0, 1 - this.params.leak * dt);
      this.vel = [this.vel[0] * decay, this.vel[1] * decay, this.vel[2] * decay];
    }
    this.pos = [this.pos[0] + this.vel[0] * dt, this.pos[1] + this.vel[1] * dt, this.pos[2] + this.vel[2] * dt];

    if (this.recording) {
      this.rawGesture.push({ t, dt, aw: [aLin[0], aLin[1], aLin[2]], alpha: this.ori.alpha, beta: this.ori.beta, gamma: this.ori.gamma });
      // Live causal preview; replaced by the acausal rebuild on stop.
      this.gesturePath.push({ x: this.pos[0], y: this.pos[1], z: this.pos[2] });
    }
  }

  // Batch reconstruction with rest→move→rest boundary constraints — identical
  // to the web app: smooth, zero-mean accel, integrate, linear-detrend the
  // velocity so it ends at 0, integrate again, optionally close the loop.
  rebuild(): void {
    const raw = this.rawGesture;
    const n = raw.length;
    if (n < 3) return;
    const totalT = raw[n - 1].t - raw[0].t || 1;

    const w = Math.max(0, Math.floor(this.params.smooth));
    let accel = raw.map((r) => r.aw.slice() as Vec3);
    if (w > 0) {
      const smoothed: Vec3[] = [];
      for (let i = 0; i < n; i++) {
        const out: Vec3 = [0, 0, 0];
        let c = 0;
        for (let j = Math.max(0, i - w); j <= Math.min(n - 1, i + w); j++) {
          out[0] += accel[j][0];
          out[1] += accel[j][1];
          out[2] += accel[j][2];
          c++;
        }
        smoothed.push([out[0] / c, out[1] / c, out[2] / c]);
      }
      accel = smoothed;
    }

    if (this.params.detrend) {
      const avg: Vec3 = [0, 0, 0];
      for (const a of accel) {
        avg[0] += a[0];
        avg[1] += a[1];
        avg[2] += a[2];
      }
      avg[0] /= n;
      avg[1] /= n;
      avg[2] /= n;
      for (const a of accel) {
        a[0] -= avg[0];
        a[1] -= avg[1];
        a[2] -= avg[2];
      }
    }

    const velocity: Vec3[] = [[0, 0, 0]];
    for (let i = 1; i < n; i++) {
      const prev = velocity[i - 1];
      const dt = raw[i].dt;
      velocity.push([prev[0] + accel[i][0] * dt, prev[1] + accel[i][1] * dt, prev[2] + accel[i][2] * dt]);
    }

    if (this.params.detrend) {
      const endV = velocity[n - 1];
      for (let i = 0; i < n; i++) {
        const f = (raw[i].t - raw[0].t) / totalT;
        velocity[i] = [velocity[i][0] - endV[0] * f, velocity[i][1] - endV[1] * f, velocity[i][2] - endV[2] * f];
      }
    }

    const path: Vec3[] = [[0, 0, 0]];
    for (let i = 1; i < n; i++) {
      const prev = path[i - 1];
      const dt = raw[i].dt;
      path.push([prev[0] + velocity[i][0] * dt, prev[1] + velocity[i][1] * dt, prev[2] + velocity[i][2] * dt]);
    }

    if (this.params.closed) {
      const endP = path[n - 1];
      for (let i = 0; i < n; i++) {
        const f = (raw[i].t - raw[0].t) / totalT;
        path[i] = [path[i][0] - endP[0] * f, path[i][1] - endP[1] * f, path[i][2] - endP[2] * f];
      }
    }

    this.gesturePath = path.map((p) => ({ x: p[0], y: p[1], z: p[2] }));
  }

  private walkStep(aLin: Vec3, accMag: number, rotRateMag: number, dt: number, now: number): void {
    const w = this.walk;
    const isStance = Math.abs(accMag - 9.80665) < this.params.walkAccTh && rotRateMag < this.params.walkGyroTh;
    if (isStance) {
      w.stanceCount++;
      w.moveCount = 0;
    } else {
      w.moveCount++;
      w.stanceCount = 0;
    }

    if (!w.inStance && w.stanceCount >= this.params.walkN) {
      w.pitchHS = this.ori.beta;
      w.headingChange = wrap180(this.ori.alpha - w.alphaTO);
      this.commitStride();
      w.inStance = true;
      w.v = [0, 0, 0];
      w.pLive = w.p.slice() as Vec3;
      w.stanceStartT = now;
    } else if (w.inStance && w.moveCount >= this.params.walkN) {
      w.inStance = false;
      w.swing = [];
      w.v = [0, 0, 0];
      w.pLive = w.p.slice() as Vec3;
      w.pendingStanceT = w.stanceStartT > 0 ? now - w.stanceStartT : 0;
      w.pitchTO = this.ori.beta;
      w.alphaTO = this.ori.alpha;
      w.peakGyro = 0;
      w.peakAcc = 0;
    }

    if (w.inStance) {
      w.v = [0, 0, 0];
      w.pLive = w.p.slice() as Vec3;
    } else {
      w.swing.push({ aw: aLin, dt, t: now });
      w.peakGyro = Math.max(w.peakGyro, rotRateMag);
      w.peakAcc = Math.max(w.peakAcc, accMag);
      w.v = [w.v[0] + aLin[0] * dt, w.v[1] + aLin[1] * dt, w.v[2] + aLin[2] * dt];
      w.pLive = [w.pLive[0] + w.v[0] * dt, w.pLive[1] + w.v[1] * dt, w.pLive[2] + w.v[2] * dt];
    }
  }

  private commitStride(): void {
    const w = this.walk;
    const sw = w.swing;
    if (sw.length < 3) return;

    const velocity: Vec3[] = [[0, 0, 0]];
    for (let i = 1; i < sw.length; i++) {
      const prev = velocity[i - 1];
      velocity.push([prev[0] + sw[i].aw[0] * sw[i].dt, prev[1] + sw[i].aw[1] * sw[i].dt, prev[2] + sw[i].aw[2] * sw[i].dt]);
    }
    const totalT = sw[sw.length - 1].t - sw[0].t || 1;
    const endV = velocity[velocity.length - 1];
    for (let i = 0; i < velocity.length; i++) {
      const f = (sw[i].t - sw[0].t) / totalT;
      velocity[i] = [velocity[i][0] - endV[0] * f, velocity[i][1] - endV[1] * f, velocity[i][2] - endV[2] * f];
    }

    const z = this.verticalArc(sw);
    const zMax = Math.max(...z);
    const zMin = Math.min(...z);
    const zFlip = -zMin > zMax ? -1 : 1;
    const clearance = Math.max(zMax, -zMin);
    let p = w.p.slice() as Vec3;
    let peakV = 0;

    for (let i = 1; i < sw.length; i++) {
      p = [p[0] + velocity[i][0] * sw[i].dt, p[1] + velocity[i][1] * sw[i].dt, 0];
      w.path.push([p[0], p[1], Math.max(0, z[i] * zFlip)]);
      w.pathT.push(sw[i].t - w.startT);
      peakV = Math.max(peakV, Math.hypot(velocity[i][0], velocity[i][1]));
    }

    const strideLen = Math.hypot(p[0] - w.p[0], p[1] - w.p[1]);
    if (strideLen > 0.1 && strideLen < 2.0) {
      w.steps++;
      w.dist += strideLen;
      const flatPitch = w.flatPitch;
      w.strides.push({
        t: sw[sw.length - 1].t,
        swingT: totalT,
        stanceT: w.pendingStanceT || 0,
        len: strideLen,
        peakV,
        peakGyro: w.peakGyro,
        peakAcc: w.peakAcc,
        clearance,
        heading: w.headingChange || 0,
        pitchHS: flatPitch != null ? w.pitchHS - flatPitch : w.pitchHS,
        pitchTO: flatPitch != null ? w.pitchTO - flatPitch : w.pitchTO,
      });
    }
    w.p = [p[0], p[1], 0];
  }

  private verticalArc(sw: { aw: Vec3; dt: number; t: number }[]): number[] {
    const az = sw.map((_, i) => {
      let sum = 0;
      let count = 0;
      for (let j = Math.max(0, i - 2); j <= Math.min(sw.length - 1, i + 2); j++) {
        sum += sw[j].aw[2];
        count++;
      }
      return sum / count;
    });
    const vz = [0];
    for (let i = 1; i < sw.length; i++) vz.push(vz[i - 1] + az[i] * sw[i].dt);
    const totalT = sw[sw.length - 1].t - sw[0].t || 1;
    const endVz = vz[vz.length - 1];
    for (let i = 0; i < vz.length; i++) vz[i] -= endVz * ((sw[i].t - sw[0].t) / totalT);
    const z = [0];
    for (let i = 1; i < sw.length; i++) z.push(z[i - 1] + vz[i] * sw[i].dt);
    const endZ = z[z.length - 1];
    for (let i = 0; i < z.length; i++) z[i] -= endZ * ((sw[i].t - sw[0].t) / totalT);
    return z;
  }
}
