import sourceRaw from '../../task-explorer/automed-kidney/source.json?raw';
import outputRaw from '../../task-explorer/automed-kidney/output.json?raw';
import referenceRaw from '../../task-explorer/automed-kidney/reference.json?raw';

export type AutomedKidneySceneName =
  'inputs' | 'assistance' | 'workflow' | 'schema' | 'reference' | 'contract' | 'limits';
export type AutomedKidneyState = {
  recipe: 'automed-kidney-v1';
  scene: AutomedKidneySceneName;
  view: number;
  helper: number;
  step: number;
  reference: number;
  fixture: number;
};
export const kidneySource = JSON.parse(sourceRaw) as {
  case: string;
  kind: string;
  shape: number[];
  spacing_mm: number[];
  axis_codes: string[];
  affine: number[][];
  views: { index: number; ct_png: string; window_hu: number[] }[];
  source_sha256: string;
  source_url: string;
};
export const kidneyOutput = JSON.parse(outputRaw) as {
  saved_prediction: null;
  patient_path: string;
  required: string[];
  empty_artifacts: { name: string; data: null }[];
  shape: number[];
  affine: number[][];
  values: string;
  steps: { id: string; name: string; action: string }[];
  tiers: { name: string; help: string }[];
  config_budget_seconds: number;
  fixture_scope: string;
  fixtures: {
    id: string;
    quick_check_complete: boolean;
    format_valid: boolean;
    organ_dice: number;
    lesion_dice_positive: number;
    lesion_positive_cases: number;
    cases: number;
  }[];
  audit_sha256: string;
};
export const kidneyReference = JSON.parse(referenceRaw) as {
  kind: string;
  source_sha256: string;
  mapping: { target: string; rule: string; color: string }[];
  views: { index: number; overlay_png: string; organ_voxels: number; lesion_voxels: number }[];
  source_url: string;
};
export const kidneyIndex = (progress: number, length: number) =>
  Math.min(length - 1, Math.max(0, Math.floor(progress * length)));
export const kidneyRevealed = (s: AutomedKidneyState) =>
  s.scene === 'reference' && s.reference > 0.5;
