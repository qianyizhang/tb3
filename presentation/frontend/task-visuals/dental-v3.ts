import sourceRaw from '../../task-explorer/dental-v3/source.json?raw';
import outputRaw from '../../task-explorer/dental-v3/output.json?raw';
import referenceRaw from '../../task-explorer/dental-v3/reference.json?raw';
import type { StoryState } from './story-timeline';

export type DentalV3State = Extract<StoryState, { recipe: 'dental-v3-v1' }>;
export type V3Item = {
  id: number | string;
  paths: number[][][];
  pixels: number;
  center: number[] | null;
};
type Frame = {
  case: string;
  plane_axes: string[];
  bounds_uv: number[][];
  width: number;
  height: number;
  selection: string;
};
type Plane = Frame & { axis: string; index: number; png: string };
type Projection = Frame & { label: number; collapsed_axis: string };
type Overlap = {
  gt_voxels: number;
  prediction_voxels: number;
  intersection: number;
  dice: number | null;
  precision: number | null;
  recall: number | null;
};
export const dentalV3Source = JSON.parse(sourceRaw) as {
  views: Record<string, Plane>;
  projections: Record<string, Projection>;
  example_annotations: Record<string, V3Item[]>;
};
export const dentalV3Outputs = JSON.parse(outputRaw) as {
  views: Record<string, Record<string, V3Item[]>>;
  projections: Record<string, Record<string, V3Item[]>>;
  registration: {
    warped_example_png: string;
    atlas_plane_exactly_reproduced: boolean;
    warped_ct_plane_exactly_reproduced: boolean;
    replayed_plane_voxels: number;
    optimization_rerun: boolean;
  };
};
export const dentalV3Reference = JSON.parse(referenceRaw) as {
  views: Record<string, V3Item[]>;
  projections: Record<string, V3Item[]>;
  conditions: {
    original_macro_dice: number;
    active_labels: number;
    identity_counts: {
      gt: number;
      predicted: number;
      detected: number;
      correct_among_detected: number;
    };
  }[];
  metrics: {
    score: {
      macro_dice: number;
      groups: Record<string, { macro_dice: number | null; active_labels: number }>;
      whole_tooth_geometry_and_identity: { geometry_mean_dice_with_unmatched_zero: number };
      per_label: (Overlap & { id: number })[];
      canal_surface_metrics: Record<string, { hd95_mm: number; assd_mm: number; status: string }>;
    };
    seconds: number;
    usage: { n_output_tokens: number };
  }[];
  pooled: { pulp: Overlap; main_canals: Overlap; small_canals: Overlap }[];
  diagnostic_details: {
    label: number;
    conditions: Overlap[];
    transferred_prior: Overlap;
  }[];
  pulp_stages: {
    label: number;
    gt_voxels_full_volume: number;
    gt_voxels_in_tooth_crop: number;
    gt_in_saved_whole_tooth: number;
    gt_within_six_voxels_of_prior_in_crop: number;
    before: Overlap;
    retained_or_geometry_eligible: Overlap;
    extra_after_intensity: Overlap;
    after_component_filter: Overlap;
    saved_intermediate_exact_reproduction: boolean;
  }[];
  canal_stages: {
    label: number;
    bounds_ijk_half_open: number[][];
    gt_voxels_full_volume: number;
    gt_voxels_in_search_crop: number;
    prior: Overlap;
    final: Overlap;
    saved_intermediate_exact_reproduction: boolean;
  }[];
};
export const dentalV3Colors = {
  baseline: '#fb923c',
  assisted: '#32d8e2',
  example: '#32d8e2',
  atlas: '#d197ff',
  reference: '#9beb72',
  eligible: '#f5d76e',
  search_box: '#f5d76e',
  before: '#32d8e2',
  extra: '#32d8e2',
  after: '#32d8e2',
};
export const dentalV3Stages = ['atlas', 'before', 'eligible', 'extra', 'after'] as const;
const select = <T>(values: readonly T[], progress: number) =>
  values[Math.min(values.length - 1, Math.floor(progress * values.length))];
export function dentalV3Selection(s: DentalV3State) {
  return {
    helper: s.helper > 0.5,
    output: s.output > 0.5,
    reveal: s.reference > 0.5,
    gainView: select(['pulp-122-j43', 'pulp-122-j50'], s.view),
    lossView: select(['pulp-127-j156', 'pulp-127-j160', 'pulp-127-j162'], s.view),
    canalView: select(['canal-104-k201', 'canal-104-k204', 'canal-104-k207'], s.view),
    projection: select(['canal-4-along-i', 'canal-4-along-j', 'canal-4-along-k'], s.view),
    stage: select(dentalV3Stages, s.stage),
    transfer: s.transfer,
  };
}
export const dentalV3Path = (items: V3Item[]) =>
  items
    .flatMap((item) => item.paths)
    .map((p) => p.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join('') + 'Z')
    .join('');
