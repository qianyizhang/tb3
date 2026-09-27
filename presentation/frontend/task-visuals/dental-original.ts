import sourceRaw from '../../task-explorer/dental-original/source.json?raw';
import outputRaw from '../../task-explorer/dental-original/output.json?raw';
import referenceRaw from '../../task-explorer/dental-original/reference.json?raw';
import type { StoryState } from './story-timeline';

export type DentalState = Extract<StoryState, { recipe: 'dental-original-v1' }>;
export type DentalPaths = number[][][];
export type DentalItem = {
  id: number | string;
  paths: DentalPaths;
  center: number[];
  pixels: number;
};
export type DentalPlane = {
  case: string;
  axis: string;
  index: number;
  plane_axes: string[];
  bounds_uv: number[][];
  width: number;
  height: number;
  png: string;
  selection: string;
};
export const dentalSource = JSON.parse(sourceRaw) as {
  views: Record<string, DentalPlane>;
  labels: Record<string, string>;
};
export const dentalOutputs = JSON.parse(outputRaw) as {
  views: Record<string, Record<string, DentalItem[]>> & {
    'pulp-gates': Record<string, DentalPaths>;
  };
  gate_description: { reference_pulp_voxels: number; overlap_counts: Record<string, number> };
};
export const dentalReference = JSON.parse(referenceRaw) as {
  views: Record<string, DentalItem[]> & { 'pulp-gates': DentalPaths };
  diagnostics: {
    name: string;
    original_macro: number;
    fixed_lr_diagnostic_macro: number;
    foreground_dice: number;
    active_labels_original: number;
    active_labels_lr_diagnostic: number;
    per_label: {
      id: number;
      gt_voxels: number;
      pred_voxels: number;
      original_dice: number | null;
      lr_diagnostic_dice: number | null;
    }[];
  }[];
  pulp_gates: Record<string, number>;
};
export const dentalColors = {
  medium: '#fb923c',
  output: '#32d8e2',
  reference: '#9beb72',
  gate: '#d197ff',
};
export const dentalGates = ['envelope', 'distance', 'intensity', 'slice', 'final'] as const;
export function dentalSwapId(id: number | string): number | string {
  if (typeof id !== 'number') return id;
  if ([3, 5, 103].includes(id)) return id + 1;
  if ([4, 6, 104].includes(id)) return id - 1;
  const base = id >= 111 ? id - 100 : id;
  const quadrant = Math.floor(base / 10),
    position = base % 10;
  if (quadrant >= 1 && quadrant <= 4 && position >= 1 && position <= 8)
    return id + ([1, 3].includes(quadrant) ? 10 : -10);
  return id;
}
export function dentalDisplayedItems(items: DentalItem[], diagnostic: boolean) {
  return diagnostic ? items.map((item) => ({ ...item, id: dentalSwapId(item.id) })) : items;
}
export function dentalSelection(s: DentalState) {
  const key =
    s.scene === 'canals'
      ? s.view < 0.5
        ? 'canals-145'
        : 'canals-205'
      : s.scene === 'restorations'
        ? 'restorations'
        : s.scene === 'pulp'
          ? 'pulp-gates'
          : s.scene === 'omissions'
            ? 'omitted-canals'
            : ['output', 'reference', 'diagnostic'].includes(s.scene)
              ? 'identity'
              : s.scene === 'limits'
                ? 'input-f002'
                : 'input-f018';
  return {
    key,
    plane: dentalSource.views[key],
    reveal: s.reference > 0.5,
    output: s.output > 0.5,
    diagnostic: s.diagnostic > 0.5,
    gate: dentalGates[Math.min(4, Math.floor(s.gate * 5))],
  };
}
export const dentalPath = (paths: DentalPaths) =>
  paths.map((p) => p.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join('') + 'Z').join('');
