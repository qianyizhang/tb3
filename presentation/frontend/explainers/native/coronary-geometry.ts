export function rasPoint(affine: number[][], point: number[]): number[] {
  return affine
    .slice(0, 3)
    .map((row) => row[3] + row[0] * point[0] + row[1] * point[1] + row[2] * point[2]);
}
/** Invert the supplied 3×3 basis, preserving non-diagonal affines as well. */
export function nativePoint(affine: number[][], ras: number[]): number[] {
  const [a, b, c] = affine[0],
    [d, e, f] = affine[1],
    [g, h, i] = affine[2];
  const det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
  if (Math.abs(det) < 1e-12) throw Error('Singular native affine');
  const p = ras.map((v, n) => v - affine[n][3]);
  return [
    ((e * i - f * h) * p[0] + (c * h - b * i) * p[1] + (b * f - c * e) * p[2]) / det,
    ((f * g - d * i) * p[0] + (a * i - c * g) * p[1] + (c * d - a * f) * p[2]) / det,
    ((d * h - e * g) * p[0] + (b * g - a * h) * p[1] + (a * e - b * d) * p[2]) / det,
  ];
}
export function fromFlat(flat: number, shape: number[]): number[] {
  return [
    Math.floor(flat / (shape[1] * shape[2])),
    Math.floor(flat / shape[2]) % shape[1],
    flat % shape[2],
  ];
}
export function nearestSample(indices: number[], native: number): number {
  let best = 0;
  indices.forEach((v, n) => {
    if (Math.abs(v - native) < Math.abs(indices[best] - native)) best = n;
  });
  return best;
}
export function inCrop(point: number[], shape: number[]): boolean {
  return point.every((v, n) => v >= -0.5 && v <= shape[n] - 0.5);
}
export function cprPixelIndex(
  shape: number[],
  angle: number,
  column: number,
  offset: number,
): number {
  if (![angle, column, offset].every((v, a) => Number.isInteger(v) && v >= 0 && v < shape[a]))
    throw Error('CPR pixel outside retained buffer');
  return (angle * shape[1] + column) * shape[2] + offset;
}
export function cumulativeArc(points: number[][]): number[] {
  let distance = 0;
  return points.map((p, n) => {
    if (n) distance += Math.hypot(...p.map((v, a) => v - points[n - 1][a]));
    return distance;
  });
}
export function planeCorners(axis: number, position: number, shape: number[]): number[][] {
  const other = [0, 1, 2].filter((a) => a !== axis);
  return [
    [0, 1],
    [1, 1],
    [1, 0],
    [0, 0],
  ].map(([u, v]) => {
    const p = [0, 0, 0];
    p[axis] = position;
    p[other[0]] = u ? shape[other[0]] - 0.5 : -0.5;
    p[other[1]] = v ? shape[other[1]] - 0.5 : -0.5;
    return p;
  });
}
export function boxEdges(bounds: number[][]): number[][] {
  const corners = Array.from({ length: 8 }, (_, n) =>
    [0, 1, 2].map((a) => bounds[(n >> a) & 1][a] - 0.5),
  );
  return corners.flatMap((p, n) =>
    [1, 2, 4].flatMap((bit) => (n & bit ? [] : [p, corners[n | bit]])),
  );
}
/** Exact binary-region boundary; never substitutes the supplied membership with a sphere. */
export function boundaryIndices(indices: number[], shape: number[]): number[] {
  const set = new Set(indices),
    strides = [shape[1] * shape[2], shape[2], 1];
  return indices.filter((flat) => {
    const p = fromFlat(flat, shape);
    return strides.some(
      (stride, a) =>
        p[a] === 0 || p[a] === shape[a] - 1 || !set.has(flat - stride) || !set.has(flat + stride),
    );
  });
}
