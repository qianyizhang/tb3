import inputs from '../../task-explorer/imaging101-ptychography/inputs.json?raw';
import contract from '../../task-explorer/imaging101-ptychography/contract.json?raw';
import reference from '../../task-explorer/imaging101-ptychography/reference.json?raw';
import type { StoryState } from './story-timeline';
export type PtychographyState = Extract<StoryState, { recipe: 'imaging101-ptychography-v1' }>;
export type PtychographyImage = {
  data: string;
  shape: [number, number];
  range: [number, number];
  transform: string;
};
export const ptychographyInput = JSON.parse(inputs) as {
  positions: [number, number][];
  encoders: [number, number][];
  metadata: { dxp_m: number; dxd_m: number };
  samples: {
    scan: number;
    position_rc: [number, number];
    encoder_m: [number, number];
    measured: PtychographyImage;
    estimated: PtychographyImage;
    projected: PtychographyImage;
    before_relative_l1: number;
    after_relative_l1: number;
  }[];
};
export const ptychographyData = JSON.parse(contract) as {
  amplitude: PtychographyImage;
  phase: PtychographyImage;
  errors: number[];
  generic: Record<string, { ncc: number; nrmse: number | 'inf'; mse: number }>;
  native_phase: Record<string, { ncc: number; nrmse: number }>;
};
export const ptychographyReference = JSON.parse(reference) as {
  phase: PtychographyImage;
  amplitude: PtychographyImage;
  unit_magnitude: boolean;
};
export const ptychographyIndex = (s: PtychographyState, count = 3) =>
  Math.min(count - 1, Math.floor(s.view * count));
export const ptychographyReveal = (s: PtychographyState) =>
  s.scene === 'reference' && s.reference > 0.5;
export const ptychographyCorner = (encoder: readonly number[]) =>
  encoder.map((v) => Math.round(v / ptychographyInput.metadata.dxp_m) + 207);
