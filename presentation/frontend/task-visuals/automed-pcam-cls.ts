import figureUrl from '../../task-explorer/automedbench-full-patchcamelyon-cls-task/figure.jpg';
import sourceRaw from '../../task-explorer/automedbench-full-patchcamelyon-cls-task/source.json?raw';
import helperRaw from '../../task-explorer/automedbench-full-patchcamelyon-cls-task/helper.json?raw';
import operationRaw from '../../task-explorer/automedbench-full-patchcamelyon-cls-task/operation.json?raw';
import outputRaw from '../../task-explorer/automedbench-full-patchcamelyon-cls-task/output.json?raw';
import type { StoryState } from './story-timeline';
export type AutomedPcamClsState = Extract<StoryState, { recipe: 'automed-pcam-cls-v1' }>;
export const automedPcamClsPack = {
  figureUrl,
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
  },
  helper: JSON.parse(helperRaw) as {
    classes: string[];
    source_mapping: Record<string, string>;
    figure_partition: null;
    split_boundary: string;
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
