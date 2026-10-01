import image from '../../task-explorer/automedbench-full-vqa-rad-task/image.jpg';
import sourceRaw from '../../task-explorer/automedbench-full-vqa-rad-task/source.json?raw';
import helperRaw from '../../task-explorer/automedbench-full-vqa-rad-task/helper.json?raw';
import operationRaw from '../../task-explorer/automedbench-full-vqa-rad-task/operation.json?raw';
import outputRaw from '../../task-explorer/automedbench-full-vqa-rad-task/output.json?raw';
import type { StoryState } from './story-timeline';
export type AutomedVqaRadState = Extract<StoryState, { recipe: 'automed-vqa-rad-v1' }>;
export const automedVqaRadPack = {
  image,
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    question: string;
    geometry: string;
    question_unit: string;
  },
  helper: JSON.parse(helperRaw) as {
    public_answer: string;
    public_answer_role: string;
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

export const operationSteps = [
  'Question + images',
  'Method + raw decode',
  'Phrase / yes-no',
  'Six-field write',
] as const;
export function operationIndex(state: AutomedVqaRadState) {
  return Math.min(3, Math.max(0, Math.round(state.progress * 3)));
}
export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}
export function publicAnnotationVisible(state: AutomedVqaRadState, requested = false) {
  return state.scene === 'helper' && requested;
}
export function operationFrame(plan: import('../contracts.generated').StoryPlan, index: number) {
  if (plan.recipe !== 'automed-vqa-rad-v1' || !Number.isInteger(index) || index < 0 || index > 3)
    throw new Error('VQA-RAD operation mismatch');
  const beat = plan.beats.find((b) => b.scene === 'operation');
  if (!beat) throw new Error('Missing VQA-RAD operation beat');
  const target = index / 3;
  let best = 0,
    distance = Infinity;
  for (let frame = 0; frame < beat.frames; frame++) {
    const u = frame / beat.frames,
      eased = u * u * (3 - 2 * u),
      value = Math.abs(eased - target);
    if (value < distance) {
      distance = value;
      best = frame;
    }
  }
  return beat.startFrame + best;
}
