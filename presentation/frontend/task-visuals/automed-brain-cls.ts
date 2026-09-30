import sourceRaw from '../../task-explorer/automedbench-full-braintumor-cls-task/source.json?raw';
import helperRaw from '../../task-explorer/automedbench-full-braintumor-cls-task/helper.json?raw';
import operationRaw from '../../task-explorer/automedbench-full-braintumor-cls-task/operation.json?raw';
import outputRaw from '../../task-explorer/automedbench-full-braintumor-cls-task/output.json?raw';
import type { StoryState } from './story-timeline';
export type AutomedBrainClsState = Extract<StoryState, { recipe: 'automed-brain-cls-v1' }>;
export const automedBrainClsPack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
  },
  helper: JSON.parse(helperRaw) as {
    classes: string[];
    tiers: Record<'lite' | 'standard', string>;
    index_boundary: string;
    training_labels: string;
  },
  operation: JSON.parse(operationRaw) as { steps: string[] },
  output: JSON.parse(outputRaw) as {
    formats: Record<'csv' | 'json', string>;
    format_boundary: string;
    accuracy: string;
    balanced_accuracy: string;
    units: string;
    overall: string;
    workflow: string;
    tiers: string;
    CSV_precedence: string;
    clinical_boundary: string;
  },
};
