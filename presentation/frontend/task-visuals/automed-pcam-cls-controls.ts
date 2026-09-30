/** Named tokens and upstream dataset values are separate from checkpoint indices. */
export function canonicalNamedClass(token: string, classes: readonly string[]): string | null {
  const named = token.trim().toLowerCase();
  return classes.includes(named) ? named : null;
}
export function upstreamBinaryClass(value: number): 'negative' | 'positive' | null {
  return value === 0 ? 'negative' : value === 1 ? 'positive' : null;
}
export function submissionFields(format: 'csv' | 'json'): readonly string[] {
  return format === 'csv' ? ['patient_id', 'label'] : ['label'];
}
export function shouldResetControls(previous: number, current: number): boolean {
  return current < previous;
}
