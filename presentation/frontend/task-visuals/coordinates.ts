import type { ScenePoint, Polygon } from './types';

export function scenePoint(value: unknown): ScenePoint {
  if (!Array.isArray(value) || value.length !== 3 || !value.every(Number.isFinite))
    throw new Error('A scene point needs three finite coordinates');
  return [value[0], value[1], value[2]];
}

export function mapPoint(
  point: ScenePoint,
  map: (value: number, axis: 0 | 1 | 2) => number,
): [number, number, number] {
  return [map(point[0], 0), map(point[1], 1), map(point[2], 2)];
}

export function polygon(points: readonly ScenePoint[]): Polygon {
  const [a, b, c, ...rest] = points;
  if (points.length < 3) throw new Error('A surface needs at least three vertices');
  return [a, b, c, ...rest];
}
