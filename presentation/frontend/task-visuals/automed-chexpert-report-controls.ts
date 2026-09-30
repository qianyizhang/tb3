import type { StoryPlan } from '../contracts.generated';
/** Pure teaching selectors; never execute a report scorer or model. */
export function operationIndex(progress: number) {
  return Math.min(3, Math.max(0, Math.round(progress * 3)));
}
export function operationFrame(plan: StoryPlan, index: number) {
  if (plan.recipe !== 'automed-chexpert-report-v1') throw new Error('CheXpert recipe mismatch');
  if (!Number.isInteger(index) || index < 0 || index > 3)
    throw new Error('Invalid operation index');
  const b = plan.beats.find((b) => b.scene === 'operation');
  if (!b) throw new Error('Missing canonical operation');
  let best = 0,
    error = Infinity;
  for (let j = 0; j < b.frames; j++) {
    const t = j / Math.max(1, b.frames - 1),
      v = t * t * (3 - 2 * t),
      e = Math.abs(v - index / 3);
    if (e < error) {
      best = j;
      error = e;
    }
  }
  return b.startFrame + best;
}
export function shouldResetControls(previous: number, current: number) {
  return current < previous;
}
export function reportSelector(mode: 'findings' | 'fallback') {
  return mode === 'findings'
    ? 'Nonempty Findings preferred'
    : 'Otherwise full stripped report; no separate Impression selector';
}
export const stageQuestions = [
  'S1 plan.md: record model variant, loader, processor/tokenizer, report prompt and exact model-card dependency versions.',
  'S2 setup: verify checkpoint and pinned runtime; respect CUDA_VISIBLE_DEVICES, OMP limits and DataLoader workers ≤ 2.',
  'S3 example guidance: one staged image; nonempty report.txt, ≥ 40 alphabetic characters and < 60 seconds per case. Guidance differs from the format checker’s 40 characters and ≥ 20 alphabetic requirement; no validation run is shown.',
  'S4/S5: generate and submit every discovered study to agent_outputs/<case_id>/report.txt; keep private reports/labels outside generation.',
] as const;
