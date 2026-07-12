import React from "react";
import { View } from "react-native";
import Svg, { Line, Polygon, Text as SvgText } from "react-native-svg";
import { Mat3, matVec, Vec3 } from "../tracking/math";

type Props = {
  r: Mat3;
  label?: string;
  width?: number;
  height?: number;
  color?: string;
};

// Live attitude plate, like the web app's orientation canvas: a rectangle in
// the device frame rotated into the world frame and orthographically projected
// (screen x = world x, screen y = -world z tilted by a fixed camera pitch).
const CAM_PITCH = 0.45;

export function AttitudeView({ r, label = "device", width = 330, height = 170, color = "#4cc2ff" }: Props): React.JSX.Element {
  const WIDTH = width;
  const HEIGHT = height;
  const SCALE = Math.min(width, height * 1.9) / 6;

  function toScreen(world: Vec3): { x: number; y: number } {
    const cp = Math.cos(CAM_PITCH);
    const sp = Math.sin(CAM_PITCH);
    const v = world[2] * cp - world[1] * sp;
    return { x: WIDTH / 2 + world[0] * SCALE, y: HEIGHT / 2 - v * SCALE };
  }
  const corners: Vec3[] = [
    [-0.9, -1.3, 0],
    [0.9, -1.3, 0],
    [0.9, 1.3, 0],
    [-0.9, 1.3, 0],
  ];
  const projected = corners.map((c) => toScreen(matVec(r, c)));
  const top = toScreen(matVec(r, [0, 1.05, 0]));
  const center = toScreen(matVec(r, [0, 0, 0]));

  const axes = ([
    { v: [1.6, 0, 0] as Vec3, color: "#ff6b6b", name: "X" },
    { v: [0, 1.6, 0] as Vec3, color: "#3fb950", name: "Y" },
    { v: [0, 0, 1.6] as Vec3, color: "#4cc2ff", name: "Z" },
  ] as const).map((a) => ({ ...a, end: toScreen(a.v) }));
  const origin = toScreen([0, 0, 0]);

  return (
    <View style={{ alignItems: "center" }}>
      <Svg width={WIDTH} height={HEIGHT}>
        {axes.map((a) => (
          <Line key={a.name} x1={origin.x} y1={origin.y} x2={a.end.x} y2={a.end.y} stroke={a.color} strokeWidth="1" opacity={0.5} />
        ))}
        {axes.map((a) => (
          <SvgText key={a.name + "t"} x={a.end.x + 3} y={a.end.y} fill={a.color} fontSize="10" opacity={0.7}>
            {a.name}
          </SvgText>
        ))}
        <Polygon
          points={projected.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ")}
          fill={color}
          fillOpacity={0.75}
          stroke="#e6edf3"
          strokeOpacity={0.5}
          strokeWidth="1.5"
        />
        <Line x1={center.x} y1={center.y} x2={top.x} y2={top.y} stroke="#06202e" strokeWidth="2" />
        <SvgText x={center.x} y={center.y + 4} fill="#06202e" fontSize="11" fontWeight="bold" textAnchor="middle">
          {label}
        </SvgText>
      </Svg>
    </View>
  );
}
