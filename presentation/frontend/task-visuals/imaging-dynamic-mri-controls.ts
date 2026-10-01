export type DynamicMethod = 'zero_filled' | 'temporal_tv' | 'prox';
export function canonicalMethod(value: string): DynamicMethod | null {
  return value === 'zero_filled' || value === 'temporal_tv' || value === 'prox' ? value : null;
}
export function nativeFrame(index: number): number | null {
  return Number.isInteger(index) && index >= 0 && index < 20 ? index : null;
}
export function resetOnBackward(previous: number, current: number): boolean {
  return current < previous;
}

export function publicTruthVisible(scene: string, requested = false) {
  return scene === 'helper' && requested;
}
/** Independent unitless arithmetic, not native physiology or a source operator. */
export function toyTemporalDifferences(values: readonly number[]) {
  if (values.length < 2 || !values.every(Number.isFinite))
    throw new Error('Expected finite toy sequence');
  return values.slice(1).map((value, index) => value - values[index]);
}
