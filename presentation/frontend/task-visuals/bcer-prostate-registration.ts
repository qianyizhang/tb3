import sourceRaw from '../../task-explorer/bcer-prostate-registration/source.json?raw';
import operationRaw from '../../task-explorer/bcer-prostate-registration/operation.json?raw';

export type BcerProstateSceneName =
  'availability' | 'inputs' | 'select' | 'coordinates' | 'resample' | 'contract' | 'limits';
export type BcerProstateState = {
  recipe: 'bcer-prostate-registration-v1';
  scene: BcerProstateSceneName;
  view: number;
  moving: number;
  operation: number;
  swap: number;
};
export const bcerSource = JSON.parse(sourceRaw) as {
  case: string;
  role: string;
  frame: 'LPS';
  units: 'mm';
  sequences: {
    name: string;
    size_xyz: number[];
    spacing_xyz_mm: number[];
    origin_lps_mm: number[];
    witness_ijk: number[];
    slice_k: number;
    display_range: number[];
    png: string;
  }[];
  witness_lps_mm: number[];
  warning: {
    text: string;
    source_url: string;
    source_label: string;
    run_url: string;
    run_label: string;
  };
};
export const bcerOperation = JSON.parse(operationRaw) as {
  status: string;
  fixed: 'T2w';
  moving_choices: string[];
  default_method: 'identity';
  default_interpolation: 'linear';
  supported_not_run: string[];
  physical_transform: string;
  mapping: string[];
  witness: { lps_mm: number[]; t2w_ijk: number[]; adc_ijk: number[]; dwi_highb_ijk: number[] };
  output: {
    resampled_path: null;
    transform_path: null;
    expected_space: string;
    saved_medium_run: false;
  };
  required_stages: string[];
  checks: string[];
  alignment_quality_reference: null;
  swap_counterexample: string;
};
export const bcerIndex = (progress: number, n: number) =>
  Math.min(n - 1, Math.max(0, Math.floor(progress * n)));
