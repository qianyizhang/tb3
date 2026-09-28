import inputs from '../../task-explorer/imaging101-nlos/inputs.json?raw';
import contract from '../../task-explorer/imaging101-nlos/contract.json?raw';
import reference from '../../task-explorer/imaging101-nlos/reference.json?raw';
import type { StoryState } from './story-timeline';
export type NlosState = Extract<StoryState, { recipe: 'imaging101-nlos-v1' }>;
export type NlosImage = { data: string; shape: [number, number]; maximum: number };
export const nlosInputs = JSON.parse(inputs) as {
  wall: NlosImage;
  histograms: {
    y: number;
    x: number;
    tof_ps: number;
    shift_bins: number;
    raw: number[];
    aligned: number[];
  }[];
};
export const nlosContract = JSON.parse(contract) as {
  views: { id: string; label: string; axes: string[]; ranges: number[][]; image: NlosImage }[];
  stolt: {
    scale: number;
    probes: {
      kz: number;
      kx: number;
      ky: number;
      sample_kf: number;
      weight: number;
      sample_index: number;
    }[];
  };
};
export const nlosReference = JSON.parse(reference) as { front: NlosImage; equal_to_saved: boolean };
export const nlosIndex = (s: NlosState, count = 3) =>
  Math.min(count - 1, Math.floor(s.view * count));
export const nlosReveal = (s: NlosState) => s.scene === 'reference' && s.reference > 0.5;
