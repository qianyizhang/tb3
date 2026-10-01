export type EitMethod = 'BP' | 'JAC' | 'GREIT';
export function canonicalMethod(value: string): EitMethod | null {
  return value === 'BP' || value === 'JAC' || value === 'GREIT' ? value : null;
}
export function measurementRow(index: number, count: number): number | null {
  return Number.isInteger(index) && index >= 0 && index < count ? index : null;
}
export function resetOnBackward(previous: number, current: number): boolean {
  return current < previous;
}

export function publicTruthVisible(scene: string, requested = false) {
  return scene === 'helper' && requested;
}
/** Authored unitless arithmetic only; no native forward/inverse solver. */
export function toyGaugeDifference(n: number, m: number, offset = 0) {
  if (![n, m, offset].every(Number.isFinite)) throw new Error('Expected finite toy values');
  return n + offset - (m + offset);
}
