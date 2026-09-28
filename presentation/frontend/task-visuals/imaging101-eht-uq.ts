import inputJson from '../../task-explorer/imaging101-eht-uq/inputs.json?raw';
import contractJson from '../../task-explorer/imaging101-eht-uq/contract.json?raw';
import referenceJson from '../../task-explorer/imaging101-eht-uq/reference.json?raw';
import type { StoryState } from './story-timeline';
export type EhtState = Extract<StoryState, { recipe: 'imaging101-eht-uq-v1' }>;
export type EhtImage = {
  data: string;
  shape: [number, number];
  range: [number, number];
  unit: string;
  palette: 'heat' | 'spread' | 'binary';
};
export type EhtWitness = {
  source_row: number;
  stations: string[];
  gains: [number, number][];
  edges: {
    from: number;
    to: number;
    visibility_index: number;
    vis: [number, number];
    weight: number;
  }[];
  observed: number;
};
export type EhtMetric = { ncc: number; nrmse: number; passed?: null; error?: string };
export const ehtInput = JSON.parse(inputJson) as {
  uv_Glambda: [number, number][];
  time_ids: number[];
  times: number[];
  phase_deg: number[];
  phase_sigma_deg: number[];
  log_amplitude: number[];
  log_amplitude_sigma: number[];
  witnesses: { phase: EhtWitness; amplitude: EhtWitness };
  current_prior: EhtImage;
  retained_prior: EhtImage;
  current_flux: number;
  retained_flux: number;
};
export const ehtData = JSON.parse(contractJson) as {
  samples: { source_row: number; image: EhtImage; flux: number }[];
  mean: EhtImage;
  std: EhtImage;
  sample_count: number;
  sample_file: string;
  pixel: { row: number; column: number; values: number[]; mean: number; std: number };
  native_metrics: EhtMetric & { calibration: number; mean_uncertainty: number };
  generic_metrics: Record<string, EhtMetric>;
  staging: Record<string, string[]>;
  alternate_samples: { mean_max_error_vs_saved: number; std_max_error_vs_saved: number };
  thresholds_available: boolean;
  solver_visible_all_levels: boolean;
};
export const ehtReference = JSON.parse(referenceJson) as {
  image: EhtImage;
  error: EhtImage;
  containment: EhtImage;
  within_std: number;
  total_pixels: number;
  pixel_truth: number;
  reference_flux: number;
};
export const ehtIndex = (s: EhtState, count: number) =>
  Math.min(count - 1, Math.floor(s.view * count));
export const ehtReveal = (s: EhtState) => s.scene === 'reference' && s.reference > 0.5;
export const ehtReferenceIndex = (s: EhtState) =>
  Math.min(1, Math.max(0, Math.floor((s.view - 0.5) * 4)));
export const ehtWrap = (v: number) => ((((v + 180) % 360) + 360) % 360) - 180;
/** Apply only multiplicative station gains to saved complex visibilities. */
export function ehtGainControl(w: EhtWitness, progress: number, kind: 'phase' | 'amplitude') {
  const g = w.gains.map(([re, im]) => ({
    amplitude: Math.hypot(re, im) ** progress,
    phase: Math.atan2(im, re) * progress,
  }));
  const edges = w.edges.map((e) => ({
    ...e,
    amplitude: Math.hypot(...e.vis) * g[e.from].amplitude * g[e.to].amplitude,
    phase: ehtWrap(
      ((Math.atan2(e.vis[1], e.vis[0]) + g[e.from].phase - g[e.to].phase) * 180) / Math.PI,
    ),
  }));
  const value =
    kind === 'phase'
      ? ehtWrap(edges.reduce((a, e) => a + e.phase, 0))
      : edges.reduce((a, e) => a + e.weight * Math.log(e.amplitude), 0);
  return { gains: g, edges, value };
}
