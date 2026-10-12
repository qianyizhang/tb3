const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const { rasPoint, bboxCells, cellSpans, boxEdges, planeCorners, nearestSample } =
    await loadFrontend('../presentation/frontend/explainers/native/mri-geometry.ts');
  const v1 = [
    [0.6640999913215637, 0, 0, -180.3939971923828],
    [0, 0.6640999913215637, 0, -138.53900146484375],
    [0, 0, 2, -105],
    [0, 0, 0, 1],
  ];
  const v2 = [
    [0.6445000171661377, 0, 0, -163.5989990234375],
    [0, 0.6445000171661377, 0, -150.72000122070312],
    [0, 0, 2, -116.1709976196289],
    [0, 0, 0, 1],
  ];
  const p1 = rasPoint(v1, [390, 270, 60]),
    p2 = rasPoint(v2, [386, 302, 64]);
  assert.ok(Math.abs(p1[0] - 78.605) < 0.001);
  assert.ok(Math.abs(p2[2] - 11.829002380371094) < 1e-8);
  assert.notEqual(rasPoint(v1, [390, 270, 60])[0], rasPoint(v2, [390, 270, 60])[0]);
  assert.ok(Math.abs(rasPoint(v1, [391, 270, 60])[0] - p1[0] - v1[0][0]) < 1e-8);
  assert.ok(Math.abs(rasPoint(v2, [386, 301, 64])[1] - p2[1] + v2[1][1]) < 1e-8);
  const b1 = bboxCells([376, 253, 54], [397, 284, 63]);
  const b2 = bboxCells([375, 285, 58], [391, 315, 67]);
  const s1 = cellSpans(b1, [v1[0][0], v1[1][1], 2]),
    s2 = cellSpans(b2, [v2[0][0], v2[1][1], 2]);
  assert.ok(Math.abs(Math.max(...s1) - 21.25119972229004) < 1e-8);
  assert.equal(Math.max(...s2), 20);
  assert.ok(s2[1] < s2[2]);
  const edges = boxEdges(b1);
  assert.equal(edges.length, 24);
  assert.equal(Math.min(...edges.map((p) => p[0])), 375.5);
  assert.equal(Math.max(...edges.map((p) => p[2])), 63.5);
  const plane = planeCorners(2, 60, [512, 512, 106]);
  assert.ok(plane.every((p) => p[2] === 60));
  assert.ok(
    Math.abs(rasPoint(v1, plane[1])[0] - rasPoint(v1, plane[0])[0] - 512 * v1[0][0]) < 1e-8,
  );
  const map = [0, 3, 9, 20, 105];
  assert.equal(nearestSample(map, 0), 0);
  assert.equal(nearestSample(map, 105), 4);
  assert.equal(nearestSample(map, 10), 2);
  assert.equal(nearestSample(map, 512), 4);
  console.log(
    'MRI geometry: independent affine grids, one-voxel focus/citation distinctions, inclusive bbox cell edges, metric spans, planes and endpoint sampling pass.',
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
