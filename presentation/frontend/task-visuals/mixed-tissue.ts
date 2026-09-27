import raw from '../../task-explorer/mixed-tissue/fixture.json?raw';
import type { StoryState } from './story-timeline';

export type MixedTissueState = Extract<StoryState, { recipe: 'mixed-tissue-v1' }>;
export const mixedTissue = JSON.parse(raw) as {
  slices: {
    plane: string;
    size: number;
    right: string;
    down: string;
    pixel_center_origin_lps_mm: number[];
    pixel_dx_lps_mm: number[];
    pixel_dy_lps_mm: number[];
    witness_pixel: number[];
    paths: { host: string; donor: string; region: string; original_host: string };
    region_cells: string;
  }[];
  witness_lps_mm: number[];
  reference_volume_ml: number;
  remaining_pancreas_ml: number;
};
export function mixedTissueView(state: MixedTissueState) {
  return {
    slice: mixedTissue.slices[Math.min(2, Math.floor(state.plane * 3 + 1e-8))],
    referenceVisible: state.reference > 0,
    witnessVisible: state.witness > 0,
  };
}
