import baseline from '../../task-explorer/localized-ct/baseline.json?raw';
import followup from '../../task-explorer/localized-ct/followup.json?raw';
import output from '../../task-explorer/localized-ct/output.json?raw';
import reference from '../../task-explorer/localized-ct/reference.json?raw';
import type { StoryState } from './story-timeline';

export type LocalizedCtState = Extract<StoryState, { recipe: 'localized-ct-v1' }>;
export type LocalizedVisit = 'baseline' | 'followup';
export interface LocalizedPlane {
  axis: number;
  index: number;
  bounds: number[];
  u_axis: number;
  v_axis: number;
  flip_v: boolean;
  width: number;
  height: number;
  extent_mm: number[];
  png: string;
  selection: string;
  window: number[];
}
interface Visit {
  candidate: string;
  visit: LocalizedVisit;
  native_ijk: number[];
  shape: number[];
  spacing_mm: number[];
  axes: string[];
  views: Record<string, LocalizedPlane>;
}
export const localizedVisits = {
  baseline: JSON.parse(baseline),
  followup: JSON.parse(followup),
} as Record<LocalizedVisit, Visit>;
export const localizedOutput = JSON.parse(output) as {
  judgments: { candidates: { candidate_id: string; judgment: string; reason: string }[] };
  events: { schema_version: number; groups: unknown[] };
};
export const localizedReference = JSON.parse(reference) as {
  views: Record<string, { paths: number[][][]; pixels: number }>;
  geometry: { volume_ml: number; reference_voxels: number }[];
  controls: Record<string, { valid: boolean; acceptance?: number; detected: number }>;
};
export function localizedIndex(value: number, count: number): number {
  return Math.min(count - 1, Math.max(0, Math.floor(value * count)));
}
export function localizedSelection(s: LocalizedCtState) {
  const n = localizedIndex(s.view, 6);
  return {
    axial: localizedIndex(s.view, 4),
    serial: localizedIndex(s.view, 12),
    orthogonal: `${n < 3 ? 'i' : 'j'}-${n % 3}`,
    output: s.output > 0.5,
    reference: s.reference > 0.5,
  };
}
export function localizedPixel(p: LocalizedPlane, point: number[], spacing: number[]) {
  return {
    x: point[p.u_axis] - p.bounds[2 * p.u_axis] + 0.5,
    y: p.flip_v
      ? p.bounds[2 * p.v_axis + 1] - point[p.v_axis] - 0.5
      : point[p.v_axis] - p.bounds[2 * p.v_axis] + 0.5,
    offset: (p.index - point[p.axis]) * spacing[p.axis],
  };
}
export function localizedPath(paths: number[][][]) {
  return paths
    .map((p) => p.map(([x, y], i) => `${i ? 'L' : 'M'}${x},${y}`).join(' ') + 'Z')
    .join(' ');
}
