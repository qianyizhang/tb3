import type { StoryPlan } from '../contracts.generated';
export type SosMethod = 'fbp' | 'sart' | 'tv';
export function canonicalMethod(s: string): SosMethod | null {
  return s === 'fbp' || s === 'sart' || s === 'tv' ? s : null;
}
export function nativeAngle(i: number): number | null {
  return Number.isInteger(i) && i >= 0 && i < 60 ? i : null;
}
export function signedSlowness(c: number): number | null {
  return Number.isFinite(c) && c > 0 ? 1 / c - 1 / 1500 : null;
}
export function resetOnBackward(prev: number, next: number): boolean {
  return next < prev;
}
export function operationIndex(progress: number): number {
  return Math.min(2, Math.max(0, Math.round(progress * 2)));
}
export function branchIndex(detail: number): number {
  return Math.min(2, Math.max(0, Math.round(detail * 2)));
}
export function operationFrame(plan: StoryPlan, index: number, branch = 0): number {
  if (plan.recipe !== 'imaging-ultrasound-sos-v1') throw new Error('Recipe mismatch');
  if (
    !Number.isInteger(index) ||
    index < 0 ||
    index > 2 ||
    !Number.isInteger(branch) ||
    branch < 0 ||
    branch > 2
  )
    throw new Error('Invalid step or branch');
  const b = plan.beats.find((b) => b.scene === 'operation' && b.channels.progress[0] === index / 2);
  if (!b) throw new Error('Operation absent');
  if (index !== 1) return b.startFrame;
  const target = branch / 2;
  let best = 0;
  let distance = Infinity;
  for (let k = 0; k < b.frames; k++) {
    const u = k / Math.max(1, b.frames - 1);
    const p = u * u * (3 - 2 * u);
    const d = Math.abs(p - target);
    if (d < distance - 1e-12) {
      distance = d;
      best = k;
    }
  }
  return b.startFrame + best;
}
