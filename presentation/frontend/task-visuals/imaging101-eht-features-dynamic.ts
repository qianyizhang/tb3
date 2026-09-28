import inputJson from '../../task-explorer/imaging101-eht-features-dynamic/inputs.json?raw';
import dataJson from '../../task-explorer/imaging101-eht-features-dynamic/contract.json?raw';
import referenceJson from '../../task-explorer/imaging101-eht-features-dynamic/reference.json?raw';
import type { StoryState } from './story-timeline';
export type EhtFeaturesState = Extract<
  StoryState,
  { recipe: 'imaging101-eht-features-dynamic-v1' }
>;
export type FeaturesImage = {
  data: string;
  shape: [number, number];
  range: [number, number];
  palette: 'heat' | 'error';
  unit: string;
};
export const featuresInput = JSON.parse(inputJson) as {
  times_hours: number[];
  station_names: string[];
  frames: {
    uv_Glambda: [number, number][];
    vis_real_Jy: number[];
    vis_imaginary_Jy: number[];
    station_pairs: [number, number][];
  }[];
  closure_controls: {
    kind: 'phase' | 'amplitude';
    epoch: number;
    stations: number[];
    pairs: [number, number][];
    signs: number[];
    before: number[];
    after: number[];
    combined_before: number;
    combined_after: number;
    baseline_indices: number[];
  }[];
  model_controls: {
    label: string;
    unit: string;
    values: number[];
    parameters: number[][];
    images: FeaturesImage[];
  }[];
  closure_counts: number[];
  closure_ranks: number[];
};
export const featuresData = JSON.parse(dataJson) as {
  images: FeaturesImage[];
  histograms: {
    edges: number[];
    centers: number[];
    mass: number[][];
    bin_width: number;
    range: [number, number];
  }[];
  means: number[][];
  stds: number[][];
  intervals: number[][][];
  ess: number[];
  max_weight: number[];
  samples_per_frame: number;
  likelihood_ratio: number;
  parameter_labels: string[];
  parameter_units: string[];
};
export const featuresReference = JSON.parse(referenceJson) as {
  truth: FeaturesImage[];
  error: FeaturesImage[];
  parameters: number[][];
  biases: number[][];
  native: { avg_abs_bias: number[]; avg_std: number[] };
  generic: { ncc: number; nrmse: number; passed: null };
  oracle_point: { avg_abs_bias: number[]; stds: number[][] };
  angle_wrap: {
    fixed_angles_deg: number[];
    source_linear_mean_deg: number;
    circular_mean_deg: number;
  };
};
export const featuresIndex = (s: EhtFeaturesState, count = 10) =>
  Math.min(count - 1, Math.max(0, Math.floor(s.view * count)));
export const featuresReveal = (s: EhtFeaturesState) =>
  ['reference', 'diagnostics', 'scoring'].includes(s.scene) && s.reference > 0.5;
export const featuresReferenceIndex = (s: EhtFeaturesState) =>
  Math.min(9, Math.max(0, Math.floor((s.view - 0.5) * 20)));
