import geometry from '../../task-explorer/airway-repair/geometry.json?raw';
import inputA from '../../task-explorer/airway-repair/mask-A01.json?raw';
import inputB from '../../task-explorer/airway-repair/mask-A02.json?raw';
import output from '../../task-explorer/airway-repair/output.json?raw';
import reference from '../../task-explorer/airway-repair/reference.json?raw';
import type { IndexedMesh } from './operation-fixtures';
import type { CTPlane } from './respiratory';
import type { StoryState } from './story-timeline';

export type AirwayState = Extract<StoryState, { recipe: 'airway-repair-v1' }>;
export type AirwaySection = CTPlane & {
  axis: number;
  index: number;
  proposed: string;
  editable: string;
};
export const airwayCases = JSON.parse(geometry) as {
  id: string;
  patient: string;
  shape: number[];
  affine_ras_mm: number[][];
  anchors: number[][];
  mesh_key: 'A01' | 'A02';
  sections: AirwaySection[];
}[];
export const airwayMasks = {
  A01: JSON.parse(inputA) as IndexedMesh,
  A02: JSON.parse(inputB) as IndexedMesh,
};
export const airwayOutput = JSON.parse(output) as {
  id: string;
  route: number[][];
  added_mesh: IndexedMesh;
  slice_added: string[];
  cpr: {
    angle_deg: number;
    png: string;
    arc_png: string;
    display_arc_mm: number[];
    width: number;
    height: number;
    arc_mm: number[];
    offsets_mm: number[];
    sampling_edges: number[][][];
  }[];
}[];
type Connectivity = {
  components: number;
  anchor_components: number[];
  anchor_component_voxels: number[];
  anchors_connected: boolean;
  anchors_in_largest_component: boolean[];
};
export const airwayReference = JSON.parse(reference) as {
  id: string;
  core_mesh: IndexedMesh;
  reference_path: number[][];
  slice_core: string[];
  metrics: { core_coverage: number; route_p95_mm: number; cpr_HU_p99_error: number };
  connectivity: { before: Connectivity; after: Connectivity; added: number; removed: number };
}[];
export const airwayColors = {
  input: '#7197a9',
  anchor: '#efa933',
  output: '#2bbba0',
  reference: '#e880ad',
};
export const airwayCaseIndex = (state: AirwayState) =>
  state.scene === 'controls' ? (state.view < 0.5 ? 1 : 2) : 0;
export const airwayReveal = (state: AirwayState) => state.reference > 0.5;
export const airwayReturned = (state: AirwayState) => state.output > 0.5;
export const airwaySliceIndex = (state: AirwayState) =>
  state.scene === 'inspect' ? Math.round(state.view * 8) : 4;
export const airwayAngleIndex = (state: AirwayState) =>
  state.scene === 'cpr' ? Math.min(7, Math.floor(state.view * 8)) : 0;
export const airwayRouteIndex = (state: AirwayState) =>
  Math.round(
    (state.scene === 'route' ? state.view : 0.5) *
      (airwayOutput[airwayCaseIndex(state)].route.length - 1),
  );
/** Proper rotations in physical RAS mm; one shared fit for every object in a case. */
export function airwayDisplay(point: readonly number[], index: number) {
  const [x, y, z] = point;
  const [a, b, c] = index === 1 ? [-x, -y, z] : [-y, z, -x];
  const angle = 0.16;
  return [Math.cos(angle) * a + Math.sin(angle) * c, b, -Math.sin(angle) * a + Math.cos(angle) * c];
}
const bounds = airwayCases.map((_, index) => {
  const key = airwayCases[index].mesh_key;
  // Include all retained sampling extents so changing angle cannot crop the ribbon.
  // Requests sharing a source crop share one fit, including before any output reveal.
  const points = [
    ...airwayMasks[key].vertices,
    ...airwayOutput
      .filter((_, i) => airwayCases[i].mesh_key === key)
      .flatMap((o) => o.cpr.flatMap((c) => c.sampling_edges.flat())),
  ].map((p) => airwayDisplay(p, index));
  return {
    low: [0, 1, 2].map((i) => Math.min(...points.map((p) => p[i]))),
    high: [0, 1, 2].map((i) => Math.max(...points.map((p) => p[i]))),
  };
});
export const airwayBounds = (index: number) => bounds[index];
export function airwayProject(point: readonly number[], index: number) {
  const { low, high } = airwayBounds(index),
    p = airwayDisplay(point, index);
  const scale = 315 / Math.max(high[0] - low[0], high[1] - low[1]);
  return [
    300 + (p[0] - (high[0] + low[0]) / 2) * scale,
    220 - (p[1] - (high[1] + low[1]) / 2) * scale,
  ];
}

/** Cell edges for the saved nonuniform arc samples; never assume row index is millimetres. */
export function airwayCPRRowEdges(arc: readonly number[]) {
  return [
    arc[0] - (arc[1] - arc[0]) / 2,
    ...arc.slice(1).map((v, i) => (v + arc[i]) / 2),
    arc[arc.length - 1] + (arc[arc.length - 1] - arc[arc.length - 2]) / 2,
  ];
}
