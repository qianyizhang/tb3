import sourceRaw from '../../task-explorer/automedbench-full-vqa-kvasir-task/source.json?raw';
import referenceRaw from '../../task-explorer/automedbench-full-vqa-kvasir-task/reference.json?raw';
import fixtureRaw from '../../task-explorer/automedbench-full-vqa-kvasir-task/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  preview_data_uri: string;
  source_question: { id: string; question: string; images: string[] };
  notice: { label: string; text: string; url: string; link_label: string };
};
export const reference = JSON.parse(referenceRaw) as {
  answer: string;
  category: string;
  role: string;
};
export const fixture = JSON.parse(fixtureRaw) as {
  normalization: { raw: string; normalized: string };
  nonbinary: {
    reference: string;
    prediction: string;
    EM: number;
    token_F1: number;
    half_EM_plus_half_F1: number;
  };
  binary: { reference: string; prediction: string; strict_match: number };
};
export const automedKvasirPack = { source };
export type AutomedKvasirState = Extract<StoryState, { recipe: 'automed-kvasir-v1' }>;
export const steps = ['Question + image', 'Metric branches', 'Answer schema'] as const;
export const branches = ['Lexical score', 'Strict yes/no', 'Optional judge'] as const;
export function operationIndex(s: AutomedKvasirState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: AutomedKvasirState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (
    p.recipe !== 'automed-kvasir-v1' ||
    !Number.isInteger(i) ||
    i < 0 ||
    i > 2 ||
    !Number.isInteger(o) ||
    o < 0 ||
    o > 2
  )
    throw new Error('Kvasir-VQA recipe mismatch');
  const b = p.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - Math.round(i) / 2) < 1e-6,
  );
  if (!b) throw new Error('Missing operation beat');
  if (i !== 1) return b.startFrame;
  const t = Math.min(2, Math.max(0, Math.round(o))) / 2;
  let best = 0,
    d = Infinity;
  for (let k = 0; k < b.frames; k++) {
    const u = k / b.frames,
      z = u * u * (3 - 2 * u),
      v = Math.abs(z - t);
    if (v < d) {
      d = v;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: AutomedKvasirState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}

export function resetOnBackward(previous: number, next: number): boolean {
  return next < previous;
}
