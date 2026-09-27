import source from '../../task-explorer/longitudinal-mri/source.json?raw';
import p02 from '../../task-explorer/longitudinal-mri/p02.json?raw';
import p03 from '../../task-explorer/longitudinal-mri/p03.json?raw';
import reference from '../../task-explorer/longitudinal-mri/reference.json?raw';
import type { StoryState } from './story-timeline';
export type MriState = Extract<StoryState, { recipe: 'longitudinal-mri-v1' }>;
export type XYZ = [number, number, number];
interface InputView {
  id: string;
  visit: string;
  day: number;
  shape: number[];
  phase: number;
  k: number;
  image: string;
  voxel_sizes_mm: XYZ;
  affine_ras_mm: number[][];
}
export const mriSource = JSON.parse(source) as {
  overview: { case: string; visits: InputView[] }[];
  cases: { case: string; volumes: number; frames: number; days: number[] }[];
};
export const mriP02 = JSON.parse(p02) as {
  visits: {
    visit: string;
    series: string;
    center: XYZ;
    spacing_mm: XYZ;
    phases: { phase: number; offset_s: number; image: string }[];
    t2: { series: string; center: XYZ; image: string };
  }[];
  citation: {
    visit: string;
    series_id: string;
    phase: number;
    voxel: XYZ;
    ras_mm: XYZ;
    image: string;
  };
};
export interface MriMethodView {
  visit: string;
  series: string;
  phase: number;
  k: number;
  image: string;
  bounds: [number, number, number, number];
  spacing_mm: XYZ;
  bbox_native_min: XYZ;
  bbox_native_max: XYZ;
  bbox_mm: XYZ;
  diameter_mm: number;
  reported_mm: number;
  method: {
    post_phase: number;
    threshold_fraction: number;
    gaussian_sigma_voxels: number;
    bbox_convention: string;
  };
}
export const mriP03 = JSON.parse(p03) as {
  methods: { condition: string; visits: MriMethodView[]; change_percent: number }[];
};
export const mriRef = JSON.parse(reference) as {
  cases: {
    case: string;
    ftv_cc: number[];
    diameter_raw: number[];
    ftv_change_percent: number;
    diameter_change_percent: number;
    pCR: number;
  }[];
  answers: {
    condition: string;
    contract_reward: number;
    clinical_pass: boolean | null;
    assessment: {
      comparison: {
        size_measurements_mm: {
          visit: string;
          longest_diameter_mm: number | null;
          method: string;
        }[];
      };
      impression: { confidence: number; leading_explanation: string; limitations: string[] };
      forecast: {
        next_exam_extent: string;
        confidence: number;
        basis: string;
        assumptions: string[];
      };
    };
  }[];
  clinical_success_rate: null;
  mechanical_passes: number;
};
export const mriPhaseIndex = (view: number) => Math.min(3, Math.floor(Math.max(0, view) * 4));
export const mriShowReference = (s: MriState) => s.reference > 0.5;
export const mriShowOutput = (s: MriState) => s.output > 0.5;
export const percentChange = (first: number, second: number) =>
  first > 0 ? 100 * (second / first - 1) : null;
/** Display projection of the 3-D bounding box, not a slice segmentation. */
export function projectedMethodBox(v: MriMethodView) {
  const edge = v.method.bbox_convention === 'voxel edges' ? 1 : 0;
  const low = v.bbox_native_min,
    high = v.bbox_native_max;
  return {
    x: v.bounds[2] - 1 - (high[0] - v.bounds[0]) - edge / 2,
    y: v.bounds[3] - 1 - (high[1] - v.bounds[1]) - edge / 2,
    width: high[0] - low[0] + edge,
    height: high[1] - low[1] + edge,
  };
}
