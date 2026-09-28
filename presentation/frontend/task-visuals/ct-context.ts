import inputs from '../../task-explorer/ct-context/inputs.json?raw';
import output from '../../task-explorer/ct-context/output.json?raw';
import reference from '../../task-explorer/ct-context/reference.json?raw';
import type { StoryState } from './story-timeline';
export type CtContextState = Extract<StoryState, { recipe: 'ct-context-v1' }>;
export const contextInputs = JSON.parse(inputs) as {
  geometry: {
    visit: string;
    shape: number[];
    spacing_mm: number[];
    affine: number[][];
    axes: string[];
    extensions: number;
    descrip: string;
  }[];
  images: {
    id: string;
    visit: string;
    region: string;
    k: number;
    bounds: number[];
    width: number;
    height: number;
    png: string;
    point: number[] | null;
    roi: number[] | null;
  }[];
};
export const contextOutput = JSON.parse(output) as {
  fields: Record<
    string,
    {
      status: 'inferred' | 'unknown' | 'observed';
      value: string | number | null;
      confidence: number;
      basis: string;
      alternatives: string[];
    }
  >;
  counts: { inferred: number; unknown: number; observed: number };
  agent_seconds: number;
};
export const contextReference = JSON.parse(reference) as {
  metadata: Record<string, { value: string | number | null; level: string }>;
  diagnostics: { id: string; contract_valid: boolean; scientific_score: null }[];
  rewards: { id: string; reward: number }[];
};
export const contextFields = [
  [
    'broad_diagnosis',
    'Broad diagnosis',
    'Suspected metastatic liver disease',
    'Multiplicity and increased visible burden support an imaging inference; histology remains unproved.',
  ],
  [
    'specific_primary_diagnosis',
    'Specific primary',
    'Unknown',
    'Melanoma appears among alternatives; compatible features do not establish a primary or histology.',
  ],
  [
    'age_years',
    'Age in years',
    'Unknown',
    'Adult appearance does not establish chronological age. No birth or scan date was supplied.',
  ],
  [
    'recorded_sex',
    'Recorded sex',
    'Unknown',
    'No demographic record was supplied. Visible anatomy does not establish a recorded field.',
  ],
  [
    'interval_days',
    'Interval in days',
    'Unknown',
    'Earlier/later order was given. Spatial origins, voxel spacing and visible change do not encode elapsed days.',
  ],
  [
    'baseline_scan_purpose',
    'Baseline purpose',
    'Unknown',
    'Staging, restaging and surveillance are possibilities. “Baseline” does not establish treatment-naive status.',
  ],
  [
    'followup_scan_purpose',
    'Follow-up purpose',
    'Unknown',
    'Reassessment is plausible. Worsening appearance does not establish the ordering indication.',
  ],
  [
    'systemic_treatment_context',
    'Systemic treatment',
    'Unknown',
    'No drugs or treatment dates were supplied. Image change does not establish regimen or treatment failure.',
  ],
  [
    'surgical_context',
    'Surgical context',
    'Probable prior local intervention',
    'Groin changes support a qualified suggestion; procedure, indication and timing remain unestablished.',
  ],
] as const;
export function contextSelection(s: CtContextState) {
  return {
    field: Math.min(8, Math.max(0, Math.floor(s.view * 9))),
    reference: s.reference > 0.5,
    output: s.output > 0.5,
  };
}
export function contextPixel(
  view: (typeof contextInputs.images)[number],
  point: readonly number[],
) {
  return [point[0] - view.bounds[0] + 0.5, point[1] - view.bounds[2] + 0.5];
}
