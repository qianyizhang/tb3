const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const g = await loadFrontend('../presentation/frontend/explainers/native/wsi-geometry.ts');
  const same = (a, b) => assert.deepEqual(Array.from(a), b);
  const raster = [12, 34, 100, 50],
    native = [2000, 3000, 6400, 3200];
  same(g.panelToLevel0([62, 59], raster, native), [5200, 4600]);
  same(g.level0ToPanel([5200, 4600], raster, native), [62, 59]);
  same(g.intersect([90, 40, 20, 20], [0, 0, 100, 50]), [90, 40, 10, 10]);
  assert.equal(g.paddedFraction([90, 40, 20, 20], [100, 50]), 0.75);
  same(g.panelToLevel0([100, 50], [0, 0, 200, 100], [90, 40, 20, 20]), [100, 50]);
  const fitted = g.fitBounds([0, 0, 100, 100], 2);
  same(fitted, [-50, 0, 200, 100]);
  const zoomed = g.zoomBounds(fitted, 2, [20, 30]);
  same(g.zoomBounds(zoomed, 0.5, [20, 30]), Array.from(fitted));
  same(g.panBounds(g.panBounds(fitted, 25, -10), -25, 10), Array.from(fitted));
  assert.equal(zoomed[2] / zoomed[3], 2);
  console.log('WSI geometry: exact panel mapping, padding, aspect, anchored zoom and pan passed.');
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
