import React, { useMemo, useRef, useState } from "react";
import { PanResponder, Text, TouchableOpacity, View } from "react-native";
import Svg, { Circle, Line, Polyline, Text as SvgText } from "react-native-svg";
import { PathPoint } from "../tracking/tracker";

export type PathSeries = {
  label: string;
  color: string;
  points: PathPoint[];
};

type Props = {
  series: PathSeries[];
  progress?: number; // 0..1 cursor applied to every series; undefined = all
  topView?: boolean; // walk mode: default to ground-plane view
  showFootMarkers?: boolean; // draw a marker at each series cursor (step replay)
};

type ViewPreset = "3D" | "XY" | "XZ" | "YZ";

const WIDTH = 330;
const HEIGHT = 240;

// World->screen: yaw around Z then pitch, orthographic — same feel as the web
// app's drag-to-rotate trajectory canvas.
export function PathView3D({ series, progress, topView, showFootMarkers }: Props): React.JSX.Element {
  const [preset, setPreset] = useState<ViewPreset>(topView ? "XY" : "3D");
  const [yaw, setYaw] = useState(-0.6);
  const [pitch, setPitch] = useState(0.5);
  const dragStart = useRef({ yaw: -0.6, pitch: 0.5 });

  const angles = useRef({ yaw, pitch });
  angles.current = { yaw, pitch };
  const pan = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dx) + Math.abs(g.dy) > 4,
      onPanResponderGrant: () => {
        dragStart.current = { ...angles.current };
      },
      onPanResponderMove: (_, g) => {
        setPreset("3D");
        setYaw(dragStart.current.yaw + g.dx * 0.012);
        setPitch(Math.max(-1.5, Math.min(1.5, dragStart.current.pitch + g.dy * 0.012)));
      },
    }),
  );

  const shownSeries = useMemo(() => {
    return series.map((s) => {
      const count = progress == null ? s.points.length : Math.max(1, Math.floor(s.points.length * progress));
      return { ...s, points: s.points.slice(0, count) };
    });
  }, [series, progress]);

  const { rendered, axis } = useMemo(() => {
    let projector: (p: PathPoint) => { u: number; v: number };
    if (preset === "XY") projector = (p) => ({ u: p.x, v: p.y });
    else if (preset === "XZ") projector = (p) => ({ u: p.x, v: p.z });
    else if (preset === "YZ") projector = (p) => ({ u: p.y, v: p.z });
    else {
      const cy = Math.cos(yaw), sy = Math.sin(yaw);
      const cp = Math.cos(pitch), sp = Math.sin(pitch);
      projector = (p) => {
        const x1 = p.x * cy - p.y * sy;
        const y1 = p.x * sy + p.y * cy;
        return { u: x1, v: p.z * cp - y1 * sp };
      };
    }

    let minU = -0.15, maxU = 0.15, minV = -0.15, maxV = 0.15;
    const uvSeries = shownSeries.map((s) => s.points.map(projector));
    for (const uv of uvSeries) {
      for (const q of uv) {
        minU = Math.min(minU, q.u);
        maxU = Math.max(maxU, q.u);
        minV = Math.min(minV, q.v);
        maxV = Math.max(maxV, q.v);
      }
    }
    const span = Math.max(maxU - minU, maxV - minV, 0.2);
    const pad = 20;
    const scale = (Math.min(WIDTH, HEIGHT) - pad * 2) / span;
    const cx = (minU + maxU) / 2;
    const cyv = (minV + maxV) / 2;
    const toScreen = (q: { u: number; v: number }) => ({
      x: WIDTH / 2 + (q.u - cx) * scale,
      y: HEIGHT / 2 - (q.v - cyv) * scale,
    });

    const renderedSeries = shownSeries.map((s, i) => ({
      label: s.label,
      color: s.color,
      mapped: uvSeries[i].map(toScreen),
    }));

    const axisLen = 0.06 * span;
    const axes = ([
      { p: { x: axisLen, y: 0, z: 0 }, color: "#ff6b6b", label: "X" },
      { p: { x: 0, y: axisLen, z: 0 }, color: "#3fb950", label: "Y" },
      { p: { x: 0, y: 0, z: axisLen }, color: "#4cc2ff", label: "Z" },
    ] as const).map((a) => {
      const end = toScreen(projector(a.p));
      const origin = toScreen(projector({ x: 0, y: 0, z: 0 }));
      return { ...a, origin, end };
    });

    return { rendered: renderedSeries, axis: axes };
  }, [shownSeries, preset, yaw, pitch]);

  const hasAnyPath = rendered.some((s) => s.mapped.length > 1);

  return (
    <View>
      <View style={{ flexDirection: "row", gap: 6, marginBottom: 6, alignItems: "center" }}>
        {(["3D", "XY", "XZ", "YZ"] as ViewPreset[]).map((v) => (
          <TouchableOpacity
            key={v}
            onPress={() => setPreset(v)}
            style={{
              paddingVertical: 4,
              paddingHorizontal: 12,
              borderRadius: 6,
              backgroundColor: preset === v ? "#4cc2ff" : "#1b2330",
              borderWidth: 1,
              borderColor: preset === v ? "#4cc2ff" : "#2a3445",
            }}
          >
            <Text style={{ color: preset === v ? "#06202e" : "#8b98a9", fontSize: 12, fontWeight: "700" }}>{v}</Text>
          </TouchableOpacity>
        ))}
        <View style={{ flexDirection: "row", gap: 8, marginLeft: "auto" }}>
          {series.length > 1
            ? series.map((s) => (
                <Text key={s.label} style={{ color: s.color, fontSize: 11, fontWeight: "700" }}>
                  ● {s.label}
                </Text>
              ))
            : null}
        </View>
      </View>
      <View {...pan.current.panHandlers} style={{ alignItems: "center" }}>
        <Svg width={WIDTH} height={HEIGHT}>
          {axis.map((a) => (
            <Line key={a.label} x1={a.origin.x} y1={a.origin.y} x2={a.end.x} y2={a.end.y} stroke={a.color} strokeWidth="1.5" />
          ))}
          {axis.map((a) => (
            <SvgText key={a.label + "t"} x={a.end.x + 4} y={a.end.y} fill={a.color} fontSize="10">
              {a.label}
            </SvgText>
          ))}
          {hasAnyPath ? (
            rendered.map((s) =>
              s.mapped.length > 1 ? (
                <Polyline
                  key={s.label}
                  points={s.mapped.map((m) => `${m.x.toFixed(1)},${m.y.toFixed(1)}`).join(" ")}
                  fill="none"
                  stroke={s.color}
                  strokeWidth="2.5"
                  strokeOpacity={0.9}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              ) : null,
            )
          ) : (
            <SvgText x={WIDTH / 2} y={HEIGHT / 2} fill="#8b98a9" fontSize="13" textAnchor="middle">
              Path appears after motion
            </SvgText>
          )}
          {rendered.map((s) => {
            const start = s.mapped[0];
            return start && s.mapped.length > 1 ? <Circle key={s.label + "s"} cx={start.x} cy={start.y} r="4" fill="#3fb950" /> : null;
          })}
          {rendered.map((s) => {
            const end = s.mapped[s.mapped.length - 1];
            if (!end || s.mapped.length <= 1) return null;
            return showFootMarkers ? (
              <Circle key={s.label + "f"} cx={end.x} cy={end.y} r="7" fill={s.color} stroke="#e6edf3" strokeWidth="1.5" />
            ) : (
              <Circle key={s.label + "e"} cx={end.x} cy={end.y} r="4" fill="#e6edf3" />
            );
          })}
        </Svg>
      </View>
    </View>
  );
}
