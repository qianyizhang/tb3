/** Native voxel indices remain authoritative; scene permutation is display-only. */
export function rasPoint(affine: number[][], point: number[]): number[] {
  return affine.slice(0, 3).map((r) => r[3] + r[0] * point[0] + r[1] * point[1] + r[2] * point[2]);
}
export function nearestSample(indices: number[], native: number): number {
  let best = 0;
  for (let i = 1; i < indices.length; i++)
    if (Math.abs(indices[i] - native) < Math.abs(indices[best] - native)) best = i;
  return best;
}
export function insideCrop(point: number[], shape: number[]): boolean {
  return point.every((v, a) => v >= -0.5 && v <= shape[a] - 0.5);
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
  const corners = Array.from({ length: 8 }, (_, i) =>
    [0, 1, 2].map((a) => bounds[(i >> a) & 1][a]),
  );
  return corners.flatMap((p, i) =>
    [1, 2, 4].flatMap((bit) => (i & bit ? [] : [p, corners[i | bit]])),
  );
}
