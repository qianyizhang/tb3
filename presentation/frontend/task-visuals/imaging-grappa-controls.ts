export type GrappaMethod = 'calibration' | 'interpolation' | 'combination';
export function canonicalMethod(value: string): GrappaMethod | null {
  return value === 'calibration' || value === 'interpolation' || value === 'combination'
    ? value
    : null;
}
export function nativeCoil(index: number): number | null {
  return Number.isInteger(index) && index >= 0 && index < 8 ? index : null;
}
export function resetOnBackward(previous: number, current: number): boolean {
  return current < previous;
}
export function sourceTargetVisible(scene: string, requested: boolean): boolean {
  return scene === 'helper' && requested;
}
export function canonicalStep(progress: number): number {
  return Math.round(Math.max(0, Math.min(1, progress)) * 3);
}
export function operationFrame(
  plan: { beats: { scene: string; frames: number }[] },
  step: number,
): number | null {
  if (!Number.isInteger(step) || step < 0 || step > 3) return null;
  let offset = 0;
  for (const beat of plan.beats) {
    if (beat.scene === 'operation') {
      let nearest = 0,
        distance = Infinity;
      for (let k = 0; k < beat.frames; k++) {
        const u = k / Math.max(1, beat.frames - 1);
        const delta = Math.abs(u * u * (3 - 2 * u) - step / 3);
        if (delta < distance - 1e-12) {
          distance = delta;
          nearest = k;
        }
      }
      return offset + nearest;
    }
    offset += beat.frames;
  }
  return null;
}
