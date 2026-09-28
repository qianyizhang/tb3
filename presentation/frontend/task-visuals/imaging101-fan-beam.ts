import inputs from '../../task-explorer/imaging101-fan-beam/inputs.json?raw';
import contract from '../../task-explorer/imaging101-fan-beam/contract.json?raw';
import reference from '../../task-explorer/imaging101-fan-beam/reference.json?raw';
import type { StoryState } from './story-timeline';
export type FanBeamState = Extract<StoryState, { recipe: 'imaging101-fan-beam-v1' }>;
export type FanBeamImage = { data: string; shape: [number, number]; range: [number, number] };
export const fanBeamInput = JSON.parse(inputs) as {
  sinograms: FanBeamImage[];
  angles_degrees: number[][];
  detector_positions: number[];
  geometry: {
    detector_spacing: number;
    detector_center_range: number[];
    declared_half_fan_degrees: number;
    geometric_half_fan_degrees: number;
    declared_sweep_degrees: number;
  };
};
export const fanBeamData = JSON.parse(contract) as {
  maps: FanBeamImage[];
  normalized_maps: FanBeamImage[];
  names: string[];
  keys: string[];
  weights: FanBeamImage;
  weight_curves: {
    selected_curves: number[][];
    selected_detector_bins: number[];
    angles_degrees: number[];
  };
  pixel_controls: {
    row: number;
    column: number;
    angle_degrees: number;
    U: number;
    magnification: number;
    detector_coordinate: number;
    bins: number[];
    weights: number[];
  }[];
  native: Record<string, { ncc: number; nrmse: number }>;
  generic: Record<string, { ncc?: number; nrmse?: number; error?: string }>;
  loss: { values: number[]; increasing_steps: number; first: number; last: number };
  staging: Record<string, string[]>;
  adjoint: { inner_Ax_y: number; inner_x_By: number; relative_error: number };
  prox: { output_norm: number; declared_ball_radius: number };
};
export const fanBeamReference = JSON.parse(reference) as {
  map: FanBeamImage;
  normalized_map: FanBeamImage;
  solver_visible_all_levels: boolean;
};
export const fanBeamIndex = (s: FanBeamState, count = 3) =>
  Math.min(count - 1, Math.floor(s.view * count));
export const fanBeamReveal = (s: FanBeamState) => s.scene === 'reference' && s.reference > 0.5;
export function fanBeamProject(row: number, column: number, degrees: number) {
  const beta = (degrees * Math.PI) / 180,
    x = column - 63.5,
    y = row - 63.5;
  const t = x * Math.cos(beta) + y * Math.sin(beta),
    u = 256 + x * Math.sin(beta) - y * Math.cos(beta);
  const magnification = 512 / u,
    detector = t * magnification;
  const index =
    (detector - fanBeamInput.geometry.detector_center_range[0]) /
    fanBeamInput.geometry.detector_spacing;
  const lo = Math.floor(index),
    fraction = index - lo;
  return {
    u,
    magnification,
    detector,
    bins: [lo, lo + 1],
    weights: [(1 - fraction) * magnification, fraction * magnification],
  };
}
