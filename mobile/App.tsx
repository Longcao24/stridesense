import AsyncStorage from "@react-native-async-storage/async-storage";
import { StatusBar } from "expo-status-bar";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Alert, PermissionsAndroid, Platform, SafeAreaView, ScrollView, Share, StyleSheet, Switch, Text, TextInput, TouchableOpacity, View } from "react-native";
import { FootSide, XiaoPodManager, XiaoSample } from "./src/ble/xiao";
import { exportAndShare } from "./src/cloud/exportFile";
import { uploadMotion } from "./src/cloud/upload";
import { GaitSummary, Mode, MotionTracker } from "./src/tracking/tracker";
import { AttitudeView } from "./src/ui/AttitudeView";
import { PathSeries, PathView3D } from "./src/ui/PathView3D";

const CLOUD_URL_KEY = "cloudUploadUrl";
const DEFAULT_UPLOAD_URL = "https://phone-motion-tracker-upload.longcao.workers.dev/upload";
const SIDE_COLOR: Record<FootSide, string> = { L: "#4cc2ff", R: "#f0883e" };
const SIDES: FootSide[] = ["L", "R"];

function fmt(value: number, digits = 1, suffix = ""): string {
  return Number.isFinite(value) ? `${value.toFixed(digits)}${suffix}` : "--";
}

// Symmetry index: 0% = perfectly symmetric gait, larger = more asymmetric.
function symmetry(a: number, b: number): number {
  if (!Number.isFinite(a) || !Number.isFinite(b) || a + b === 0) return Number.NaN;
  return (Math.abs(a - b) / ((a + b) / 2)) * 100;
}

// Each pod's 6-axis AHRS has an arbitrary yaw (relative to its boot pose), so
// the two feet walk in rotated frames. Rotate each path so its first
// significant displacement points +Y, making L/R overlays comparable.
function alignHeading(points: { x: number; y: number; z: number }[]): { x: number; y: number; z: number }[] {
  let i = 1;
  while (i < points.length && Math.hypot(points[i].x, points[i].y) < 0.3) i++;
  if (i >= points.length) return points;
  const a = Math.atan2(points[i].x, points[i].y);
  const c = Math.cos(a);
  const s = Math.sin(a);
  return points.map((p) => ({ x: p.x * c - p.y * s, y: p.x * s + p.y * c, z: p.z }));
}

export default function App(): React.JSX.Element {
  const podsRef = useRef<XiaoPodManager | null>(null);
  const trackersRef = useRef<Record<FootSide, MotionTracker>>({ L: new MotionTracker(), R: new MotionTracker() });
  const [connectedSides, setConnectedSides] = useState<FootSide[]>([]);
  const [connecting, setConnecting] = useState(false);
  const [status, setStatus] = useState("Connect the foot pods to begin.");
  const [mode, setModeState] = useState<Mode>("walk");
  const [lastSamples, setLastSamples] = useState<Partial<Record<FootSide, XiaoSample>>>({});
  const [tick, setTick] = useState(0);
  const [uploadUrl, setUploadUrl] = useState(DEFAULT_UPLOAD_URL);
  const [replayT, setReplayT] = useState<number | null>(null); // gesture replay 0..1
  const [simT, setSimT] = useState<number | null>(null); // walk simulation, seconds
  const [smooth, setSmooth] = useState(2);
  const [detrend, setDetrend] = useState(true);
  const [closed, setClosed] = useState(false);
  // Completed-walk distances, for path variation across repeated experiments.
  const [walkSessions, setWalkSessions] = useState<number[]>([]);
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  const trackers = trackersRef.current;
  const primary: FootSide = connectedSides[0] ?? "L";
  const primaryTracker = trackers[primary];
  const dual = connectedSides.length === 2;

  useEffect(() => {
    AsyncStorage.getItem(CLOUD_URL_KEY).then((v) => setUploadUrl(v || DEFAULT_UPLOAD_URL));
    // Keep tracker mode in sync with the UI's initial selection.
    for (const side of SIDES) trackers[side].setMode(mode);
    return () => {
      void podsRef.current?.destroy();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const id = setInterval(() => setTick((x) => x + 1), 250);
    return () => clearInterval(id);
  }, []);

  // Gesture replay sweep (~2.5 s).
  useEffect(() => {
    if (replayT == null) return;
    if (replayT >= 1) {
      setReplayT(null);
      return;
    }
    const id = setTimeout(() => setReplayT(replayT + 0.02), 40);
    return () => clearTimeout(id);
  }, [replayT]);

  // Walk step simulation: advance a shared clock over both feet's timelines.
  const walkDuration = useMemo(() => {
    let max = 0;
    for (const side of connectedSides) {
      const t = trackers[side].walkTimeline().times;
      if (t.length) max = Math.max(max, t[t.length - 1]);
    }
    return max;
  }, [connectedSides, tick]);

  useEffect(() => {
    if (simT == null) return;
    if (simT >= walkDuration) {
      setSimT(null);
      return;
    }
    const id = setTimeout(() => setSimT(simT + 0.1), 50); // 2x speed
    return () => clearTimeout(id);
  }, [simT, walkDuration]);

  async function connectPods(): Promise<void> {
    const allowed = await requestBlePermissions();
    if (!allowed) {
      setStatus("Bluetooth permission denied.");
      return;
    }
    setConnecting(true);
    setStatus("Scanning for foot pods (L/R)...");
    await podsRef.current?.destroy();
    const pods = new XiaoPodManager();
    podsRef.current = pods;
    try {
      const found = await pods.scanPods(10000);
      if (!found.length) {
        setStatus("No pod found. Check power and BLE advertising.");
        setConnecting(false);
        return;
      }
      for (const pod of found) {
        setStatus(`Connecting ${pod.name} (${pod.side})...`);
        await pods.connectPod(pod, {
          onSample: (side, sample) => {
            setLastSamples((prev) => (prev[side] === sample ? prev : { ...prev, [side]: sample }));
            trackers[side].process({
              tMs: sample.timestampMs,
              aDev: [sample.ax, sample.ay, sample.az],
              quat: { w: sample.qw, x: sample.qx, y: sample.qy, z: sample.qz },
              userAccel: null,
              rotRateMag: Math.hypot(sample.gx, sample.gy, sample.gz),
            });
          },
          onError: (side, message) => setStatus(`[${side}] ${message}`),
          onDisconnected: (side) => {
            setConnectedSides(pods.connectedSides);
            setStatus(`Pod ${side} disconnected.`);
          },
        });
      }
      setConnectedSides(pods.connectedSides);
      const names = found.map((p) => `${p.side}✓`).join(" ");
      setStatus(`Connected ${names}. Pods auto-calibrate while still; run ② for gravity.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : String(error));
    } finally {
      setConnecting(false);
    }
  }

  async function disconnectPods(): Promise<void> {
    await podsRef.current?.disconnectAll();
    setConnectedSides([]);
    setStatus("Disconnected.");
  }

  function calibrate(): void {
    if (!connectedSides.length) {
      Alert.alert("No pods", "Connect the foot pods first.");
      return;
    }
    const busy = connectedSides.some((s) => trackers[s].recording || trackers[s].walk.active);
    if (busy) {
      Alert.alert("Busy", "Stop recording / walking before calibrating.");
      return;
    }
    // No BLE command: the pods auto-calibrate their gyro bias while still.
    // This estimates each pod's world gravity vector.
    const ms = 2800;
    for (const side of connectedSides) trackers[side].startCalibration(Date.now(), ms);
    setStatus(`Calibrating ${connectedSides.join("+")}... keep both pods still for ${(ms / 1000).toFixed(1)}s.`);
    setTimeout(() => {
      const done = connectedSides.filter((s) => trackers[s].calibrated);
      setStatus(
        done.length === connectedSides.length
          ? `Calibration done (${done.join("+")}). Start walking or record a gesture.`
          : `Calibrated ${done.join("+") || "none"} — retry for the rest (keep pods still).`,
      );
      setTick((x) => x + 1);
    }, ms + 400);
  }

  function setMode(next: Mode): void {
    for (const side of SIDES) trackers[side].setMode(next);
    setModeState(next);
    setReplayT(null);
    setSimT(null);
    setStatus(next === "gesture" ? `Gesture mode (pod ${primary}): record, rebuild, replay.` : "Walk mode: per-stride ZUPT on each foot.");
  }

  function toggleWalk(): void {
    try {
      const active = connectedSides.some((s) => trackers[s].walk.active);
      if (active) {
        for (const side of connectedSides) trackers[side].stopWalk();
        const dists = connectedSides.map((s) => trackers[s].gaitSummary().distanceM).filter((d) => d > 0.2);
        if (dists.length) setWalkSessions((prev) => [...prev, dists.reduce((a, b) => a + b, 0) / dists.length]);
        setStatus("Walk tracking stopped. Tap ▶ Simulate to replay the steps.");
      } else {
        // Start each foot independently so one uncalibrated pod can't silently
        // knock the other out of the session.
        const started: FootSide[] = [];
        const skipped: FootSide[] = [];
        for (const side of connectedSides) {
          try {
            trackers[side].startWalk();
            started.push(side);
          } catch {
            skipped.push(side);
          }
        }
        if (!started.length) {
          Alert.alert("Calibration needed", "Run ② Calibrate (pods still) before walking.");
          return;
        }
        setSimT(null);
        setStatus(
          skipped.length
            ? `Walking with ${started.join("+")} only — ${skipped.join("+")} not calibrated! Stop, run ②, and restart.`
            : dual
              ? "Walking — tracking both feet."
              : "Walking — single pod.",
        );
      }
      setTick((x) => x + 1);
    } catch (error) {
      Alert.alert("Walk", error instanceof Error ? error.message : String(error));
    }
  }

  function toggleRecord(): void {
    const recording = connectedSides.some((s) => trackers[s].recording);
    if (recording) {
      for (const side of connectedSides) trackers[side].stopRecording();
      const counts = connectedSides.map((s) => `${s}:${trackers[s].rawGesture.length}`).join(" ");
      setStatus(`Recording stopped — ${counts} samples reconstructed.`);
    } else {
      const started: FootSide[] = [];
      const skipped: FootSide[] = [];
      for (const side of connectedSides) {
        try {
          trackers[side].startRecording();
          started.push(side);
        } catch {
          skipped.push(side);
        }
      }
      if (!started.length) {
        Alert.alert("Calibration needed", "Run ② Calibrate (pods still) before recording.");
        return;
      }
      setReplayT(null);
      setStatus(
        skipped.length
          ? `Recording ${started.join("+")} only — ${skipped.join("+")} not calibrated!`
          : "Recording both pods. Start still, draw for 2-4 s, end still.",
      );
    }
    setTick((x) => x + 1);
  }

  function rebuild(nextSmooth = smooth, nextDetrend = detrend, nextClosed = closed): void {
    for (const side of SIDES) {
      trackers[side].params.smooth = nextSmooth;
      trackers[side].params.detrend = nextDetrend;
      trackers[side].params.closed = nextClosed;
      trackers[side].rebuild();
    }
    setTick((x) => x + 1);
  }

  function exportPayload(): unknown {
    if (mode === "walk" && dual) {
      return {
        kind: "walk_dual",
        meta: { source: "xiao_nrf52840_dual", rateHz: { L: trackers.L.rateHz, R: trackers.R.rateHz } },
        left: { summary: trackers.L.gaitSummary(), strides: trackers.L.walk.strides, path: trackers.L.walkTimeline() },
        right: { summary: trackers.R.gaitSummary(), strides: trackers.R.walk.strides, path: trackers.R.walkTimeline() },
      };
    }
    if (mode === "gesture" && dual) {
      return {
        kind: "gesture_dual",
        meta: { source: "xiao_nrf52840_dual", rateHz: { L: trackers.L.rateHz, R: trackers.R.rateHz }, params: trackers.L.params },
        left: { samples: trackers.L.gesturePath, raw: trackers.L.rawGesture },
        right: { samples: trackers.R.gesturePath, raw: trackers.R.rawGesture },
      };
    }
    return primaryTracker.exportPayload("xiao_nrf52840");
  }

  async function exportJson(): Promise<void> {
    try {
      await exportAndShare(mode === "walk" ? "walk_data.json" : "gesture_data.json", "application/json", JSON.stringify(exportPayload(), null, 2));
    } catch (error) {
      setStatus(error instanceof Error ? error.message : String(error));
    }
  }

  async function exportCsv(): Promise<void> {
    try {
      await exportAndShare(mode === "walk" ? "walk_data.csv" : "gesture_data.csv", "text/csv", primaryTracker.exportCsv());
    } catch (error) {
      setStatus(error instanceof Error ? error.message : String(error));
    }
  }

  async function saveUploadUrl(): Promise<void> {
    await AsyncStorage.setItem(CLOUD_URL_KEY, uploadUrl.trim());
    setStatus("Upload URL saved.");
  }

  async function upload(): Promise<void> {
    try {
      setStatus("Uploading...");
      const name = await uploadMotion(uploadUrl, exportPayload());
      // The worker serves a public share viewer at /view/<name>.
      const base = uploadUrl.trim().replace(/\/upload\/?$/, "");
      const link = `${base}/view/${encodeURIComponent(name.trim())}`;
      setShareUrl(link);
      setStatus(`Uploaded ✓ public link ready — tap Share link.`);
    } catch (error) {
      setShareUrl(null);
      setStatus(error instanceof Error ? error.message : String(error));
    }
  }

  async function shareLink(): Promise<void> {
    if (!shareUrl) return;
    await Share.share({ message: shareUrl });
  }

  // Path series for the trajectory card.
  const pathSeries: PathSeries[] = useMemo(() => {
    if (mode === "gesture") {
      const sides = connectedSides.length ? connectedSides : ([primary] as FootSide[]);
      return sides.map((side) => ({ label: side, color: SIDE_COLOR[side], points: trackers[side].gesturePath }));
    }
    const sides = connectedSides.length ? connectedSides : (["L"] as FootSide[]);
    if (simT != null) {
      return sides.map((side) => {
        const { points, times } = trackers[side].walkTimeline();
        const aligned = alignHeading(points);
        let count = 1;
        while (count < aligned.length && times[count] <= simT) count++;
        return { label: side, color: SIDE_COLOR[side], points: aligned.slice(0, count) };
      });
    }
    return sides.map((side) => ({ label: side, color: SIDE_COLOR[side], points: alignHeading(trackers[side].path()) }));
  }, [mode, connectedSides, simT, tick, primary]);

  const gaits: Partial<Record<FootSide, GaitSummary>> = {};
  for (const side of connectedSides) gaits[side] = trackers[side].gaitSummary();
  const gaitPrimary = gaits[primary] ?? primaryTracker.gaitSummary();

  const walkActive = connectedSides.some((s) => trackers[s].walk.active);
  const anyRecording = connectedSides.some((s) => trackers[s].recording);
  const canSimulate = mode === "walk" && !walkActive && walkDuration > 0.5;
  const canReplay = mode === "gesture" && !anyRecording && connectedSides.some((s) => trackers[s].gesturePath.length > 2);

  // Global (both-feet) figures for the feature table.
  const bothSpeeds = connectedSides.map((s) => gaits[s]?.speed ?? Number.NaN).filter(Number.isFinite);
  const walkingSpeed = bothSpeeds.length ? bothSpeeds.reduce((a, b) => a + b, 0) / bothSpeeds.length : Number.NaN;
  const speedDiffLR = dual ? Math.abs((gaits.L?.speed ?? Number.NaN) - (gaits.R?.speed ?? Number.NaN)) : Number.NaN;
  const bothCadence = connectedSides.map((s) => (gaits[s]?.cadence ?? Number.NaN) * 2).filter(Number.isFinite);
  const cadenceSpm = bothCadence.length ? bothCadence.reduce((a, b) => a + b, 0) / bothCadence.length : Number.NaN;
  const pathVariation = useMemo(() => {
    if (walkSessions.length < 2) return Number.NaN;
    const m = walkSessions.reduce((a, b) => a + b, 0) / walkSessions.length;
    const sd = Math.sqrt(walkSessions.reduce((a, b) => a + (b - m) ** 2, 0) / (walkSessions.length - 1));
    return m ? (sd / m) * 100 : Number.NaN;
  }, [walkSessions]);

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Motion Tracker</Text>
        <Text style={styles.subtitle}>Dual XIAO foot pods — gait & gesture tracking</Text>

        <View style={styles.card}>
          <View style={styles.row}>
            <Button
              label={connectedSides.length ? "Disconnect pods" : connecting ? "Scanning..." : "① Connect pods (L/R)"}
              onPress={connectedSides.length ? disconnectPods : connectPods}
              disabled={connecting}
              primary={!connectedSides.length}
            />
            <Button label="② Calibrate (still)" onPress={calibrate} primary={connectedSides.length > 0 && !primaryTracker.calibrated} />
          </View>
          <Text style={styles.status}>{status}</Text>
          <View style={styles.metricsRow}>
            {SIDES.map((side) => {
              const on = connectedSides.includes(side);
              const s = lastSamples[side];
              return (
                <View key={side} style={[styles.metric, on && { borderColor: SIDE_COLOR[side], borderWidth: 1 }]}>
                  <Text style={[styles.metricLabel, { color: SIDE_COLOR[side] }]}>{side === "L" ? "Left pod" : "Right pod"}</Text>
                  <Text style={[styles.metricValue, on && styles.good]}>
                    {on ? `${fmt(trackers[side].rateHz, 0)}Hz ${s?.calibrated ? "✓cal" : s?.calibrating ? "…" : ""}` : "off"}
                  </Text>
                </View>
              );
            })}
            <Metric
              label="Gravity"
              value={
                connectedSides.length
                  ? connectedSides.map((s) => `${s}${trackers[s].calibrating ? "…" : trackers[s].calibrated ? "✓" : "✗"}`).join(" ")
                  : "needed"
              }
              good={connectedSides.length > 0 && connectedSides.every((s) => trackers[s].calibrated)}
            />
          </View>
        </View>

        <View style={styles.card}>
          <View style={styles.segment}>
            <Segment label="🚶 Walk (PDR)" active={mode === "walk"} onPress={() => setMode("walk")} />
            <Segment label="✍ Gesture" active={mode === "gesture"} onPress={() => setMode("gesture")} />
          </View>
          {mode === "walk" ? (
            <View style={styles.row}>
              <Button label={walkActive ? "■ Stop walking" : "● Start walking"} onPress={toggleWalk} primary />
              <Button label={simT != null ? "■ Stop sim" : "▶ Simulate"} onPress={() => setSimT(simT != null ? null : 0)} disabled={!canSimulate && simT == null} />
              <Button
                label="Clear"
                onPress={() => {
                  for (const side of SIDES) trackers[side].clearWalk();
                  setSimT(null);
                  setTick((x) => x + 1);
                }}
              />
            </View>
          ) : (
            <View style={styles.row}>
              <Button label={anyRecording ? "■ Stop" : "● Record"} onPress={toggleRecord} primary />
              <Button label="▶ Replay" onPress={() => setReplayT(0)} disabled={!canReplay} />
              <Button
                label="Clear"
                onPress={() => {
                  for (const side of SIDES) trackers[side].clearGesture();
                  setReplayT(null);
                  setTick((x) => x + 1);
                }}
              />
            </View>
          )}
        </View>

        <View style={styles.card}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "baseline" }}>
            <Text style={styles.sectionTitle}>{mode === "walk" ? "Ground path" : "Gesture trajectory"}</Text>
            {simT != null ? <Text style={{ color: "#8b98a9", fontSize: 12 }}>t = {simT.toFixed(1)}s / {walkDuration.toFixed(1)}s</Text> : null}
          </View>
          <PathView3D
            series={pathSeries}
            progress={mode === "gesture" ? replayT ?? undefined : undefined}
            topView={mode === "walk"}
            showFootMarkers={simT != null}
          />
          {mode === "walk" ? (
            <View style={styles.metricsRow}>
              <Metric label="Distance L" value={fmt(gaits.L?.distanceM ?? Number.NaN, 2, "m")} />
              <Metric label="Distance R" value={fmt(gaits.R?.distanceM ?? Number.NaN, 2, "m")} />
              <Metric label="Strides" value={`${gaits.L?.strides ?? 0}+${gaits.R?.strides ?? 0}`} />
            </View>
          ) : (
            <Text style={styles.hint}>
              {connectedSides.some((s) => trackers[s].rawGesture.length)
                ? connectedSides.map((s) => `${s}: ${trackers[s].rawGesture.length} samples`).join(" · ")
                : "record a gesture to see its 3D path"}
            </Text>
          )}
        </View>

        {mode === "walk" ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Important features in gait analysis</Text>
            <GaitRow label="" l="Left" r="Right" sym="Sym%" header />
            <GaitRow label="1· Walking speed (m/s)" single={fmt(walkingSpeed, 2)} />
            <GaitRow label="2· Stride height (cm)" l={fmt((gaits.L?.clearance ?? Number.NaN) * 100, 1)} r={fmt((gaits.R?.clearance ?? Number.NaN) * 100, 1)} sym={fmt(symmetry(gaits.L?.clearance ?? Number.NaN, gaits.R?.clearance ?? Number.NaN), 0)} />
            <GaitRow label="3· Stride length (m)" l={fmt(gaits.L?.strideLengthMean ?? Number.NaN, 2)} r={fmt(gaits.R?.strideLengthMean ?? Number.NaN, 2)} sym={fmt(symmetry(gaits.L?.strideLengthMean ?? Number.NaN, gaits.R?.strideLengthMean ?? Number.NaN), 0)} />
            <GaitRow label="4· Landing position" l={gaits.L?.landingPosition ?? "--"} r={gaits.R?.landingPosition ?? "--"} sym="" />
            <GaitRow label="5· Path distance (m)" l={fmt(gaits.L?.distanceM ?? Number.NaN, 2)} r={fmt(gaits.R?.distanceM ?? Number.NaN, 2)} sym={fmt(symmetry(gaits.L?.distanceM ?? Number.NaN, gaits.R?.distanceM ?? Number.NaN), 0)} />
            <GaitRow label="6· Path variation (%)" single={walkSessions.length < 2 ? `${walkSessions.length}/2+ walks` : fmt(pathVariation, 1)} dim={walkSessions.length < 2} />
            <GaitRow label="7· Leg speed (mm/s)" l={fmt(gaits.L?.avgFootVelocity ?? Number.NaN, 0)} r={fmt(gaits.R?.avgFootVelocity ?? Number.NaN, 0)} sym={fmt(symmetry(gaits.L?.avgFootVelocity ?? Number.NaN, gaits.R?.avgFootVelocity ?? Number.NaN), 0)} />
            <GaitRow label="8· Speed diff L–R (m/s)" single={fmt(speedDiffLR, 3)} />
            <GaitRow label="9· Foot orientation (° HS/TO)" l={`${fmt(gaits.L?.pitchHSMean ?? Number.NaN, 0)}/${fmt(gaits.L?.pitchTOMean ?? Number.NaN, 0)}`} r={`${fmt(gaits.R?.pitchHSMean ?? Number.NaN, 0)}/${fmt(gaits.R?.pitchTOMean ?? Number.NaN, 0)}`} sym="" />
            <GaitRow label="10· Cadence (steps/min)" single={fmt(cadenceSpm, 0)} />
            <GaitRow label="11· Swing time (s)" l={fmt(gaits.L?.swingTimeMean ?? Number.NaN, 3)} r={fmt(gaits.R?.swingTimeMean ?? Number.NaN, 3)} sym={fmt(symmetry(gaits.L?.swingTimeMean ?? Number.NaN, gaits.R?.swingTimeMean ?? Number.NaN), 0)} />
            <Text style={styles.hint}>
              {dual
                ? "Landing position & foot orientation from foot pitch at heel-strike/toe-off. Path variation needs 2+ completed walks."
                : "Connect both pods to fill the Right column and L–R comparisons."}
            </Text>
          </View>
        ) : (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Reconstruction (tweak if the shape is off)</Text>
            <View style={styles.paramRow}>
              <Text style={styles.paramLabel}>Smoothing window: {smooth}</Text>
              <View style={{ flexDirection: "row", gap: 8 }}>
                <Stepper label="−" onPress={() => { const v = Math.max(0, smooth - 1); setSmooth(v); rebuild(v); }} />
                <Stepper label="+" onPress={() => { const v = Math.min(10, smooth + 1); setSmooth(v); rebuild(v); }} />
              </View>
            </View>
            <View style={styles.paramRow}>
              <Text style={styles.paramLabel}>Rest-boundary de-drift (recommended)</Text>
              <Switch value={detrend} onValueChange={(v) => { setDetrend(v); rebuild(smooth, v); }} trackColor={{ true: "#4cc2ff" }} />
            </View>
            <View style={styles.paramRow}>
              <Text style={styles.paramLabel}>Closed gesture (loops/circles)</Text>
              <Switch value={closed} onValueChange={(v) => { setClosed(v); rebuild(smooth, detrend, v); }} trackColor={{ true: "#4cc2ff" }} />
            </View>
            <Button label="↻ Rebuild with current params" onPress={() => rebuild()} primary disabled={primaryTracker.rawGesture.length < 3} />
          </View>
        )}

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Attitude</Text>
          {connectedSides.length ? (
            <View style={{ flexDirection: "row", justifyContent: "space-around" }}>
              {connectedSides.map((side) => (
                <View key={side} style={{ alignItems: "center", flex: 1 }}>
                  <AttitudeView r={trackers[side].r} label={side} width={160} height={150} color={SIDE_COLOR[side]} />
                  <Text style={{ color: SIDE_COLOR[side], fontSize: 11, fontWeight: "700" }}>
                    {side} · α{fmt(trackers[side].ori.alpha, 0)}° β{fmt(trackers[side].ori.beta, 0)}° γ{fmt(trackers[side].ori.gamma, 0)}°
                  </Text>
                </View>
              ))}
            </View>
          ) : (
            <AttitudeView r={primaryTracker.r} label="pod" />
          )}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Export & upload</Text>
          <View style={styles.row}>
            <Button label="⬇ JSON" onPress={exportJson} />
            <Button label="⬇ CSV" onPress={exportCsv} />
          </View>
          <TextInput
            value={uploadUrl}
            onChangeText={setUploadUrl}
            autoCapitalize="none"
            autoCorrect={false}
            placeholder={DEFAULT_UPLOAD_URL}
            placeholderTextColor="#56627a"
            style={styles.input}
          />
          <View style={styles.row}>
            <Button label="Save URL" onPress={saveUploadUrl} />
            <Button label="⬆ Upload" onPress={upload} primary />
          </View>
          {shareUrl ? (
            <>
              <View style={styles.row}>
                <Button label="🔗 Share link" onPress={shareLink} primary />
              </View>
              <Text style={styles.hint} selectable>
                {shareUrl}
              </Text>
            </>
          ) : null}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

async function requestBlePermissions(): Promise<boolean> {
  if (Platform.OS !== "android") return true;

  if (Platform.Version >= 31) {
    const result = await PermissionsAndroid.requestMultiple([
      PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN,
      PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT,
    ]);
    return Object.values(result).every((value) => value === PermissionsAndroid.RESULTS.GRANTED);
  }

  const result = await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION);
  return result === PermissionsAndroid.RESULTS.GRANTED;
}

function Button({ label, onPress, primary, disabled }: { label: string; onPress: () => void; primary?: boolean; disabled?: boolean }): React.JSX.Element {
  return (
    <TouchableOpacity onPress={onPress} disabled={disabled} style={[styles.button, primary && styles.buttonPrimary, disabled && styles.disabled]}>
      <Text style={[styles.buttonText, primary && styles.buttonTextPrimary]}>{label}</Text>
    </TouchableOpacity>
  );
}

function Stepper({ label, onPress }: { label: string; onPress: () => void }): React.JSX.Element {
  return (
    <TouchableOpacity onPress={onPress} style={styles.stepper}>
      <Text style={styles.stepperText}>{label}</Text>
    </TouchableOpacity>
  );
}

function Segment({ label, active, onPress }: { label: string; active: boolean; onPress: () => void }): React.JSX.Element {
  return (
    <TouchableOpacity onPress={onPress} style={[styles.segmentButton, active && styles.segmentActive]}>
      <Text style={[styles.segmentText, active && styles.segmentTextActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

function Metric({ label, value, good }: { label: string; value: string; good?: boolean }): React.JSX.Element {
  return (
    <View style={styles.metric}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={[styles.metricValue, good && styles.good]}>{value}</Text>
    </View>
  );
}

function GaitRow({ label, l, r, sym, single, header, dim }: { label: string; l?: string; r?: string; sym?: string; single?: string; header?: boolean; dim?: boolean }): React.JSX.Element {
  const style = header ? styles.gaitHeader : styles.gaitCell;
  return (
    <View style={styles.gaitRow}>
      <Text style={[styles.gaitLabel, header && styles.gaitHeader]}>{label}</Text>
      {single != null ? (
        <Text style={[styles.gaitCell, { flex: 3, color: dim ? "#56627a" : "#e6edf3" }]}>{single}</Text>
      ) : (
        <>
          <Text style={[style, { color: header ? SIDE_COLOR.L : "#e6edf3" }]}>{l}</Text>
          <Text style={[style, { color: header ? SIDE_COLOR.R : "#e6edf3" }]}>{r}</Text>
          <Text style={[style, { color: header ? "#8b98a9" : "#3fb950" }]}>{sym}</Text>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#0b0e14" },
  container: { padding: 14, paddingBottom: 40 },
  title: { color: "#e6edf3", fontSize: 24, fontWeight: "700" },
  subtitle: { color: "#8b98a9", fontSize: 13, marginBottom: 12 },
  card: { backgroundColor: "#141a24", borderColor: "#2a3445", borderWidth: 1, borderRadius: 10, padding: 12, marginBottom: 12 },
  row: { flexDirection: "row", gap: 8, marginTop: 8 },
  status: { color: "#8b98a9", fontSize: 13, lineHeight: 19, marginTop: 10 },
  hint: { color: "#56627a", fontSize: 12, marginTop: 6 },
  button: { flex: 1, backgroundColor: "#1b2330", borderColor: "#2a3445", borderWidth: 1, borderRadius: 8, paddingVertical: 12, alignItems: "center" },
  buttonPrimary: { backgroundColor: "#4cc2ff", borderColor: "#4cc2ff" },
  buttonText: { color: "#e6edf3", fontWeight: "600", fontSize: 13 },
  buttonTextPrimary: { color: "#06202e" },
  disabled: { opacity: 0.45 },
  metricsRow: { flexDirection: "row", gap: 8, marginTop: 10 },
  metric: { flex: 1, backgroundColor: "#1b2330", borderRadius: 8, padding: 8, minHeight: 54 },
  metricLabel: { color: "#8b98a9", fontSize: 11 },
  metricValue: { color: "#e6edf3", fontSize: 14, fontWeight: "700", marginTop: 4 },
  good: { color: "#3fb950" },
  segment: { flexDirection: "row", backgroundColor: "#1b2330", borderRadius: 8, padding: 3, marginBottom: 4 },
  segmentButton: { flex: 1, paddingVertical: 9, alignItems: "center", borderRadius: 7 },
  segmentActive: { backgroundColor: "#4cc2ff" },
  segmentText: { color: "#8b98a9", fontWeight: "700" },
  segmentTextActive: { color: "#06202e" },
  sectionTitle: { color: "#e6edf3", fontSize: 15, fontWeight: "700", marginBottom: 8 },
  input: { borderColor: "#2a3445", borderWidth: 1, borderRadius: 8, backgroundColor: "#1b2330", color: "#e6edf3", padding: 11, fontSize: 13, marginTop: 10 },
  paramRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 10 },
  paramLabel: { color: "#8b98a9", fontSize: 13, flex: 1, marginRight: 8 },
  stepper: { backgroundColor: "#1b2330", borderColor: "#2a3445", borderWidth: 1, borderRadius: 8, width: 40, alignItems: "center", paddingVertical: 6 },
  stepperText: { color: "#e6edf3", fontSize: 16, fontWeight: "700" },
  gaitRow: { flexDirection: "row", alignItems: "center", paddingVertical: 4, borderBottomWidth: 1, borderBottomColor: "#1b2330" },
  gaitLabel: { flex: 2.2, color: "#8b98a9", fontSize: 12.5 },
  gaitCell: { flex: 1, fontSize: 13, fontWeight: "700", textAlign: "right" },
  gaitHeader: { flex: 1, fontSize: 11, fontWeight: "700", textAlign: "right", color: "#8b98a9" },
});
