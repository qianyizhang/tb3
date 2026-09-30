import inputJson from '../../task-explorer/imaging101-eht-original/inputs.json?raw';
import contractJson from '../../task-explorer/imaging101-eht-original/contract.json?raw';
import referenceJson from '../../task-explorer/imaging101-eht-original/reference.json?raw';
import type { StoryState } from './story-timeline';
export type EhtOriginalState = Extract<StoryState, { recipe: 'imaging101-eht-original-v1' }>;
export type OriginalImage = {
  data: string;
  shape: [number, number];
  range: [number, number];
  stored_sum: number;
  unit: string;
};
export const originalInput = JSON.parse(inputJson) as {
  uv_Glambda: [number, number][];
  station_pairs: [number, number][];
  station_names: string[];
  vis_cal_abs_Jy: number[];
  vis_corrupt_abs_Jy: number[];
  observed: {
    cp_values_deg: number[];
    cp_corrupt_values_deg: number[];
    lca_values: number[];
    lca_corrupt_values: number[];
  };
  closure_controls: {
    kind: 'phase' | 'amplitude';
    source_row: number;
    baseline_indices: number[];
    pairs: [number, number][];
    stations: number[];
    signs: number[];
    before: number[];
    after: number[];
    combined_before: number;
    combined_after: number;
  }[];
};
export const originalData = JSON.parse(contractJson) as {
  names: string[];
  images: OriginalImage[];
  prior: OriginalImage;
  method_labels: string[];
};
type Score = { ncc: number; nrmse: number; passed?: null };
export const originalReference = JSON.parse(referenceJson) as {
  truth: OriginalImage;
  native: Score[];
  generic: Score[];
  zero: Score;
  physical_truth: Score;
  fallback: Score;
};
export const originalIndex = (s: EhtOriginalState, count: number) =>
  Math.min(count - 1, Math.max(0, Math.floor(s.view * count)));
export const originalReveal = (s: EhtOriginalState) =>
  ['reference', 'scoring'].includes(s.scene) && s.reference > 0.5;
export const originalReferenceIndex = (s: EhtOriginalState) =>
  Math.min(2, Math.max(0, Math.floor((s.view - 0.5) * 6)));
export const originalPairs = Array.from(
  new Set(originalInput.station_pairs.map((p) => [...p].sort((a, b) => a - b).join('-'))),
).sort();

export function originalStationOrder(c: (typeof originalInput.closure_controls)[number]): number[] {
  if (c.kind === 'phase') return c.stations;
  const top = c.pairs[0];
  const negative = c.pairs.filter((_, i) => c.signs[i] < 0);
  const partner = (station: number) => {
    const pair = negative.find((p) => p.includes(station));
    if (!pair) throw new Error('Missing closure partner');
    return pair[0] === station ? pair[1] : pair[0];
  };
  return [top[0], top[1], partner(top[0]), partner(top[1])];
}
