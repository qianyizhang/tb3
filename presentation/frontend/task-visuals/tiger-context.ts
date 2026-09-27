import source from '../../task-explorer/tiger-context/source.json?raw';
import roi1 from '../../task-explorer/tiger-context/roi1.json?raw';
import roi2 from '../../task-explorer/tiger-context/roi2.json?raw';
import roi3 from '../../task-explorer/tiger-context/roi3.json?raw';
import reference from '../../task-explorer/tiger-context/reference.json?raw';
import type { StoryState } from './story-timeline';
export type TigerState = Extract<StoryState, { recipe: 'tiger-context-v1' }>;
export type XY = [number, number];
export type Bounds = [number, number, number, number];
export interface TigerView {
  pilot_id: string;
  coco_id: number;
  bounds_level0: Bounds;
  image: string;
}
export interface TigerRow {
  code: number;
  cells: number;
  pixels: number;
  area_mm2: number;
  density_per_mm2: number | null;
}
export interface TigerCell {
  id: number;
  bbox: Bounds;
  center: XY;
  compartment: number;
}
export interface TigerReference {
  pilot_id: string;
  coco_id: number;
  bounds_level0: Bounds;
  cells: TigerCell[];
  rows: TigerRow[];
  merged_stroma: Omit<TigerRow, 'code'>;
  mask_overlay: string;
}
export const tigerSource = JSON.parse(source) as {
  sample: string;
  size_level0: XY;
  mpp: number;
  overview: string;
  detail: { bounds_roi: Bounds; image: string };
  boundary: { bounds_roi: Bounds; image: string };
};
export const tigerViews = [roi1, roi2, roi3].map((s) => JSON.parse(s) as TigerView);
export const tigerRef = JSON.parse(reference) as {
  rois: TigerReference[];
  palette: { code: number; label: string; color: string }[];
  total_cells: number;
  boundary: {
    center: XY;
    shifted: XY;
    distance_px: number;
    source_code: number;
    shifted_code: number;
  };
};
export const tigerReveal = (s: TigerState) => s.reference > 0.5;
export const tissueArea = (pixels: number) => (pixels * tigerSource.mpp ** 2) / 1e6;
export function pooledDensity(rows: Pick<TigerRow, 'cells' | 'area_mm2'>[]) {
  const area = rows.reduce((a, r) => a + r.area_mm2, 0);
  return area > 0 ? rows.reduce((a, r) => a + r.cells, 0) / area : null;
}
export const slidePoint = (p: XY, b: Bounds): XY => [p[0] + b[0], p[1] + b[1]];
export const selectedCells = (bounds: Bounds) =>
  tigerRef.rois[1].cells.filter(
    (c) =>
      c.center[0] >= bounds[0] &&
      c.center[0] < bounds[0] + bounds[2] &&
      c.center[1] >= bounds[1] &&
      c.center[1] < bounds[1] + bounds[3],
  );
