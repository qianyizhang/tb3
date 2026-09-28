import inputJson from '../../task-explorer/imaging101-deflectometry/inputs.json?raw';
import contractJson from '../../task-explorer/imaging101-deflectometry/contract.json?raw';
import referenceJson from '../../task-explorer/imaging101-deflectometry/reference.json?raw';
import type { StoryState } from './story-timeline';
export type DeflectometryState = Extract<StoryState, { recipe: 'imaging101-deflectometry-v1' }>;
export type DeflectometryImage = { data: string; shape: [number, number] };
export type LensProfile = {
  r: number[];
  front: number[];
  back: number[];
  curvatures: [number, number];
  thickness: number;
};
export type PhaseProbe = {
  axis: string;
  camera: number;
  row: number;
  column: number;
  frames: DeflectometryImage[];
  values: number[];
  mean: number;
  squared_modulation: number;
  phase: number;
  delta: [number, number];
  phase_image: DeflectometryImage;
};
export const deflectometryInput = JSON.parse(inputJson) as {
  measurements: DeflectometryImage[];
  fixture_probes: PhaseProbe[];
  raw_available: boolean;
};
export const deflectometryData = JSON.parse(contractJson) as {
  modeled: { initial: DeflectometryImage[]; saved: DeflectometryImage[] };
  initial_profile: LensProfile;
  saved_profile: LensProfile;
  saved_parameters: {
    surface_0_c: number;
    surface_1_c: number;
    surface_1_d: number;
    origin: number[];
    theta_x: number;
    theta_y: number;
  };
  saved_metrics: Record<string, number>;
  loss: { values: number[] };
  custom_score: { ncc: number; nrmse: number };
  pose_control: {
    score: { ncc: number; nrmse: number };
    output_pose: { origin: number[]; theta_x: number; theta_y: number };
  };
  generic_scoring: Record<string, { error?: string; nrmse?: string; passed?: boolean | null }>;
  staging: Record<string, string[]>;
};
export const deflectometryReference = JSON.parse(referenceJson) as {
  manufacturer_parameters_mm: number[];
  relative_errors: number[];
  profile: LensProfile;
  solver_visible_all_levels: boolean;
  pose_truth_available: boolean;
};
export const deflectometryIndex = (s: DeflectometryState, count: number) =>
  Math.min(count - 1, Math.floor(s.view * count));
export const deflectometryReveal = (s: DeflectometryState) =>
  s.scene === 'reference' && s.reference > 0.5;
export const deflectometryPhase = (v: number[]) => Math.atan2(v[3] - v[1], v[0] - v[2]);
export const deflectometrySag = (c: number, r: number) =>
  (c * r * r) / (1 + Math.sqrt(1 - c * c * r * r));
