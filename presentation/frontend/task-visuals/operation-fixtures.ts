/** Retained fixture bytes: Python owns hash/role checks before portable bundling. */
import rawGraph from '../../assets/teaching-fixtures/topology-v1/fixture.json?raw';
import rawRigid from '../../assets/teaching-fixtures/correspondence-v1/fixture.json?raw';
import rawScale from '../../assets/teaching-fixtures/multiscale-v1/fixture.json?raw';
export interface IndexedMesh {
  vertices: readonly (readonly number[])[];
  faces: readonly (readonly number[])[];
  normals?: readonly (readonly number[])[];
}
export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  points: number[][];
  length_m: number;
}
interface Graph {
  nodes: Record<string, number[]>;
  edges: GraphEdge[];
  selected_edges: string[];
  selected_target: string;
}
interface Rigid {
  geometry: { moving: IndexedMesh; fixed: IndexedMesh };
  moving_points: number[][];
  fixed_points: number[][];
  deformed_points: number[][];
  fixed_from_moving: number[][];
  point_ids: string[];
  held_out_ids: string[];
  fit_ids: string[];
  target_absent_id: string;
}
interface Multiscale {
  width_level0: number;
  height_level0: number;
  patches: { id: string; origin_level0: number[]; size_level0: number[]; class_code: null }[];
  regions: { id: string; bounds_level0: number[] }[];
  objects: { id: string; center_level0: number[]; radius_level0: number; teaching_class: string }[];
  teaching_classes: string[];
  tile_origin_level0: number[];
  tile_downsample: number;
  example_local_point: number[];
  example_level0_point: number[];
}
export const graph = JSON.parse(rawGraph) as Graph;
export const rigid = JSON.parse(rawRigid) as Rigid;
export const multiscale = JSON.parse(rawScale) as Multiscale;
export function level0Point(local: readonly number[]): number[] {
  return local.map((v, i) => multiscale.tile_origin_level0[i] + multiscale.tile_downsample * v);
}
export function transformedPoint(p: readonly number[]): number[] {
  return rigid.fixed_from_moving
    .slice(0, 3)
    .map((row) => row[0] * p[0] + row[1] * p[1] + row[2] * p[2] + row[3]);
}
export function residualM(index: number): number {
  return Math.hypot(
    ...transformedPoint(rigid.moving_points[index]).map((v, i) => v - rigid.fixed_points[index][i]),
  );
}
/** A distance budget traverses connected edge samples; no straight-line shortcut. */
export function traceEdges(fraction: number) {
  const selected = graph.selected_edges.map((id) => graph.edges.find((edge) => edge.id === id)!);
  let remaining = selected.reduce((sum, edge) => sum + edge.length_m, 0) * fraction;
  return selected.map((edge) => {
    const points = [edge.points[0]];
    for (let i = 1; i < edge.points.length; i++) {
      const a = edge.points[i - 1],
        b = edge.points[i];
      const length = Math.hypot(...b.map((v, j) => v - a[j]));
      if (remaining >= length) {
        points.push(b);
        remaining -= length;
      } else {
        if (remaining > 0) points.push(a.map((v, j) => v + ((b[j] - v) * remaining) / length));
        remaining = 0;
        break;
      }
    }
    return { edge, points };
  });
}

import rawMaterial from '../../assets/teaching-fixtures/shape-material-v1/fixture.json?raw';
import rawLongitudinal from '../../assets/teaching-fixtures/longitudinal-v1/fixture.json?raw';
interface MaterialFixture {
  geometry: { initial: IndexedMesh; later: IndexedMesh };
  marker_uv: number[][];
  material_ids: string[];
}
interface VisitObject {
  id: string;
  position: number[];
  radius: number;
}
interface LongitudinalFixture {
  visits: { id: string; objects: VisitObject[]; coverage?: number[] }[];
  links: { source: string | null; target: string | null; relation: string }[];
}
export const material = JSON.parse(rawMaterial) as MaterialFixture;
export const longitudinal = JSON.parse(rawLongitudinal) as LongitudinalFixture;
export function materialPosition(u: number, v: number, t: number, alternative: number): number[] {
  const phase = 1 - 0.14 * t,
    a = (u + 0.32 * t * Math.sin(Math.PI * v) * alternative) * Math.PI * 2,
    b = 0.55 + v * (Math.PI - 0.55),
    r = Math.sin(b),
    y = (0.056 * Math.cos(b)) / phase;
  return [0.0385 * r * Math.cos(a) * phase + 0.12 * y, y, 0.0315 * r * Math.sin(a) * phase];
}
