import inputs from '../../task-explorer/rex-topcow/inputs.json?raw';
import reference from '../../task-explorer/rex-topcow/reference.json?raw';
import contract from '../../task-explorer/rex-topcow/contract.json?raw';
import type { StoryState } from './story-timeline';
export type RexState = Extract<StoryState, { recipe: 'rex-topcow-v1' }>;
export const rexInputs = JSON.parse(inputs) as {
  views: {
    z: number;
    width: number;
    height: number;
    png: string;
    pixel_index_to_native_ijk: number[][];
  }[];
};
export const rexReference = JSON.parse(reference) as {
  views: {
    z: number;
    png: string;
    crop_png: string;
    ct_crop_png: string;
    plane_counts: Record<string, number>;
  }[];
  structures: { id: number; name: string; color: string; voxels: number }[];
};
export type RexFixture = {
  id: string;
  dice: number;
  cldice: number;
  b0_error: number;
  anterior_topology: number;
  prediction_voxels: { ijk: number[]; label: number }[];
  reference_voxels: number[][];
};
export const rexContract = JSON.parse(contract) as {
  fixtures: RexFixture[];
  split: {
    train_ids: string[];
    test_ids: string[];
    public_label_012: boolean;
    private_label_012: boolean;
  };
  ranking: { positions: Record<string, number>; competitors: number };
};
export function rexSelection(s: RexState) {
  const count =
    s.scene === 'inputs' || s.scene === 'reference'
      ? 3
      : s.scene === 'metrics'
        ? 5
        : s.scene === 'labels'
          ? 13
          : s.scene === 'topology' || s.scene === 'geometry'
            ? 2
            : 1;
  const progress = s.scene === 'reference' ? Math.max(0, (s.view - 0.5) * 2) : s.view;
  return Math.min(count - 1, Math.floor(progress * count));
}
export function rexReveal(s: RexState) {
  return s.scene === 'reference' && s.reference > 0.5;
}
export function rexNativeIndex(x: number, y: number, z: number, crop = false) {
  return [crop ? 187 - x : 265 - x, crop ? y + 113 : y, z];
}
