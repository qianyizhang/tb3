import geometry from '../../task-explorer/registration-analysis/geometry.json?raw';
import reference from '../../task-explorer/registration-analysis/reference.json?raw';
import type { StoryState } from './story-timeline';
export type AnalysisState = Extract<StoryState, { recipe: 'registration-analysis-v1' }>;
export type Patch = { png: string; width: number; height: number };
type Grade = { rms_mm: number; max_mm: number; per_point_mm: number[]; reward: number };
type Support = { id: string; true_offset_local_mm: number[]; distance_to_box_mm: number };
type Variant = {
  name: string;
  composition: string;
  seed: number;
  bound_mm: number;
  grade: Grade;
  search_geometry: Support[];
  box_best_possible_rms_mm: number;
};
type Objective = {
  id: string;
  score_at_manual_target: number;
  score_at_submitted_point: number;
  best_found_score_within_3mm_of_manual: number;
  error_mm: number;
  curve_reference_to_submission: number[];
  curve_fractions: number[];
};
export const analysisGeometry = JSON.parse(geometry) as {
  source_view: Patch;
  queries: { query_ids: string[]; pixels_uv: number[][] };
  patches: Record<string, { source: Patch; submitted: Patch }>;
  original_diagnostics: { id: string; centre: number[]; axes: number[][]; offset: number[] }[];
};
export const analysisReference = JSON.parse(reference) as {
  manual_patches: Record<string, Patch>;
  attempts: { phase: string; grade: Grade }[];
  analysis: {
    replay: { maximum_coordinate_drift_mm: number; stages: Record<string, Grade> };
    counterfactuals: Variant[];
    author_baseline_ablations: { name: string; grade: Grade }[];
    objective_diagnostics: Objective[];
  };
};
export const originalVariant = analysisReference.analysis.counterfactuals.find(
  (v) => v.name === 'original-b9-s17',
)!;
export const analysisColors = {
  query: '#b77128',
  output: '#307f74',
  reference: '#a34575',
  neutral: '#5b7791',
};
export function supportRows(bounds: number) {
  const halfWidth = 9 + 21 * bounds;
  return originalVariant.search_geometry.map((r) => {
    const nearest = r.true_offset_local_mm.map((v) => Math.max(-halfWidth, Math.min(halfWidth, v)));
    return {
      ...r,
      nearest,
      distance: Math.hypot(...nearest.map((v, i) => v - r.true_offset_local_mm[i])),
      halfWidth,
    };
  });
}
export const analysisRevealed = (state: AnalysisState) => state.reference > 0.5;
export function objectiveSamples(id: string, progress: number) {
  const row = analysisReference.analysis.objective_diagnostics.find((r) => r.id === id)!;
  const count = 1 + Math.floor(progress * (row.curve_fractions.length - 1));
  return row.curve_reference_to_submission
    .slice(0, count)
    .map((score, i) => ({ score, t: row.curve_fractions[i] }));
}
