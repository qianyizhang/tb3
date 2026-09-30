import sourceRaw from '../../task-explorer/automedbench-full-mimic-cxr-report-task/source.json?raw';
import helperRaw from '../../task-explorer/automedbench-full-mimic-cxr-report-task/helper.json?raw';
import operationRaw from '../../task-explorer/automedbench-full-mimic-cxr-report-task/operation.json?raw';
import outputRaw from '../../task-explorer/automedbench-full-mimic-cxr-report-task/output.json?raw';
import type { StoryState } from './story-timeline';
export type AutomedMimicReportState = Extract<StoryState, { recipe: 'automed-mimic-report-v1' }>;
export const automedMimicReportPack = {
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

export type MimicOperationPlan = Extract<
  import('../contracts.generated').StoryPlan,
  { recipe: 'automed-mimic-report-v1' }
>;
export function operationIndex(progress: number): number {
  return Math.min(3, Math.max(0, Math.round(progress * 3)));
}
export function operationFrame(
  plan: import('../contracts.generated').StoryPlan,
  index: number,
): number {
  if (plan.recipe !== 'automed-mimic-report-v1') throw new Error('Recipe mismatch');
  if (!Number.isInteger(index) || index < 0 || index > 3) throw new Error('Invalid step');
  const b = plan.beats.find((b) => b.scene === 'operation');
  if (!b) throw new Error('Operation absent');
  return Math.round(b.startFrame + ((b.frames - 1) * index) / 3);
}
export function canonicalTier(value: string): 'lite' | 'standard' | null {
  return value === 'lite' || value === 'standard' ? value : null;
}
export function canonicalMetric(value: string): 'macro' | 'micro' | null {
  return value === 'macro' || value === 'micro' ? value : null;
}
export function resetOnBackward(prev: number, next: number): boolean {
  return next < prev;
}
