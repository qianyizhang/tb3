import inputJson from '../../task-explorer/imaging101-dti/inputs.json?raw';
import contractJson from '../../task-explorer/imaging101-dti/contract.json?raw';
import referenceJson from '../../task-explorer/imaging101-dti/reference.json?raw';
import type { StoryState } from './story-timeline';
export type DtiState = Extract<StoryState, { recipe: 'imaging101-dti-v1' }>;
export type DtiImage = {
  data: string;
  shape: [number, number];
  range: [number, number];
  unit: string;
  masked: boolean;
};
export type DtiMetric = { ncc: number; nrmse: number };
export type DtiTensor = {
  elements: number[];
  matrix: number[][];
  eigenvalues: number[];
  eigenvectors: number[][];
  fa: number;
  md: number;
  projections: { axes: number[]; points: number[][] }[];
  principal_axis_unique: boolean;
};
export const dtiInput = JSON.parse(inputJson) as {
  signals: { volume: number; bvalue: number; gradient: number[]; image: DtiImage }[];
  mask: DtiImage;
  mask_pixels: number;
  gradients: { bvals: number[]; bvecs: number[][]; design_matrix: number[][]; rank: number };
  probes: { row: number; column: number; signal: number[] }[];
};
export const dtiData = JSON.parse(contractJson) as {
  maps: Record<'fa' | 'md', Record<'ols' | 'wls', DtiImage>>;
  tensor_probes: Record<'ols' | 'wls', DtiTensor[]>;
  fixed_pixel_fits: Record<
    'ols' | 'wls',
    { tensor_elements: number[][]; fitted_s0: number[]; predicted_signal: number[][] }
  >;
  wls_weights: number[][];
  native_metrics: Record<'ols' | 'wls', Record<'fa' | 'md', DtiMetric>>;
  custom_scoring: Record<string, DtiMetric>;
  generic_scoring: Record<string, DtiMetric & { selected_reference_keys: string[] }>;
  fallback: { result: { error: string }; runner_commands_executed: number };
  staging: Record<string, string[]>;
  notebook_probe_check: {
    source_label: string;
    row: number;
    column: number;
    in_tissue_mask: boolean;
    fa: number;
    md: number;
  }[];
  orientation_controls: {
    source_label: string;
    declared_direction: number[];
    principal_axis_unique: boolean;
    actual_principal_axis_absolute: number[] | null;
    matching_voxels: number;
  }[];
  thresholds_available: boolean;
};
export const dtiReference = JSON.parse(referenceJson) as {
  maps: Record<'fa' | 'md', DtiImage>;
  errors: Record<'fa' | 'md', Record<'ols' | 'wls', DtiImage>>;
  tensor_probes: DtiTensor[];
  solver_visible_all_levels: boolean;
};
export const dtiIndex = (s: DtiState, count: number) =>
  Math.min(count - 1, Math.floor(s.view * count));
export const dtiReveal = (s: DtiState) => s.scene === 'reference' && s.reference > 0.5;
export const dtiScalar = (s: DtiState) =>
  (
    s.scene === 'reference'
      ? Math.min(1, Math.max(0, Math.floor((s.view - 0.5) * 4)))
      : dtiIndex(s, 2)
  )
    ? 'md'
    : 'fa';
export const dtiFa = (ev: number[]) => {
  const mean = ev.reduce((a, b) => a + b, 0) / 3;
  return Math.sqrt(
    (1.5 * ev.reduce((a, b) => a + (b - mean) ** 2, 0)) / ev.reduce((a, b) => a + b ** 2, 0),
  );
};
