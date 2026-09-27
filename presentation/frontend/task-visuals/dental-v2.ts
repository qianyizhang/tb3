import sourceRaw from '../../task-explorer/dental-v2/source.json?raw';
import outputRaw from '../../task-explorer/dental-v2/output.json?raw';
import referenceRaw from '../../task-explorer/dental-v2/reference.json?raw';
import type { StoryState } from './story-timeline';

export type DentalV2State = Extract<StoryState, { recipe: 'dental-v2-v1' }>;
export type V2Item = {
  id: number | string;
  paths: number[][][];
  pixels: number;
  center: number[] | null;
};
export type V2Plane = {
  case: string;
  axis: string;
  index: number;
  plane_axes: string[];
  bounds_uv: number[][];
  width: number;
  height: number;
  png: string;
  selection: string;
};
type Overlap = {
  gt: number;
  pred: number;
  tp: number;
  dice: number;
  precision: number;
  recall: number;
};
type Pooled = {
  gt_voxels: number;
  prediction_voxels: number;
  intersection: number;
  dice: number;
  precision: number;
  recall: number;
};
export const dentalV2Source = JSON.parse(sourceRaw) as {
  views: Record<string, V2Plane>;
  example_annotations: Record<string, V2Item[]>;
};
export const dentalV2Outputs = JSON.parse(outputRaw) as {
  views: Record<string, Record<string, V2Item[]>>;
  registration: {
    warped_example_png: string;
    atlas_plane_exactly_reproduced: boolean;
    replayed_plane_voxels: number;
  };
};
export const dentalV2Reference = JSON.parse(referenceRaw) as {
  views: Record<string, V2Item[]>;
  conditions: {
    original_macro_dice: number;
    active_labels: number;
    posthoc_common_label_macro_dice: number;
    common_label_set: number[];
    pulp_pooled: Pooled;
    main_canals_pooled: Pooled;
    small_canals_pooled: Pooled;
    identity_counts: {
      gt: number;
      predicted: number;
      detected: number;
      correct_among_detected: number;
    };
    tooth_matches: { gt_id: number; predicted_id: number; dice: number; correct_fdi: boolean }[];
  }[];
  metrics: {
    score: {
      macro_dice: number;
      groups: Record<
        string,
        { macro_dice: number; active_labels: number; pooled_geometry_dice: number }
      >;
      whole_tooth_geometry_and_identity: { geometry_mean_dice_with_unmatched_zero: number };
      per_label: { id: number; dice: number | null }[];
    };
    seconds: number;
    usage: { n_output_tokens: number };
  }[];
  clipping: {
    before_true_overlap: number;
    after_true_overlap: number;
    removed_true_pulp_voxels: number;
    removed_pulp_voxels: number;
    allowed_distance_mm: number;
  };
  fine_diagnostics: {
    'diagnostics.json': {
      pulp: {
        example_true_teeth_target22_ids: { score: Overlap };
        target_true_teeth: { score: Overlap };
        target_predicted_teeth: { score: Overlap };
      };
      canals: { label: number; path_samples_inside_gt_fraction: number; final: Overlap }[];
    };
    'supplement.json': {
      saturated_pulp: { label: number; gt_voxels: number; raw_CT_above3000: number }[];
    };
  };
};
export const dentalV2Colors = {
  baseline: '#fb923c',
  assisted: '#32d8e2',
  example: '#32d8e2',
  atlas: '#d197ff',
  prior: '#d197ff',
  reference: '#9beb72',
  allowed: '#d197ff',
  removed: '#f472b6',
  before: '#32d8e2',
  after: '#32d8e2',
};
export const dentalV2Stages = ['before', 'prior', 'removed', 'after'] as const;
export function dentalV2Selection(s: DentalV2State) {
  return {
    helper: s.helper > 0.5,
    output: s.output > 0.5,
    reveal: s.reference > 0.5,
    pulpId: s.view < 0.5 ? 116 : 131,
    canalId: s.view < 0.5 ? 103 : 104,
    canalView: s.view < 0.5 ? 'canals-145' : 'canals-205',
    stage: dentalV2Stages[Math.min(3, Math.floor(s.stage * 4))],
    transfer: s.transfer,
  };
}
export const dentalV2Path = (items: V2Item[]) =>
  items
    .flatMap((item) => item.paths)
    .map((p) => p.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join('') + 'Z')
    .join('');
