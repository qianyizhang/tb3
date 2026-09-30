/** Contract selections only; no image processing or inference. */
export const abbreviations = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc'] as const;
export function canonicalCheckpointClass(index: number, mapping: Record<string, string>): string {
  if (!Number.isInteger(index) || index < 0 || index >= abbreviations.length)
    throw new Error('Invalid checkpoint class index');
  return mapping[abbreviations[index]];
}
export function processorView(
  mode: 'native' | 'processor',
  config: {
    size: { height: number; width: number };
    rescale_factor: number;
    image_mean: number[];
    image_std: number[];
  },
) {
  return mode === 'native'
    ? 'Native600×450 source display; no model tensor'
    : `RGB → ${config.size.width}×${config.size.height} resize → 1/255 → mean/std .5/.5; settings only`;
}
export function submissionFields(format: 'csv' | 'json') {
  return format === 'csv' ? ['patient_id', 'label'] : ['label'];
}
export function shouldResetControls(previous: number, current: number) {
  return current < previous;
}
