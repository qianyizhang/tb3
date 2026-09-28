import inputJson from '../../task-explorer/imaging101-eht-dynamic/inputs.json?raw';
import dataJson from '../../task-explorer/imaging101-eht-dynamic/contract.json?raw';
import referenceJson from '../../task-explorer/imaging101-eht-dynamic/reference.json?raw';
import type { StoryState } from './story-timeline';
export type EhtDynamicState = Extract<StoryState, { recipe: 'imaging101-eht-dynamic-v1' }>;
export type DynamicImage = {
  data: string;
  shape: [number, number];
  range: [number, number];
  unit: string;
  palette: 'heat' | 'error' | 'signed';
};
export type DynamicMetric = { ncc: number; nrmse: number };
export type DynamicDiagnostic = {
  flux_Jy: number[];
  array_polar_moment_angle_deg: number[];
  array_polar_moment_net_change_deg: number;
  adjacent_difference_error_ratio: number;
};
export const dynamicInput = JSON.parse(inputJson) as {
  times_hours: number[];
  station_names: string[];
  prior: DynamicImage;
  frames: {
    uv_Glambda: [number, number][];
    vis_real_Jy: number[];
    vis_imaginary_Jy: number[];
    sigma_complex_RMS_Jy: number[];
    station_pairs: [number, number][];
  }[];
  kernels: {
    frame: number;
    baseline: number;
    station_pair: [number, number];
    uv_Glambda: [number, number];
    real: DynamicImage;
    imaginary: DynamicImage;
  }[];
};
export const dynamicData = JSON.parse(dataJson) as {
  videos: { static: DynamicImage[]; starwarps: DynamicImage[] };
  metrics: Record<
    'starwarps' | 'static_per_frame',
    { average: DynamicMetric; per_frame: DynamicMetric[] }
  >;
  diagnostics: Record<'starwarps' | 'static_per_frame', DynamicDiagnostic>;
  generic_starwarps: DynamicMetric & { passed: null };
  historical_recipe: DynamicMetric;
};
export const dynamicReference = JSON.parse(referenceJson) as {
  truth: DynamicImage[];
  error: DynamicImage[];
  diagnostics: DynamicDiagnostic;
  controls: {
    id: string;
    first: DynamicImage;
    last: DynamicImage;
    native: DynamicMetric;
    generic: DynamicMetric;
    direction_change_deg: number;
    difference_error_ratio: number;
  }[];
};
export const dynamicIndex = (s: EhtDynamicState, count = 12) =>
  Math.min(count - 1, Math.max(0, Math.floor(s.view * count)));
export const dynamicReveal = (s: EhtDynamicState) =>
  ['reference', 'diagnostics', 'scoring'].includes(s.scene) && s.reference > 0.5;
export const dynamicReferenceIndex = (s: EhtDynamicState) =>
  Math.min(11, Math.max(0, Math.floor((s.view - 0.5) * 24)));
export const dynamicControlNames = [
  'Saved StarWarps',
  'Oracle time mean',
  'Oracle reversed truth',
  'Oracle first frame',
];
