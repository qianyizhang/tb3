import geometry from '../../task-explorer/resect/geometry.json?raw';
import reference from '../../task-explorer/resect/reference.json?raw';
import helpers from '../../task-explorer/resect/helpers.json?raw';
import type { StoryState } from './story-timeline';
export type ResectState = Extract<StoryState, { recipe: 'resect-correspondence-v1' }>;
export type ResectPlane = {
  name: string;
  width: number;
  height: number;
  png: string;
  origin_world_mm: number[];
  dx_world_mm: number[];
  dy_world_mm: number[];
  coverage_fraction: number;
};
type Modality = {
  shape: number[];
  spacing_mm: number[];
  affine: number[][];
  initial_voxel: number[];
  window: number[];
  native: ResectPlane[];
  ras: ResectPlane[];
  sweep: ResectPlane[];
};
export const resect = (
  JSON.parse(geometry) as {
    cases: { id: string; query_world_mm: number[]; modalities: Record<'mri' | 'us', Modality> }[];
  }
).cases;
export const resectCase = resect[1];
export const resectReference = (
  JSON.parse(reference) as {
    cases: {
      id: string;
      selected_index_zero_based: number;
      target_world_mm: number[];
      delta_world_mm: number[];
      initial_error_mm: number;
      all_noop_errors_mm: number[];
      baseline: { mean_mm: number; median_mm: number; max_mm: number };
    }[];
  }
).cases;
export const resectHelpers = JSON.parse(helpers) as Record<'mri' | 'us', ResectPlane>;
export const resectColors = { query: '#efa933', initial: '#41c5b6', reference: '#e880ad' };
const dot = (a: number[], b: number[]) => a.reduce((s, v, i) => s + v * b[i], 0);
/** Gram-system projection also handles the source affine's slight nonorthogonality. */
export function resectProjection(p: ResectPlane, point: number[]) {
  const dx = p.dx_world_mm,
    dy = p.dy_world_mm,
    d = point.map((v, i) => v - p.origin_world_mm[i]);
  const aa = dot(dx, dx),
    bb = dot(dy, dy),
    ab = dot(dx, dy),
    ad = dot(dx, d),
    bd = dot(dy, d),
    det = aa * bb - ab * ab;
  const u = (ad * bb - bd * ab) / det,
    v = (bd * aa - ad * ab) / det;
  const normal = [
    dx[1] * dy[2] - dx[2] * dy[1],
    dx[2] * dy[0] - dx[0] * dy[2],
    dx[0] * dy[1] - dx[1] * dy[0],
  ];
  return { u, v, normal_mm: dot(d, normal) / Math.hypot(...normal) };
}
export const resectSweepIndex = (scan: number) => Math.round(12 * Math.max(0, Math.min(1, scan)));
export const resectReveal = (state: ResectState) => state.reference > 0.5;
export function resectTeachingOutput(state: ResectState) {
  return state.output > 0.5
    ? {
        us_voxel_ijk: resectCase.modalities.us.initial_voxel,
        confidence: 0,
        evidence: 'Unchanged teaching control; no anatomical claim.',
      }
    : null;
}
