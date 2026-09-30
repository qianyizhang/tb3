import sourceRaw from '../../task-explorer/automedbench-full-chexpert-plus-cxr-task/source.json?raw';
import helperRaw from '../../task-explorer/automedbench-full-chexpert-plus-cxr-task/helper.json?raw';
import operationRaw from '../../task-explorer/automedbench-full-chexpert-plus-cxr-task/operation.json?raw';
import outputRaw from '../../task-explorer/automedbench-full-chexpert-plus-cxr-task/output.json?raw';
import type { StoryState } from './story-timeline';
export type AutomedChexpertReportState = Extract<
  StoryState,
  { recipe: 'automed-chexpert-report-v1' }
>;
export const automedChexpertReportPack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    input: string;
    unit: string;
    original_boundary: string;
    partition: string;
  },
  helper: JSON.parse(helperRaw) as {
    classes: string[];
    schema_boundary: string;
    rules: string;
    tiers: Record<'lite' | 'standard', string>;
    training_labels: string;
  },
  operation: JSON.parse(operationRaw) as { steps: string[] },
  output: JSON.parse(outputRaw) as {
    path: string;
    format: string;
    completeness: string;
    macro: string;
    micro: string;
    selector: string;
    empty_positive: string;
    workflow: string;
    overall: string;
    boundary: string;
  },
};
