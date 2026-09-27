import geometry from '../../task-explorer/vessel-source/geometry.json?raw';
import reference from '../../task-explorer/vessel-source/reference.json?raw';
import output from '../../task-explorer/vessel-source/output.json?raw';
import type { StoryState } from './story-timeline';
export type VesselSourceState = Extract<StoryState, { recipe: 'vessel-source-v1' }>;
export interface VesselPlane {
  width: number;
  height: number;
  png: string;
}
export interface VesselCase {
  id: string;
  shape: number[];
  affine_ras_mm: number[][];
  spacing_mm: number[];
  roi_origin_ijk: number[];
  roi_size_ijk: number[];
  mip: VesselPlane;
  native: (VesselPlane & {
    k: number;
    origin_world_mm: number[];
    dx_world_mm: number[];
    dy_world_mm: number[];
  })[];
}
export interface VesselNode {
  id: number;
  ras_mm: number[];
  native_ijk: number[];
  foreground_distance_mm: number;
}
interface Pcom {
  label: number;
  voxel_count: number;
  components_26: number;
  touches_expected_parent_labels_26: Record<string, boolean>;
}
export const vesselCases = (JSON.parse(geometry) as { cases: VesselCase[] }).cases;
export const vesselReference = (
  JSON.parse(reference) as {
    cases: {
      id: string;
      mip_overlay: string;
      native_overlays: string[];
      pcoms: Record<'left' | 'right', Pcom>;
      edges: Record<string, number>;
      node_entries: VesselNode[];
      node_distances_mm: { median: number; p95: number; max: number };
    }[];
  }
).cases;
export const vesselResult = JSON.parse(output) as {
  source_candidates: { id: string; status: string }[];
  natural_faulty_prediction: null;
  admitted_defect_fixtures: number;
  local_model_trials: number;
  numeric_verifier_thresholds: string;
};
export const vesselReveal = (s: VesselSourceState) => s.reference > 0.5;
export const vesselOutput = (s: VesselSourceState) => (s.output > 0.5 ? vesselResult : null);
export const vesselSliceIndex = (scan: number) =>
  Math.round((vesselCases[1].native.length - 1) * Math.min(1, Math.max(0, scan)));
/** MIP pixels use native i right and j up. Depth is deliberately collapsed. */
export function vesselNodePixel(c: VesselCase, node: VesselNode) {
  return {
    u: node.native_ijk[0] - c.roi_origin_ijk[0],
    v: c.roi_origin_ijk[1] + c.roi_size_ijk[1] - 1 - node.native_ijk[1],
  };
}
export const vesselColors = {
  right: '#f49c30',
  left: '#27c4bc',
  other: '#5773df',
  node: '#f5e4a7',
};

/** Only nodes within the MIP's actual three-dimensional source box are drawn. */
export function vesselVisibleNodes(index: number) {
  const c = vesselCases[index];
  return vesselReference[index].node_entries.filter(
    (n, i, all) =>
      all.findIndex((m) => m.id === n.id) === i &&
      n.native_ijk.every(
        (v, axis) =>
          v >= c.roi_origin_ijk[axis] - 0.5 &&
          v < c.roi_origin_ijk[axis] + c.roi_size_ijk[axis] - 0.5,
      ),
  );
}
