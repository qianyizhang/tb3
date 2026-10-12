const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');

(async () => {
  const { rasPoint, nearestSample, insideCrop, planeCorners, boxEdges } = await loadFrontend(
    '../presentation/frontend/explainers/native/landmark-geometry.ts',
  );
  const affine = [
    [-0.71875, 0, 0, 181.640625],
    [0, 0.71875, 0, -7.140625],
    [0, 0, 0.70001220703125, -1546.11474609375],
    [0, 0, 0, 1],
  ];
  const claim = [269.8, 154.6, 906.1],
    t5 = [269.7, 156, 908.8],
    t4 = [273, 165.4, 937.6];
  const a = rasPoint(affine, claim),
    b = rasPoint(affine, t5);
  assert.ok(Math.abs(Math.hypot(...a.map((v, i) => v - b[i])) - 2.142) < 0.001);
  assert.equal(insideCrop(t4, [512, 512, 920]), false);
  assert.equal(insideCrop(claim, [512, 512, 920]), true);
  assert.equal(insideCrop([-0.5, 511.5, 919.5], [512, 512, 920]), true);
  assert.equal(nearestSample([0, 3, 8, 11], 7), 2);
  assert.equal(nearestSample([0, 3, 8, 11], 4), 1);
  const corners = planeCorners(2, 908, [512, 512, 920]);
  assert.ok(corners.every((p) => p[2] === 908));
  assert.equal(Math.abs(rasPoint(affine, corners[1])[0] - rasPoint(affine, corners[0])[0]), 368);
  const edges = boxEdges([
    [-0.5, -0.5, -0.5],
    [511.5, 511.5, 919.5],
  ]);
  assert.equal(edges.length, 24);
  for (let n = 0; n < edges.length; n += 2)
    assert.equal(edges[n].filter((v, i) => v !== edges[n + 1][i]).length, 1);
  console.log(
    'Landmark native geometry: affine, fractional points, crop exclusion, physical planes, explicit sampling and 12 box edges pass.',
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
