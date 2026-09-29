import sourceRaw from '../../task-explorer/report-reading/source.json?raw';
import outputRaw from '../../task-explorer/report-reading/output.json?raw';
import referenceRaw from '../../task-explorer/report-reading/reference.json?raw';

export type ReportReadingSceneName =
  'availability' | 'input' | 'viewer' | 'answer' | 'reference' | 'comparison' | 'limits';
export type ReportReadingState = {
  recipe: 'report-reading-v1';
  scene: ReportReadingSceneName;
  phase: number;
  helper: number;
  output: number;
  reference: number;
};
export const reportSource = JSON.parse(sourceRaw) as {
  warning: { label: string; text: string; url: string; link_label: string };
  admitted_pairs: 0;
  model_trials: 0;
  actual_volume: null;
  actual_report: null;
  context_slots: string[];
  viewer_roles: string[];
  location_convention: string;
  private_not_input: string[];
};
export const reportOutput = JSON.parse(outputRaw) as {
  is_actual_answer: false;
  filename: 'answer.json';
  empty_fields: Record<'findings' | 'impression' | 'limitations' | 'evidence_summary', []>;
  finding_slots: string[];
  certainty_vocabulary: string[];
  evidence_location_slots: string[];
};
export const reportReference = JSON.parse(referenceRaw) as {
  is_actual_report: false;
  claim_slots: string[];
  source_claim_routes: string[];
  solver_addition_routes: string[];
  rule: string;
  proposed_controls: string[];
  control_results: null;
};
export const reportReveal = (state: ReportReadingState) =>
  state.reference > 0.5 && ['reference', 'comparison', 'limits'].includes(state.scene);
export const reportColors = { input: '#75a4d5', output: '#13afbd', reference: '#d99722' };
