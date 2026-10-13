/** Level-0 geometry only; no dataset or private reference imports. */
export type XY = readonly [number, number];
export type Bounds = readonly [number, number, number, number];
export function intersect(a: Bounds, b: Bounds): Bounds {
  const x = Math.max(a[0], b[0]),
    y = Math.max(a[1], b[1]);
  return [
    x,
    y,
    Math.max(0, Math.min(a[0] + a[2], b[0] + b[2]) - x),
    Math.max(0, Math.min(a[1] + a[3], b[1] + b[3]) - y),
  ];
}
export function panelToLevel0(point: XY, raster: Bounds, native: Bounds): XY {
  return [
    native[0] + ((point[0] - raster[0]) * native[2]) / raster[2],
    native[1] + ((point[1] - raster[1]) * native[3]) / raster[3],
  ];
}
export function level0ToPanel(point: XY, raster: Bounds, native: Bounds): XY {
  return [
    raster[0] + ((point[0] - native[0]) * raster[2]) / native[2],
    raster[1] + ((point[1] - native[1]) * raster[3]) / native[3],
  ];
}
export function fitBounds(bounds: Bounds, aspect: number): Bounds {
  const width = Math.max(bounds[2], bounds[3] * aspect),
    height = width / aspect;
  return [bounds[0] + (bounds[2] - width) / 2, bounds[1] + (bounds[3] - height) / 2, width, height];
}
export function zoomBounds(
  view: Bounds,
  factor: number,
  anchor: XY = [view[0] + view[2] / 2, view[1] + view[3] / 2],
): Bounds {
  return [
    anchor[0] + (view[0] - anchor[0]) / factor,
    anchor[1] + (view[1] - anchor[1]) / factor,
    view[2] / factor,
    view[3] / factor,
  ];
}
export function panBounds(view: Bounds, dx: number, dy: number): Bounds {
  return [view[0] + dx, view[1] + dy, view[2], view[3]];
}
export function paddedFraction(bounds: Bounds, size: XY): number {
  const clipped = intersect(bounds, [0, 0, ...size]);
  return 1 - (clipped[2] * clipped[3]) / (bounds[2] * bounds[3]);
}
