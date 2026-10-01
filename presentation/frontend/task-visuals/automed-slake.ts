import type { StoryPlan } from '../contracts.generated';
import image from '../../task-explorer/automedbench-full-slake-task/image.jpg';
import sourceRaw from '../../task-explorer/automedbench-full-slake-task/source.json?raw';
import referenceRaw from '../../task-explorer/automedbench-full-slake-task/reference.json?raw';
import helperRaw from '../../task-explorer/automedbench-full-slake-task/helper.json?raw';
import operationRaw from '../../task-explorer/automedbench-full-slake-task/operation.json?raw';
import outputRaw from '../../task-explorer/automedbench-full-slake-task/output.json?raw';
import type { StoryState } from './story-timeline';
export type AutomedSlakeState = Extract<StoryState, { recipe: 'automed-slake-v1' }>;
export const automedSlakePack = {
  image,
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    question: string;
    geometry: string;
    question_unit: string;
  },
  reference: JSON.parse(referenceRaw) as { public_answer: string; public_answer_role: string },
  helper: JSON.parse(helperRaw) as {
    tiers: Record<'lite' | 'standard', string>;
    tools: string[];
    calibration: string;
  },
  operation: JSON.parse(operationRaw) as { steps: string[]; normalization: string },
  output: JSON.parse(outputRaw) as {
    path: string;
    fields: Record<string, string>;
    format: string;
    accuracy: string;
    judge: string;
    format_gate: string;
    completion: string;
    rating_rule: string;
    workflow: string;
    limits: string;
    checker_difference: string;
  },
};

export function operationIndex(state: AutomedSlakeState) {
  return Math.min(3, Math.max(0, Math.round(state.progress * 3)));
}
export function operationFrame(plan: StoryPlan, step: number) {
  if (plan.recipe !== 'automed-slake-v1') throw new Error('SLAKE recipe mismatch');
  if (!Number.isInteger(step) || step < 0 || step > 3) throw new RangeError('Invalid SLAKE step');
  const beat = plan.beats.find(
    (b) =>
      b.scene === 'operation' &&
      Math.abs(b.channels.progress[0] - step / 3) < 1e-8 &&
      b.channels.progress[0] === b.channels.progress[1],
  );
  if (!beat) throw new Error('Missing canonical SLAKE step');
  return beat.startFrame;
}
export function readerVisible(state: AutomedSlakeState, revealed = false) {
  return state.scene === 'helper' && state.reference > 0 && revealed;
}
export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}
