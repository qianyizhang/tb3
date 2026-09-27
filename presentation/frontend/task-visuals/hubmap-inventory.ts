import source from '../../task-explorer/hubmap-inventory/source.json?raw';
import detail from '../../task-explorer/hubmap-inventory/detail.json?raw';
import tiles from '../../task-explorer/hubmap-inventory/tiles.json?raw';
import reference from '../../task-explorer/hubmap-inventory/reference.json?raw';
import helpers from '../../task-explorer/hubmap-inventory/helpers.json?raw';
import type { StoryState } from './story-timeline';

export type HubmapState = Extract<StoryState, { recipe: 'hubmap-inventory-v1' }>;
export type XY = [number, number];
export type Bounds = [number, number, number, number];
export interface SlideView {
  bounds_level0: Bounds;
  raster_size: XY;
  image: string;
}
export interface Glomerulus {
  id: string;
  source_index: number;
  source_id: string;
  ring: XY[];
  center_level0: XY;
  area_px2: number;
  area_um2: number;
}
export const hubmapSource = JSON.parse(source) as {
  sample: string;
  size_level0: XY;
  mpp: number;
  overview: SlideView;
};
export const hubmapDetail = JSON.parse(detail) as SlideView;
export const hubmapTiles = JSON.parse(tiles) as SlideView[];
export const hubmapRef = JSON.parse(reference) as {
  objects: Glomerulus[];
  source_object_count: number;
  duplicate: { local_centers: XY[]; unique_objects: number; view_records: number };
};
export const hubmapHelpers = JSON.parse(helpers) as {
  features: {
    properties: { classification: { name: 'Cortex' | 'Medulla' } };
    geometry:
      { type: 'Polygon'; coordinates: XY[][] } | { type: 'MultiPolygon'; coordinates: XY[][][] };
  }[];
};
export const hubmapReveal = (s: HubmapState) => s.reference > 0.5;
/** Native level-0 extents, not rounded overview raster dimensions, set display aspect. */
export function slideFit(p: SlideView, width: number, height: number) {
  const scale = Math.min(width / p.bounds_level0[2], height / p.bounds_level0[3]);
  return { width: scale * p.bounds_level0[2], height: scale * p.bounds_level0[3], scale };
}
export const toLocal = (point: XY, bounds: Bounds): XY => [
  point[0] - bounds[0],
  point[1] - bounds[1],
];
export const toLevel0 = (point: XY, bounds: Bounds): XY => [
  point[0] + bounds[0],
  point[1] + bounds[1],
];
export function ringPath(rings: XY[][], bounds: Bounds) {
  return rings
    .map((ring) => 'M' + ring.map((point) => toLocal(point, bounds).join(',')).join('L') + 'Z')
    .join(' ');
}
export const profileArea = (px2: number) => px2 * hubmapSource.mpp ** 2;
export const hubmapRows = (view: number) =>
  Math.min(5, 1 + Math.floor(Math.max(0, Math.min(1, view)) * 5));
