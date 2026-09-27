import case004 from '../../task-explorer/topbrain-screen/case-004.json?raw';
import case006 from '../../task-explorer/topbrain-screen/case-006.json?raw';
import case007 from '../../task-explorer/topbrain-screen/case-007.json?raw';
import case011 from '../../task-explorer/topbrain-screen/case-011.json?raw';
import case012 from '../../task-explorer/topbrain-screen/case-012.json?raw';
import reference from '../../task-explorer/topbrain-screen/reference.json?raw';
import output from '../../task-explorer/topbrain-screen/output.json?raw';
import type { StoryState } from './story-timeline';

export type TopbrainState = Extract<StoryState, { recipe: 'topbrain-screen-v1' }>;
export interface BrainPlane {
  kind: string;
  axis: number;
  index: number | null;
  origin_ijk: number[];
  end_ijk_exclusive: number[];
  width: number;
  height: number;
  pixel_spacing_mm: number[];
  origin_ras_mm: number[];
  dx_ras_mm: number[];
  dy_ras_mm: number[];
  window: number[];
  image: string;
  prediction: string;
  added?: string;
}
interface Calibration {
  overview: BrainPlane & { route_native_ijk: number[][]; anchors_native_ijk: number[][] };
  gap_sections: BrainPlane[];
  cpr: { angle: number; width: number; height: number; png: string; raw_rows_png: string }[];
  arc_mm: number[];
  offsets_mm: number[];
  cpr_window: number[];
  cpr_display_extent_mm: number[];
  changes_native_ijk: number[][];
}
export interface BrainCase {
  id: string;
  shape: number[];
  affine_ras_mm: number[][];
  overview: BrainPlane;
  contacts?: BrainPlane[];
  contact_labels?: number[];
  variant?: BrainPlane;
  parent?: BrainPlane;
  calibration?: Calibration;
}
interface Branch {
  voxels: number;
  parent_connected_voxels: number;
  fraction: number | null;
}
interface Attachment {
  chain: number[];
  components_26: number;
  branches: Record<string, Branch>;
}
export interface BrainReference {
  overview: string;
  metrics: {
    name: string;
    label: number;
    reference_voxels: number;
    prediction_voxels: number;
    dice: number;
  }[];
  mean_present_label_dice: number;
  contacts?: string[];
  contact_metrics?: Record<
    'prediction' | 'reference',
    { contact_voxels_6: number; contact_voxels_26: number }
  >;
  variant?: string;
  variant_metrics?: Record<'prediction' | 'reference', Attachment>;
  parent?: string;
  parent_detached?: string;
  parent_metrics?: Attachment;
  calibration?: {
    overview: string;
    gap_sections: string[];
    checks: {
      changed_voxels_native_ijk: number[][];
      added_reference_labels: Record<string, number>;
      connected_before_after: boolean[];
      route_length_mm: number;
      route_p95_mm: number;
      route_max_mm: number;
      cpr_samples: number;
      cpr_max_signal_error: number;
      mesh_components: number;
      mesh_watertight: boolean;
    };
  };
}
export const brainCases = [case004, case006, case007, case011, case012].map(
  (raw) => JSON.parse(raw) as BrainCase,
);
export const brainRefs = (JSON.parse(reference) as { cases: Record<string, BrainReference> }).cases;
export const brainResult = JSON.parse(output) as {
  segmentation_predictions: number;
  hard_cases_admitted: number;
  coding_agent_trials: number;
  new_task_frozen: boolean;
  dispositions: { id: string; status: string; reason: string }[];
};
export const brainReveal = (s: TopbrainState) => s.reference > 0.5;
export const brainOutput = (s: TopbrainState) => s.output > 0.5;
export const brainIndex = (v: number, count: number) =>
  Math.round(Math.max(0, Math.min(1, v)) * (count - 1));
export function brainSelection(s: TopbrainState) {
  if (s.scene === 'variants') return { case: brainCases[[1, 3][brainIndex(s.view, 2)]], plane: 0 };
  if (s.scene === 'contacts') {
    const index = brainIndex(s.view, 9);
    return { case: brainCases[[0, 2, 3][Math.floor(index / 3)]], plane: index % 3 };
  }
  if (s.scene === 'parent') return { case: brainCases[2], plane: 0 };
  if (['calibration', 'cpr'].includes(s.scene))
    return { case: brainCases[0], plane: brainIndex(s.view, s.scene === 'cpr' ? 8 : 5) };
  return { case: brainCases[brainIndex(s.view, 5)], plane: 0 };
}
/** One uniform millimetre scale for both pixel axes; native anisotropy stays visible. */
export function brainPlaneFit(p: BrainPlane, width: number, height: number) {
  const w = p.width * p.pixel_spacing_mm[0],
    h = p.height * p.pixel_spacing_mm[1];
  const scale = Math.min(width / w, height / h);
  return { width: w * scale, height: h * scale };
}
/** Native image pixel centres, with depth collapsed only for the named MIP axis. */
export function brainPixel(p: BrainPlane, ijk: number[]) {
  const dims = [0, 1, 2].filter((a) => a !== p.axis);
  return [ijk[dims[0]] - p.origin_ijk[dims[0]], p.end_ijk_exclusive[dims[1]] - 1 - ijk[dims[1]]];
}
