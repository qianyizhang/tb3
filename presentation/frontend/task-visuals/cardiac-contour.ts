import sourceRaw from '../../task-explorer/cardiac-contour/source.json?raw';
import outputRaw from '../../task-explorer/cardiac-contour/output.json?raw';
import referenceRaw from '../../task-explorer/cardiac-contour/reference.json?raw';
import type { StoryState } from './story-timeline';

export type CardiacContourState = Extract<StoryState, { recipe: 'cardiac-contour-v1' }>;
export type ContourCondition = 'one' | 'four' | 'eight';
export type NativeFrame = {
  frame_1based: number;
  supplied_image: string;
  supplied_contour: string;
  additional_inputs: { plane_1based: number; image: string; contour: string }[];
  withheld_image: string;
};
export const contourSource = JSON.parse(sourceRaw) as {
  patient: string;
  shape_hw: [number, number];
  spacing_mm_per_pixel: number;
  frames: NativeFrame[];
  supplied_planes_1based: Record<ContourCondition, number[]>;
  withheld_planes_1based: number[];
};
export const contourOutput = JSON.parse(outputRaw) as {
  frames: Record<ContourCondition, string>[];
  curves_ml: Record<ContourCondition | 'two' | 'static', number[]>;
  mesh_samples_mm: Record<ContourCondition, number[][][]>;
  mesh_sample_grid: { rings: number; azimuths: number; rule: string };
  radial_samples: {
    polar_index: number[];
    positive_radius_px: number[];
    negative_radius_px: number[];
  }[];
};
type Metric = {
  input_planes_1based: number[];
  heldout_dice: { mean: number };
  heldout_hd95_mm: { mean: number };
  volume_curve_mape_vs_dense_percent: number;
  ef_error_vs_dense_reference_pp: number;
  ef_at_source_phases_percent: number;
};
export const contourReference = JSON.parse(referenceRaw) as {
  frames: { withheld_contour: string }[];
  dense_curve_ml: number[];
  stats: Record<ContourCondition | 'two' | 'dense' | 'static', Metric>;
  depth_control: {
    original_ef_percent: number;
    modified_ef_percent: number;
    difference_pp: number;
  };
  denominator: string;
};
export const contourColors = { helper: '#8398ad', output: '#18c6d4', reference: '#f4bc49' };
export function contourFrame(state: CardiacContourState) {
  return Math.max(0, Math.min(29, Math.round(state.phase * 29)));
}
export function contourCondition(state: CardiacContourState): ContourCondition {
  if (state.scene === 'inputs') return 'one';
  if (state.scene === 'depth') return 'one';
  return 'four';
}
export function contourReveal(state: CardiacContourState) {
  return state.reference > 0.5;
}
