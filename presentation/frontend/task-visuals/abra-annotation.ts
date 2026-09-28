import inputs from '../../task-explorer/abra-annotation/inputs.json?raw';
import reference from '../../task-explorer/abra-annotation/reference.json?raw';
import type { StoryState } from './story-timeline';
export type AbraState = Extract<StoryState, { recipe: 'abra-annotation-v1' }>;
export const abraInputs = JSON.parse(inputs) as {
  case: string;
  shape: number[];
  spacing_mm: number[];
  slice_step_mm: number;
  orientation_lps: number[];
  series_uid: string;
  study_uid: string;
  target_k: number;
  full: { k: number; png: string; origin_lps_mm: number[] }[];
};
export const abraReference = JSON.parse(reference) as {
  crop_bounds: number[];
  crops: { k: number; png: string }[];
  frames: { k: number; pixels: number; z_lps_mm: number; polygon: number[][] }[];
  ordinary: {
    id: string;
    max_turns: number;
    initial_slice_index: number;
    expected_outcome: { slice_index: number; reference_polygon: number[][] };
  };
  oracle: {
    id: string;
    max_turns: number;
    oracle_data: {
      overview: {
        findings: {
          label: string;
          slice_range: number[];
          representative_slice: number;
          confidence: number;
        }[];
      };
      slices: Record<string, { points: number[][]; confidence: number }[]>;
    };
  };
  scorer_arithmetic: {
    delta: number | null;
    penalty: number;
    reference_copy_polygon_score: number;
  }[];
};
export const abraNavigation = [0, 64, 66] as const;
export function abraSelection(s: AbraState) {
  return {
    k:
      s.scene === 'inputs'
        ? 0
        : s.scene === 'navigate'
          ? abraNavigation[Math.min(2, Math.floor(s.view * 3))]
          : 66,
    field: Math.min(5, Math.floor(s.view * 6)),
    frame: Math.min(
      7,
      Math.max(0, Math.floor((s.scene === 'reference' ? (s.view - 0.5) * 2 : s.view) * 8)),
    ),
    reference: s.reference > 0.5,
    helper: s.helper > 0.25,
    output: s.output > 0.75,
  };
}
/** Pixel coordinates name voxel centers; SVG image extents start at the outer corner. */
export function abraPixel(point: readonly number[], crop = false) {
  return [
    point[0] + 0.5 - (crop ? abraReference.crop_bounds[0] : 0),
    point[1] + 0.5 - (crop ? abraReference.crop_bounds[1] : 0),
  ];
}
export function abraLps(point: readonly number[], k: number) {
  const o = abraInputs.full.find((v) => v.k === k)!.origin_lps_mm,
    d = abraInputs.orientation_lps,
    sp = abraInputs.spacing_mm;
  return o.map((x, j) => x + point[0] * sp[1] * d[j] + point[1] * sp[0] * d[j + 3]);
}
