import sourceRaw from '../../task-explorer/abra-birads/source.json?raw';
import operationRaw from '../../task-explorer/abra-birads/operation.json?raw';
import outputRaw from '../../task-explorer/abra-birads/output.json?raw';
import derivationRaw from '../../task-explorer/abra-birads/derivation.json?raw';
import type { StoryState } from './story-timeline';

export type AbraBiradsState = Extract<StoryState, { recipe: 'abra-birads-v1' }>;
type Condition = {
  id: 'visual' | 'oracle';
  label: string;
  vision: boolean;
  max_turns: number;
  steps: string[];
  assistance: string;
  remaining: string;
};
export const abraBiradsPack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    study: { patient_id: string; study_uid: string };
    series: { modality: string; description: string; num_instances: number; series_uid: string }[];
    ordering: string;
    pixels: null;
    generated_task: null;
  },
  operation: JSON.parse(operationRaw) as {
    conditions: Condition[];
    preprocessor: string;
    visual_reference_trajectory: string;
    executed: false;
  },
  output: JSON.parse(outputRaw) as {
    fields: string[];
    values: Record<string, null>;
    optional_quadrant: string;
    weights: Record<string, number>;
    submitted_report: null;
    oracle_response: null;
    score: null;
    private_reference: null;
  },
  derivation: JSON.parse(derivationRaw) as {
    rules: Record<string, string>;
    constructed_constants: { birads_category: number; enhancement_present: boolean };
    warning: string;
    category_credit: string;
    count_credit: string;
    laterality_caveat: string;
    quadrant_credit: string;
    score_boundary: string;
    private_reference: null;
  },
};
