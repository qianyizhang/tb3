import type { StoryPlan } from '../types';
/** Absolute integer frames; no previous state, playing flag or clock dependence. */
export function sampleStory(plan: StoryPlan, requested: number) {
  if (!Number.isSafeInteger(requested)) throw new RangeError('Expected integer story frame');
  const frame = Math.max(0, Math.min(plan.durationFrames - 1, requested));
  const index = plan.beats.findIndex((b) => frame >= b.startFrame && frame < b.endFrame);
  if (index < 0) throw new Error('Timeline contains a gap');
  const beat = plan.beats[index];
  const progress = (frame - beat.startFrame) / Math.max(1, beat.endFrame - beat.startFrame - 1);
  const eased = progress * progress * (3 - 2 * progress);
  const channel = (pair: readonly number[]) => pair[0] + (pair[1] - pair[0]) * eased;
  // Return only scalar/copy fields; never expose mutable plan arrays.
  return Object.freeze({
    frame,
    index,
    beatId: beat.id,
    caption: beat.caption,
    narration: beat.narration,
    context: channel(beat.context),
    route: channel(beat.route),
    ribbon: channel(beat.ribbon),
    cursor: channel(beat.cursor),
    unfold: channel(beat.unfold),
    output: channel(beat.output),
  });
}
export type StoryState = ReturnType<typeof sampleStory>;
