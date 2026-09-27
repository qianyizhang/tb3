import sourceRaw from '../../task-explorer/segmentation-calibration/source.json?raw';
import outputRaw from '../../task-explorer/segmentation-calibration/output.json?raw';
import referenceRaw from '../../task-explorer/segmentation-calibration/reference.json?raw';
import type { StoryState } from './story-timeline';

export type CalibrationState = Extract<StoryState, { recipe: 'segmentation-calibration-v1' }>;
export type BoxCondition = 'tight' | 'loose';
export type CalibrationMask = { paths: number[][][]; pixels: number };
export type CalibrationMetric = {
  id: string;
  tag: string;
  condition: BoxCondition;
  dice: number;
  precision: number;
  recall: number;
  hd95_mm: number;
  pred_pixels: number;
  gt_pixels: number;
  intersection: number;
  false_positive_pixels: number;
  false_negative_pixels: number;
};
type Timing = {
  count: number;
  load_seconds: number;
  warmup_seconds: number;
  encode_median_ms: number;
  prompt_median_ms: number;
  process_peak_rss_mib: number;
  driver_memory_max_observed_mib: number;
};
type Aggregate = Timing &
  Record<BoxCondition, { mean_dice: number; median_dice: number; mean_hd95_mm: number }>;
export const calibrationSource = JSON.parse(sourceRaw) as {
  views: Record<
    string,
    {
      id: string;
      organ: string;
      q: number;
      slice_k: number;
      png: string;
      width: number;
      height: number;
      boxes: Record<BoxCondition, number[]>;
      detail_bounds_xyxy: number[];
      lite_boxes_256: Record<BoxCondition, number[]>;
      sam2_boxes_1024: Record<BoxCondition, number[]>;
    }
  >;
};
export const calibrationOutput = JSON.parse(outputRaw) as {
  views: Record<string, Record<string, Partial<Record<BoxCondition, CalibrationMask>>>>;
  timing: Record<string, Timing>;
  timing_denominators: Record<
    string,
    { unique_image_encodes: number; cached_box_decodes: number; first_measured_encode_ms: number }
  >;
};
export const calibrationReference = JSON.parse(referenceRaw) as {
  views: Record<string, CalibrationMask>;
  aggregates: Record<string, Aggregate>;
  replays: CalibrationMetric[];
  control_rows: CalibrationMetric[];
  controls: {
    exact_mask_dice: number;
    empty_mask_dice: number;
    filled_box_mean_dice: Record<BoxCondition, number>;
  };
  per_organ: {
    organ: string;
    sam2_tight: number;
    sam2_loose: number;
    lite_tight: number;
    lite_loose: number;
  }[];
  backend_pairs: {
    model: string;
    id: string;
    condition: BoxCondition;
    differing_pixels: number;
    cpu_mps_mask_dice: number;
  }[];
  sam2_backend: {
    count: number;
    median_mask_dice: number;
    below_095: number;
    minimum: { cpu_mps_mask_dice: number };
  };
};
export const calibrationOrgans = [
  'liver',
  'kidney_right',
  'gallbladder',
  'pancreas',
  'adrenal_gland_right',
  'duodenum',
] as const;
export const calibrationLabels: Record<string, string> = {
  liver: 'Liver',
  kidney_right: 'Right kidney',
  gallbladder: 'Gallbladder',
  pancreas: 'Pancreas',
  adrenal_gland_right: 'Right adrenal',
  duodenum: 'Duodenum',
  'sam2-mps': 'SAM 2.1 Small · MPS',
  'lite-mps': 'LiteMedSAM · MPS',
  'sam2-cpu': 'SAM2 · CPU',
};
export const calibrationColors: Record<string, string> = {
  'sam2-mps': '#32d8e2',
  'lite-mps': '#fb923c',
  'sam2-cpu': '#d197ff',
  reference: '#9beb72',
  box: '#f5d76e',
};
const select = <T>(values: readonly T[], p: number) =>
  values[Math.min(values.length - 1, Math.floor(p * values.length))];
export function calibrationSelection(s: CalibrationState) {
  const organ = select(calibrationOrgans, s.view);
  return {
    sample:
      s.scene === 'inputs'
        ? 'liver_q50'
        : s.scene === 'sampling'
          ? select(['pancreas_q25', 'pancreas_q50', 'pancreas_q75'], s.view)
          : s.scene === 'sensitivity'
            ? organ + '_q50'
            : s.scene === 'duodenum'
              ? 'duodenum_q50'
              : s.scene === 'backend'
                ? select(['adrenal_gland_right_q50', 'liver_q25'], s.view)
                : 'pancreas_q50',
    organ,
    condition: select(['tight', 'loose'] as const, s.condition),
    box: s.box > 0.5,
    output: s.output > 0.5,
    reveal: s.reference > 0.5,
  };
}
export const calibrationPath = (mask: CalibrationMask) =>
  mask.paths.map((p) => p.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join('') + 'Z').join('');
export const calibrationMetric = (tag: string, id: string, condition: BoxCondition) =>
  calibrationReference.replays.find(
    (r) => r.tag === tag && r.id === id && r.condition === condition,
  )!;
