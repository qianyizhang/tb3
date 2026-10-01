import type { StoryPlan } from '../contracts.generated';
import sourceRaw from '../../task-explorer/imaging101-eit-conductivity-reconstruction/source.json?raw';
import measurementRaw from '../../task-explorer/imaging101-eit-conductivity-reconstruction/measurement.json?raw';
import helperRaw from '../../task-explorer/imaging101-eit-conductivity-reconstruction/helper.json?raw';
import operationRaw from '../../task-explorer/imaging101-eit-conductivity-reconstruction/operation.json?raw';
import outputRaw from '../../task-explorer/imaging101-eit-conductivity-reconstruction/output.json?raw';
import type { StoryState } from './story-timeline';
import type { EitMethod } from './imaging-eit-controls';
export type ImagingEitState = Extract<StoryState, { recipe: 'imaging-eit-v1' }>;
export const imagingEitPack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    geometry: string;
    contact: string;
    voltage: string;
    protocol: string;
  },
  measurement: JSON.parse(measurementRaw) as {
    node: number[][];
    element: number[][];
    el_pos: number[];
    ref_node: number;
    v0: number[];
    v1: number[];
    ex_mat: number[][];
    meas_mat: number[][];
  },
  helper: JSON.parse(helperRaw) as {
    public_truth: Record<string, string>;
    public_truth_role: string;
    tiers: Record<'L1' | 'L2' | 'L3', string>;
  },
  operation: JSON.parse(operationRaw) as {
    steps: string[];
    linearization: string;
    methods: Record<
      EitMethod,
      { domain: string; normalize: string; inverse: string; path: string }
    >;
  },
  output: JSON.parse(outputRaw) as {
    path: string;
    generic: string;
    metric: string;
    task_metric: string;
    reference_selection: string;
    reference_summary: string;
    threshold: string;
    limits: string;
  },
};

export const eitSteps = [
  'Pair voltages',
  'Sign + gauge',
  'Inverse assumptions',
  'Output domain',
] as const;
export const eitMethods = ['BP', 'JAC', 'GREIT'] as const;
export function operationIndex(state: ImagingEitState) {
  return Math.min(3, Math.max(0, Math.round(state.progress * 3)));
}
export function methodIndex(state: ImagingEitState) {
  return Math.min(2, Math.max(0, Math.round(state.detail * 2)));
}
export function operationFrame(plan: StoryPlan, step: number, method = 0) {
  if (plan.recipe !== 'imaging-eit-v1') throw new Error('EIT recipe mismatch');
  if (
    !Number.isInteger(step) ||
    step < 0 ||
    step > 3 ||
    !Number.isInteger(method) ||
    method < 0 ||
    method > 2
  )
    throw new Error('Invalid EIT selection');
  const beat = plan.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - step / 3) < 1e-6,
  );
  if (!beat) throw new Error('Missing EIT operation beat');
  const target = method / 2;
  let best = 0,
    distance = Infinity;
  for (let k = 0; k < beat.frames; k++) {
    const t = k / Math.max(1, beat.frames - 1);
    const eased = t * t * (3 - 2 * t),
      delta = Math.abs(eased - target);
    if (delta < distance - 1e-12) {
      best = k;
      distance = delta;
    }
  }
  return beat.startFrame + best;
}
