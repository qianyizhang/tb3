import sourceRaw from '../../task-explorer/ct-organ/source.json?raw';
import outputRaw from '../../task-explorer/ct-organ/output.json?raw';
import referenceRaw from '../../task-explorer/ct-organ/reference.json?raw';
import type { StoryState } from './story-timeline';

export type CtOrganState = Extract<StoryState, { recipe: 'ct-organ-v1' }>;
export type CtPaths = number[][][];
export type CtPlane = {
  png: string;
  width: number;
  height: number;
  index: number;
  horizontal: string;
  vertical: string;
  bounds_ij?: number[][];
};
export type CtMethod = {
  k: number;
  polygon_explicit: boolean;
  box_explicit: boolean;
  polygon_points: number[][];
  raw_polygon: CtPaths;
  box: number[];
  native_image_box_xyxy: number[];
  tool_candidate: CtPaths;
  baseline_final: CtPaths;
  tool_final: CtPaths;
};
export const ctOrganSource = JSON.parse(sourceRaw) as {
  shape: number[];
  affine: number[][];
  spacing_mm: number[];
  labels: { id: number; name: string; file: string; convention: string }[];
  views: Record<string, CtPlane>;
};
export const ctOrganOutputs = JSON.parse(outputRaw) as {
  masks: Record<string, Record<'medium' | 'tool', CtPaths>>;
  methods: CtMethod[];
};
type Metric = {
  semantic_macro_dice: number;
  matched_macro_dice: number;
  identity_correct_matches: number;
  identity_assessable_matches: number;
  per_label: { id: number; name: string; dice: number }[];
};
export const ctOrganReference = JSON.parse(referenceRaw) as {
  masks: Record<string, CtPaths>;
  metrics: Record<'xhigh' | 'medium' | 'sol' | 'tool', Metric>;
  overlap_voxels: number;
  matched_macro: Record<string, { n: number; baseline: number; tool: number }>;
};
export const ctOrganColors = {
  medium: '#fb923c',
  tool: '#32d8e2',
  reference: '#9beb72',
  method: '#d197ff',
};
const pick = <T>(rows: T[], value: number) =>
  rows[Math.min(rows.length - 1, Math.floor(value * rows.length))];
export function ctOrganSelection(s: CtOrganState) {
  const id =
    s.scene === 'inventory'
      ? pick(ctOrganSource.labels, s.view).id
      : s.scene === 'regressions'
        ? pick([4, 7, 8], s.view)
        : 6;
  return {
    id,
    label: ctOrganSource.labels[id - 1],
    reveal: s.reference > 0.5,
    output: s.output > 0.5,
    method: pick(ctOrganOutputs.methods, s.view),
    plane: ctOrganSource.views[String(id)],
  };
}
export const ctPath = (paths: CtPaths) =>
  paths.map((p) => p.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join('') + 'Z').join('');
