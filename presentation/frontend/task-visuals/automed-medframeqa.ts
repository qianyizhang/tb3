import frame1 from '../../task-explorer/automedbench-full-medframeqa-task/frame-1.jpg';
import frame2 from '../../task-explorer/automedbench-full-medframeqa-task/frame-2.jpg';
import sourceRaw from '../../task-explorer/automedbench-full-medframeqa-task/source.json?raw';
import helperRaw from '../../task-explorer/automedbench-full-medframeqa-task/helper.json?raw';
import operationRaw from '../../task-explorer/automedbench-full-medframeqa-task/operation.json?raw';
import outputRaw from '../../task-explorer/automedbench-full-medframeqa-task/output.json?raw';
import type { StoryState } from './story-timeline';
export type AutomedMedframeqaState = Extract<StoryState, { recipe: 'automed-medframeqa-v1' }>;
export const automedMedframeqaPack = {
  frames: [frame1, frame2],
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    order: string;
    geometry: string;
  },
  helper: JSON.parse(helperRaw) as {
    valid_labels: string[];
    source_options: number;
    mapping: string;
    tiers: Record<'lite' | 'standard', string>;
    tools: string[];
    calibration: string;
  },
  operation: JSON.parse(operationRaw) as { steps: string[] },
  output: JSON.parse(outputRaw) as {
    path: string;
    fields: Record<string, string>;
    format: string;
    accuracy: string;
    format_gate: string;
    completion: string;
    rating_rule: string;
    workflow: string;
    limits: string;
    checker_difference: string;
  },
};

import type { StoryPlan } from '../contracts.generated';
export function operationIndex(progress: number): number {
  return Math.max(0, Math.min(3, Math.round(progress * 3)));
}
export function operationFrame(plan: StoryPlan, index: number): number {
  if (plan.recipe !== 'automed-medframeqa-v1' || !Number.isInteger(index) || index < 0 || index > 3)
    throw new Error('Invalid operation');
  const beat = plan.beats.find((b) => b.scene === 'operation');
  if (!beat) throw new Error('Operation absent');
  return Math.round(beat.startFrame + ((beat.frames - 1) * index) / 3);
}
export function resetOnBackward(previous: number, next: number): boolean {
  return next < previous;
}
