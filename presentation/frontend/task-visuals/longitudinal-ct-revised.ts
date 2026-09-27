import source from '../../task-explorer/longitudinal-ct-revised/source.json?raw';
import firstBaseline from '../../task-explorer/longitudinal-ct-revised/case1-baseline.json?raw';
import firstFollowup from '../../task-explorer/longitudinal-ct-revised/case1-followup.json?raw';
import secondBaseline from '../../task-explorer/longitudinal-ct-revised/case2-baseline.json?raw';
import secondFollowup from '../../task-explorer/longitudinal-ct-revised/case2-followup.json?raw';
import reference from '../../task-explorer/longitudinal-ct-revised/reference.json?raw';
import type { StoryState } from './story-timeline';
export type RevisedCtState = Extract<StoryState, { recipe: 'longitudinal-ct-revised-v1' }>;
export type CtCondition = 'case1-original' | 'case1-revised' | 'case2-image' | 'case2-context';
interface Outline {
  image: string;
  labels: { id: number; pixel_ij: number[] }[];
}
export interface RevisedCtView {
  visit: string;
  k: number;
  image: string;
  reference: Outline;
  outputs: Record<CtCondition, Outline>;
  fov_mm: number;
  z_ras_mm: number;
  width_pixels: number;
  origin_ij: number[];
  selection: string;
  reported_point_ijk?: number[];
}
interface VisitViews {
  partition?: RevisedCtView[];
  focus?: RevisedCtView;
  dominant?: RevisedCtView;
  excluded?: RevisedCtView;
  new_focus?: RevisedCtView[];
}
export const revisedViews = [firstBaseline, firstFollowup, secondBaseline, secondFollowup].map(
  (x) => JSON.parse(x),
) as VisitViews[];
export const revisedSource = JSON.parse(source) as {
  overview: {
    case: string;
    visit: string;
    shape: number[];
    spacing_mm: number[];
    k: number;
    image: string;
  }[];
  colors: Record<string, string>;
  clinical_context: Record<
    string,
    { value: string | number | null; level: string; reference_date?: string }
  >;
};
interface Event {
  event: string;
  baseline_ids: number[];
  followup_ids: number[];
}
interface Score {
  tp: number;
  fp: number;
  fn: number;
  f1: number | null;
}
interface Metrics {
  valid: boolean;
  detection_micro: Score;
  segmentation_gt_macro_dice: number;
  visits: Record<
    string,
    {
      ids: number[];
      mapping: Record<string, number>;
      segmentation: { foreground_dice: number };
      per_gt: {
        gt_id: number;
        detection_prediction_id: number | null;
        best_one_to_one_dice: number;
      }[];
    }
  >;
  association: {
    links_end_to_end: Score;
    events_end_to_end: Score;
    links_conditional_on_detection: Score & { eligible_gt_edges: number; total_gt_edges: number };
    events_conditional_on_detection: Score & {
      eligible_gt_groups: number;
      total_gt_groups: number;
    };
    mapped_predictions: Event[];
  };
}
export interface RevisedInstance {
  case: string;
  visit: string;
  id: number;
  voxels: number;
  volume_ml: number;
  center_ijk: number[];
  center_ras_mm: number[];
  stratum: string;
  components_6: number[];
  outputs: Record<
    CtCondition,
    { matched_id: number | null; gt_macro_dice: number; coverage: number }
  >;
}
export const revisedRef = JSON.parse(reference) as {
  instances: RevisedInstance[];
  measurements: {
    case: string;
    visit: string;
    instances: number;
    total_reference_ml: number;
    dominant_reference_ml: number;
    dominant_share: number;
  }[];
  strata: Record<
    string,
    { stratum: string; count: number; localized: number; macro_dice: number }[]
  >;
  groups: Record<string, Event[]>;
  results: Record<CtCondition, { metrics: Metrics; events: { groups: Event[] }; report: string }>;
  point_checks: {
    visit: string;
    point_ijk: number[];
    reference_id: number;
    context_mask_at_point: number;
  }[];
};
export const revisedIndex = (view: number, n = 3) =>
  Math.min(n - 1, Math.floor(Math.max(0, view) * n));
export const revisedReference = (s: RevisedCtState) => s.reference > 0.5;
export const revisedOutput = (s: RevisedCtState) => s.output > 0.5;
export const ctNativePoint = (point: number[], view: RevisedCtView) =>
  point.slice(0, 2).map((v, i) => ((v - view.origin_ij[i]) / view.width_pixels) * 256);
export function recoveredIdentities(condition: CtCondition) {
  return Object.entries(revisedRef.results[condition].metrics.visits)
    .flatMap(([visit, v]) => Object.values(v.mapping).map((id) => `${visit}:${id}`))
    .sort();
}
/** These are visit-level annotations; the two large records share one identity. */
export function sizeSummary(condition: CtCondition) {
  return ['<=1 mL', '>1 to 10 mL', '>10 mL'].map((stratum) => {
    const rows = revisedRef.instances.filter((r) => r.case === 'case2' && r.stratum === stratum);
    return {
      stratum,
      total: rows.length,
      matched: rows.filter((r) => r.outputs[condition].matched_id !== null).length,
    };
  });
}
