import source from '../../task-explorer/longitudinal-ct-original/source.json?raw';
import baseline from '../../task-explorer/longitudinal-ct-original/baseline.json?raw';
import followup from '../../task-explorer/longitudinal-ct-original/followup.json?raw';
import reference from '../../task-explorer/longitudinal-ct-original/reference.json?raw';
import type { StoryState } from './story-timeline';
export type CtOriginalState = Extract<StoryState, { recipe: 'longitudinal-ct-original-v1' }>;
export interface CtView {
  visit: string;
  k: number;
  image: string;
  reference?: string;
  astra: string;
  fov_mm: number;
  z_ras_mm: number;
  width_pixels: number;
  origin_ij: number[];
}
interface Visit {
  boundary_frames: CtView[];
  focus: CtView;
  saved_output_view: CtView;
}
export interface CtEvent {
  baseline_ids: number[];
  followup_ids: number[];
  event: string;
}
interface CountScore {
  tp: number;
  fp: number;
  fn: number;
  precision: number | null;
  recall: number | null;
  f1: number | null;
}
export const ctSource = JSON.parse(source) as {
  overview: {
    visit: string;
    shape: number[];
    spacing_mm: number[];
    affine_ras_mm: number[][];
    k: number;
    image: string;
  }[];
  reference_colors: Record<string, string>;
  output_color: string;
};
export const ctVisits = [JSON.parse(baseline), JSON.parse(followup)] as Visit[];
export const ctReference = JSON.parse(reference) as {
  groups: CtEvent[];
  instances: {
    visit: string;
    id: number;
    voxels: number;
    center_ijk: number[];
    center_ras_mm: number[];
    volume_ml: number;
  }[];
  coverage: { visit: string; reference_id: number; astra_fraction_covered: number }[];
  conditions: {
    condition: string;
    model: string;
    effort: string;
    events: { schema_version: number; groups: CtEvent[] };
    metrics: {
      valid: boolean;
      detection_micro: CountScore;
      segmentation_gt_macro_dice: number;
      visits: Record<
        string,
        {
          ids: number[];
          mapping: Record<string, number>;
          segmentation: { foreground_dice: number };
        }
      >;
      association: {
        links_end_to_end: CountScore;
        links_conditional_on_detection: CountScore & {
          eligible_gt_edges: number;
          total_gt_edges: number;
        };
        events_end_to_end: CountScore;
        events_conditional_on_detection: CountScore & {
          eligible_gt_groups: number;
          total_gt_groups: number;
        };
        mapped_predictions: CtEvent[];
      };
    };
  }[];
};
export const ctFrameIndex = (value: number, length = 6) =>
  Math.min(length - 1, Math.floor(Math.max(0, value) * length));
export const ctShowReference = (state: CtOriginalState) => state.reference > 0.5;
export const ctShowOutput = (state: CtOriginalState) => state.output > 0.5;
export function ctEdges(groups: CtEvent[]): [number, number][] {
  return groups
    .filter((g) => ['persistent', 'merging'].includes(g.event))
    .flatMap((g) =>
      g.baseline_ids.flatMap((b) => g.followup_ids.map((f): [number, number] => [b, f])),
    );
}
/** Eligibility is a denominator, not proof that complete events were tested. */
export function ctEligibleGroups(groups: CtEvent[], baselineIds: number[], followupIds: number[]) {
  return groups.filter(
    (g) =>
      g.baseline_ids.every((id) => baselineIds.includes(id)) &&
      g.followup_ids.every((id) => followupIds.includes(id)),
  );
}
