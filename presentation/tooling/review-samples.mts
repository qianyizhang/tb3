/** Exact canonical witnesses. Ordinary explorer navigation uses its own UX policy. */
export interface ReviewSample {
  beatId: string;
  frame: number;
  phase: 'start' | 'middle' | 'end';
}

export interface ReviewCapture {
  surface: 'explainer-export' | 'explorer';
  storyId: string | null;
  sourceSha256: string | null;
  planSha256: string | null;
  entryScope: string[];
  beatId: string | null;
  requestedFrame: number | null;
  committedFrame: number | null;
  phase: ReviewSample['phase'] | 'displayed';
  renderer: string;
  viewport: { width: number; height: number };
  file: string;
}

export function reviewSamples(
  plan: {
    durationFrames: number;
    beats: readonly { id: string; startFrame: number; endFrame: number }[];
  },
  { motion = false } = {},
): ReviewSample[] {
  if (!plan.beats.length) throw new RangeError('Review needs at least one beat');
  const samples: ReviewSample[] = [];
  let next = 0;
  const ids = new Set<string>();
  for (const beat of plan.beats) {
    if (
      !Number.isSafeInteger(beat.startFrame) ||
      !Number.isSafeInteger(beat.endFrame) ||
      beat.startFrame !== next ||
      beat.endFrame <= beat.startFrame ||
      ids.has(beat.id)
    )
      throw new RangeError('Review requires unique beats and contiguous half-open intervals');
    ids.add(beat.id);
    const seen = new Set<number>();
    const add = (frame: number, phase: ReviewSample['phase']) => {
      if (!seen.has(frame)) samples.push({ beatId: beat.id, frame, phase });
      seen.add(frame);
    };
    if (next === 0) add(0, 'start');
    // Prefer the endpoint when short beats collapse middle/end to the same frame.
    const middle = Math.floor((beat.startFrame + beat.endFrame - 1) / 2);
    if (motion && middle < beat.endFrame - 1) add(middle, 'middle');
    add(beat.endFrame - 1, 'end');
    next = beat.endFrame;
  }
  if (next !== plan.durationFrames) throw new RangeError('Review duration differs from timeline');
  return samples;
}
