import upstreamImage from '../../task-explorer/automedbench-full-ixi-t1-sr-task/upstream-t1-slice.png';
import sourceRaw from '../../task-explorer/automedbench-full-ixi-t1-sr-task/source.json?raw';
import referenceRaw from '../../task-explorer/automedbench-full-ixi-t1-sr-task/reference.json?raw';
import fixtureRaw from '../../task-explorer/automedbench-full-ixi-t1-sr-task/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
  symbolic_display: {
    native_image: null;
    low_cells: number;
    high_cells: number;
    no_resizing_or_model: boolean;
  };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  clean_image: null;
  criteria: string[];
};
export const fixture = JSON.parse(fixtureRaw) as {
  branches: number[];
  low_grid: number[][];
  high_values: null;
  actual_output: null;
  clean_reference: null;
};
export const automedIxiT1SrPack = { source };
export type AutomedIxiT1SrState = Extract<
  StoryState,
  { recipe: 'automedbench-full-ixi-t1-sr-task-v1' }
>;
export const steps = ['Public input / private target', 'Help + format', '2× geometry'] as const;
export const branches = ['Full Lite', 'Full Standard', 'Format boundary'] as const;
export function operationIndex(s: AutomedIxiT1SrState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: AutomedIxiT1SrState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (!Number.isInteger(i) || i < 0 || i > 2 || !Number.isInteger(o) || o < 0 || o > 2)
    throw new Error('Invalid IXI control');
  if (p.recipe !== 'automedbench-full-ixi-t1-sr-task-v1') throw new Error('IXI SR recipe mismatch');
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
    if (v < d - 1e-12) {
      d = v;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: AutomedIxiT1SrState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}
export function resetReader(previous: number, next: number, scene: string) {
  return next < previous || scene !== 'reference';
}

export const upstreamSourceImage = upstreamImage;
