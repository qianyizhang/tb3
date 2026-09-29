import sourceRaw from '../../task-explorer/abra-longitudinal/source.json?raw';
import outputRaw from '../../task-explorer/abra-longitudinal/output.json?raw';
import referenceRaw from '../../task-explorer/abra-longitudinal/reference.json?raw';

export type AbraLongitudinalSceneName =
  'inputs' | 'metadata' | 'counts' | 'browse' | 'submit' | 'reference' | 'limits';
export type AbraLongitudinalState = {
  recipe: 'abra-longitudinal-v1';
  scene: AbraLongitudinalSceneName;
  baseline: number;
  followup: number;
  task: number;
  reference: number;
};

export type AbraSample = {
  sample_order_zero_based: number;
  image: string;
  instance_number: number;
  sop_uid: string;
  source_zip_member: string;
  source_dicom_sha256: string;
  image_position_lps_mm: number[];
  pixel_spacing_row_col_mm: number[];
  rows_columns: number[];
  viewer_slice_index: null;
};
export type AbraVisit = {
  role: 'baseline' | 'followup';
  study_uid: string;
  series_uid: string;
  study_date_yyyymmdd: string;
  kernel: string;
  native_instance_count: number;
  sample_count: number;
  sample_rule: string;
  samples: AbraSample[];
};
export const abraSource = JSON.parse(sourceRaw) as {
  frame: string;
  units: string;
  visits: AbraVisit[];
  viewer_order_verified: false;
  cross_study_registration: false;
  display: { window_center_hu: number; window_width_hu: number; formula: string };
};
export const abraOutput = JSON.parse(outputRaw) as {
  status: 'not-retained';
  agent_answer: null;
  agent_finding: null;
  agent_score: null;
};
export const abraReference = JSON.parse(referenceRaw) as {
  role: string;
  interval_days: number;
  slice_count_followup_minus_baseline: number;
  single_lesion: {
    finding_type: string;
    viewer_slice_index_zero_based: number;
    pixel_x: number;
    pixel_y: number;
    lesion_id: string;
    sop_mapping_verified: false;
    patient_image_overlay_allowed: false;
  };
  scorer: {
    metadata: string;
    single_point_threshold_px: number;
    multi_point_threshold_px: number;
    multi_false_positive_penalty: number;
  };
};

const images = import.meta.glob<string>('../../task-explorer/abra-longitudinal/images/*.png', {
  eager: true,
  query: '?url',
  import: 'default',
});
export function abraImage(file: string): string {
  const url = images[`../../task-explorer/abra-longitudinal/${file}`];
  if (!url) throw new Error(`Missing ABRA source image: ${file}`);
  return url;
}
export function abraSample(visit: AbraVisit, position: number): AbraSample {
  const index = Math.max(
    0,
    Math.min(visit.samples.length - 1, Math.round(position * (visit.samples.length - 1))),
  );
  return visit.samples[index];
}
export const abraRevealed = (state: AbraLongitudinalState) =>
  state.scene === 'reference' && state.reference > 0.5;
