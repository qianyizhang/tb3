/** Contract controls only. Never interpret numeric checkpoint indices or create predictions. */
export function canonicalNamedClass(token: string, classes: readonly string[]): string | null {
  const named = token.trim().toLowerCase();
  return classes.includes(named) ? named : null;
}
export function submissionFields(format: 'csv' | 'json'): readonly string[] {
  return format === 'csv' ? ['patient_id', 'label'] : ['label'];
}
export function shouldResetControls(previous: number, current: number): boolean {
  return current < previous;
}
