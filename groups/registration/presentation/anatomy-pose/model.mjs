export const REFERENCE = [0, 0, 88, 12, -10, 18];
export const INITIAL = [12, -8, 98, 0, 8, -8];
export const GRID = Array.from({ length: 49 }, (_, i) => [
  ((i % 7) * 80) / 6,
  (Math.floor(i / 7) * 80) / 6,
  0,
]);

export function rotation(pose) {
  const [a, b, c] = pose.slice(3).map((x) => (x * Math.PI) / 180);
  const ca = Math.cos(a),
    sa = Math.sin(a),
    cb = Math.cos(b),
    sb = Math.sin(b),
    cc = Math.cos(c),
    sc = Math.sin(c);
  return [
    [cc * cb, cc * sb * sa - sc * ca, cc * sb * ca + sc * sa],
    [sc * cb, sc * sb * sa + cc * ca, sc * sb * ca - cc * sa],
    [-sb, cb * sa, cb * ca],
  ];
}

export function point(pose, local) {
  return rotation(pose).map((row, i) => pose[i] + row.reduce((s, v, j) => s + v * local[j], 0));
}

export function transform(pose) {
  const r = rotation(pose),
    origin = point(pose, [-40, -40, 0]);
  return [...r.map((row, i) => [...row, origin[i]]), [0, 0, 0, 1]];
}

export function inPlaneTurn(degrees) {
  const r = rotation(REFERENCE),
    angle = (degrees * Math.PI) / 180;
  const c = Math.cos(angle),
    s = Math.sin(angle);
  const m = r.map((row) => [row[0] * c + row[1] * s, -row[0] * s + row[1] * c, row[2]]);
  return [
    ...REFERENCE.slice(0, 3),
    ...[Math.atan2(m[2][1], m[2][2]), Math.asin(-m[2][0]), Math.atan2(m[1][0], m[0][0])].map(
      (x) => (x * 180) / Math.PI,
    ),
  ];
}

export function metrics(pose) {
  const distances = GRID.map(([u, v]) => {
    const a = point(pose, [u - 40, v - 40, 0]),
      b = point(REFERENCE, [u - 40, v - 40, 0]);
    return Math.hypot(...a.map((x, i) => x - b[i]));
  });
  const r = rotation(pose),
    ref = rotation(REFERENCE);
  const dot = r.reduce((s, row, i) => s + row[2] * ref[i][2], 0);
  const rms = Math.sqrt(distances.reduce((s, d) => s + d * d, 0) / distances.length);
  const max = Math.max(...distances);
  return {
    rms,
    max,
    centre: Math.hypot(...pose.slice(0, 3).map((x, i) => x - REFERENCE[i])),
    normal: (Math.acos(Math.min(1, Math.max(-1, dot))) * 180) / Math.PI,
    pass: rms <= 3 && max <= 5,
  };
}
