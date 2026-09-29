import sourceRaw from '../../task-explorer/rex-isles22/source.json?raw';
import outputRaw from '../../task-explorer/rex-isles22/output.json?raw';
import referenceRaw from '../../task-explorer/rex-isles22/reference.json?raw';

export type RexIslesSceneName = 'inputs' | 'geometry' | 'output' | 'reference' | 'limits';
export type RexIslesState = {
  recipe: 'rex-isles22-v1';
  scene: RexIslesSceneName;
  slice: number;
  flair: number;
  reference: number;
};
export type IslesSample = {
  image: string;
  native_k_zero_based: number;
  center_ras_mm: number[];
  shape_xy_pixels: number[];
};
export type IslesModality = {
  shape_ijk: number[];
  spacing_ijk_mm: number[];
  affine_ijk_to_ras_mm: number[][];
  samples: IslesSample[];
  display_window_scaled_native_values: number[];
  source_sha256: string;
};
export const islesSource = JSON.parse(sourceRaw) as {
  case_id: string;
  source_case_id: string;
  modalities: Record<'dwi' | 'adc' | 'flair', IslesModality>;
  split: { complete_official_cases: number; train: number; test: number; rule: string };
  cross_grid_resampling: false;
};
export const islesOutput = JSON.parse(outputRaw) as {
  status: 'not-retained';
  agent_prediction: null;
  score: null;
  required_csv_header: string[];
  illustrative_row: string[];
};
export const islesReference = JSON.parse(referenceRaw) as {
  role: string;
  positive_voxels: number;
  total_voxels: number;
  samples: { image: string; native_k_zero_based: number; positive_voxels_in_slice: number }[];
};
const images = import.meta.glob<string>('../../task-explorer/rex-isles22/images/*.png', {
  eager: true,
  query: '?url',
  import: 'default',
});
export function islesImage(file: string): string {
  const url = images[`../../task-explorer/rex-isles22/${file}`];
  if (!url) throw new Error(`Missing ISLES22 image ${file}`);
  return url;
}
export function islesSample(modality: IslesModality, progress: number): IslesSample {
  const i = Math.max(
    0,
    Math.min(modality.samples.length - 1, Math.round(progress * (modality.samples.length - 1))),
  );
  return modality.samples[i];
}
export const islesRevealed = (state: RexIslesState) =>
  state.scene === 'reference' && state.reference > 0.5;
