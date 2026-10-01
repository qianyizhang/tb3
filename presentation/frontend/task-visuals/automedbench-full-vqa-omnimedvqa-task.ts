import sourceRaw from '../../task-explorer/automedbench-full-vqa-omnimedvqa-task/source.json?raw';
import referenceRaw from '../../task-explorer/automedbench-full-vqa-omnimedvqa-task/reference.json?raw';
import fixtureRaw from '../../task-explorer/automedbench-full-vqa-omnimedvqa-task/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  source_question: {
    question_id: string;
    question: string;
    image_path: string;
    option_A: string;
    option_B: string;
    option_C: string;
    option_D: string;
    modality_type: string;
  };
  notice: { label: string; text: string; url: string; link_label: string };
};
export const reference = JSON.parse(referenceRaw) as {
  answer: string;
  label: string;
  role: string;
};
export const fixture = JSON.parse(fixtureRaw) as {
  raw_examples: string[];
  parsed_examples: (string | null)[];
  actual_prediction: null;
  actual_reference: null;
};
export const automedOmniPack = { source };
export type AutomedOmniState = Extract<StoryState, { recipe: 'automed-omni-v1' }>;
export const steps = ['Bind image + options', 'Parser controls', 'Answer schema'] as const;
export const branches = ['Standalone A', 'Reject E', 'Reject miss'] as const;
export function operationIndex(s: AutomedOmniState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: AutomedOmniState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'automed-omni-v1') throw new Error('OmniMedVQA recipe mismatch');
  if (!Number.isInteger(i) || i < 0 || i > 2 || !Number.isInteger(o) || o < 0 || o > 2)
    throw new RangeError('Invalid OmniMedVQA step/branch');
  const b = p.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - Math.round(i) / 2) < 1e-6,
  );
  if (!b) throw new Error('Missing operation beat');
  if (i !== 1) return b.startFrame;
  const t = Math.min(2, Math.max(0, Math.round(o))) / 2;
  let best = 0,
    d = Infinity;
  for (let k = 0; k < b.frames; k++) {
    const u = k / Math.max(1, b.frames - 1),
      z = u * u * (3 - 2 * u),
      v = Math.abs(z - t);
    if (v < d) {
      d = v;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: AutomedOmniState, readerRevealed = false) {
  return s.scene === 'reference' && s.reference > 0 && readerRevealed;
}
export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}
