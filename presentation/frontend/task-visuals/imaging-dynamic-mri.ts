import sourceRaw from '../../task-explorer/imaging101-mri-dynamic-dce/source.json?raw';
import measurementRaw from '../../task-explorer/imaging101-mri-dynamic-dce/measurement.json?raw';
import helperRaw from '../../task-explorer/imaging101-mri-dynamic-dce/helper.json?raw';
import operationRaw from '../../task-explorer/imaging101-mri-dynamic-dce/operation.json?raw';
import outputRaw from '../../task-explorer/imaging101-mri-dynamic-dce/output.json?raw';
import type { StoryState } from './story-timeline';
import type { DynamicMethod } from './imaging-dynamic-mri-controls';
export type ImagingDynamicMriState = Extract<StoryState, { recipe: 'imaging-dynamic-mri-v1' }>;
const packedMeasurement = JSON.parse(measurementRaw) as {
  mask_encoding: string;
  mask_bits_base64: string;
  sample_counts: number[];
  time_seconds: number[];
  native_kspace_center_64_64: number[][];
};
export function decodeDynamicMasks(encoding: string, encoded: string): string[][] {
  if (encoding !== 'base64-lsb0-frame-row-column') throw new Error('Unknown native mask encoding');
  const bytes = atob(encoded);
  if (bytes.length !== 40960) throw new Error('Wrong native mask byte count');
  return Array.from({ length: 20 }, (_, frame) =>
    Array.from({ length: 128 }, (_, row) =>
      Array.from({ length: 128 }, (_, column) => {
        const index = frame * 16384 + row * 128 + column;
        return String((bytes.charCodeAt(Math.floor(index / 8)) >>> (index % 8)) & 1);
      }).join(''),
    ),
  );
}
export const imagingDynamicMriPack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    geometry: string;
    sampling: string;
    time: string;
    noise: string;
  },
  measurement: {
    ...packedMeasurement,
    mask_rows: decodeDynamicMasks(
      packedMeasurement.mask_encoding,
      packedMeasurement.mask_bits_base64,
    ),
  },
  helper: JSON.parse(helperRaw) as {
    source_pixel_series: number[];
    truth_role: string;
    tiers: Record<'L1' | 'L2' | 'L3', string>;
  },
  operation: JSON.parse(operationRaw) as {
    steps: string[];
    methods: Record<DynamicMethod, string>;
    axes: string;
    limits: string;
  },
  output: JSON.parse(outputRaw) as {
    prediction: null;
    map: null;
    path: string;
    format: string;
    metric: string;
    task_metric: string;
    scorer_route: string;
    threshold: string;
    limits: string;
  },
};

export const dynamicSteps = [
  'Measurement axes',
  'Masked consistency',
  'Temporal neighbors',
  'Magnitude artifact',
] as const;
export const dynamicMethods = ['zero_filled', 'temporal_tv', 'prox'] as const;
export function operationIndex(state: ImagingDynamicMriState) {
  return Math.max(0, Math.min(3, Math.round(state.progress * 3)));
}
export function methodIndex(state: ImagingDynamicMriState) {
  return Math.max(0, Math.min(2, Math.round(state.detail * 2)));
}
export function operationFrame(
  plan: import('../contracts.generated').StoryPlan,
  step: number,
  method = 1,
) {
  if (
    !Number.isInteger(step) ||
    step < 0 ||
    step > 3 ||
    !Number.isInteger(method) ||
    method < 0 ||
    method > 2
  )
    throw new RangeError('Invalid dynamic MRI step/method');
  if (plan.recipe !== 'imaging-dynamic-mri-v1') throw new Error('Wrong dynamic MRI recipe');
  const beat = plan.beats.find(
    (b) =>
      b.scene === 'operation' &&
      Math.abs(b.channels.progress[0] - step / 3) < 1e-9 &&
      b.channels.progress[0] === b.channels.progress[1],
  );
  if (!beat) throw new Error('Missing canonical dynamic MRI operation beat');
  let best = 0,
    distance = Infinity;
  for (let k = 0; k < beat.frames; k++) {
    const u = k / Math.max(1, beat.frames - 1),
      ease = u * u * (3 - 2 * u),
      v = beat.channels.detail[0] + (beat.channels.detail[1] - beat.channels.detail[0]) * ease,
      d = Math.abs(v - method / 2);
    if (d < distance - 1e-12) {
      best = k;
      distance = d;
    }
  }
  return beat.startFrame + best;
}
