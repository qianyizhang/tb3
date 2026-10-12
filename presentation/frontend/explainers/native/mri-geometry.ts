/** Each visit supplies its own affine; no registration or index correspondence is implied. */
export function rasPoint(affine: number[][], point: number[]): number[] {
  return affine
    .slice(0, 3)
    .map(
      (row) => row[3] + row.slice(0, 3).reduce((sum, value, axis) => sum + value * point[axis], 0),
    );
}
export function nearestSample(indices: number[], native: number): number {
  let best = 0;
  indices.forEach((value, i) => {
    if (Math.abs(value - native) < Math.abs(indices[best] - native)) best = i;
  });
  return best;
}
export function bboxCells(minimum: number[], inclusiveMaximum: number[]): number[][] {
  return [minimum.slice(), inclusiveMaximum.map((v) => v + 1)];
}
export function cellSpans(bounds: number[][], spacing: number[]): number[] {
  return spacing.map((s, a) => (bounds[1][a] - bounds[0][a]) * s);
}
export function boxEdges(bounds: number[][]): number[][] {
  const corners = Array.from({ length: 8 }, (_, i) =>
    [0, 1, 2].map((a) => bounds[(i >> a) & 1][a] - 0.5),
  );
  return corners.flatMap((p, i) =>
    [1, 2, 4].flatMap((bit) => (i & bit ? [] : [p, corners[i | bit]])),
  );
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
