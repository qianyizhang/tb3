const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const {
    rasPoint,
    nativePoint,
    fromFlat,
    nearestSample,
    inCrop,
    cprPixelIndex,
    cumulativeArc,
    boxEdges,
    planeCorners,
    boundaryIndices,
  } = await loadFrontend('../presentation/frontend/explainers/native/coronary-geometry.ts');
  const affine = [
      [-0.376953125, 0, 0, 30.4013671875],
      [0, 0.376953125, 0, 127.2548828125],
      [0, 0, 0.5, 39.45000076293945],
      [0, 0, 0, 1],
    ],
    shape = [366, 319, 205];
  const start = [-13.7021484375, 204.5302734375, 104.44999694824219];
  const ijk = nativePoint(affine, start);
  assert.ok(Math.abs(ijk[0] - 117) < 1e-8);
  assert.ok(Math.abs(ijk[1] - 205) < 1e-8);
  assert.ok(Math.abs(ijk[2] - 130) < 0.00002);
  const p = [142.31652215, 129.58714996, 42.53151526];
  nativePoint(affine, rasPoint(affine, p)).forEach((v, a) => assert.ok(Math.abs(v - p[a]) < 1e-10));
  const oblique = [
    [0, 2, 0, 4],
    [-3, 0, 0, 5],
    [0, 0, 4, 6],
    [0, 0, 0, 1],
  ];
  nativePoint(oblique, rasPoint(oblique, p)).forEach((v, a) =>
    assert.ok(Math.abs(v - p[a]) < 1e-10),
  );
  assert.equal(fromFlat((142 * 319 + 130) * 205 + 43, shape).join(','), '142,130,43');
  assert.equal(inCrop([-0.5, 318.5, 204.5], shape), true);
  assert.equal(inCrop([366, 100, 100], shape), false);
  assert.equal(cprPixelIndex([8, 371, 65], 7, 370, 64), 8 * 371 * 65 - 1);
  assert.throws(() => cprPixelIndex([8, 371, 65], 8, 0, 0));
  assert.equal(
    cumulativeArc([
      [0, 0, 0],
      [3, 4, 0],
      [3, 4, 12],
    ]).join(','),
    '0,5,17',
  );
  const corners = planeCorners(0, 142, shape);
  assert.ok(corners.every((p) => p[0] === 142));
  assert.equal(Math.abs(rasPoint(affine, corners[0])[2] - rasPoint(affine, corners[3])[2]), 102.5);
  const edges = boxEdges([
    [118, 105, 34],
    [168, 155, 55],
  ]);
  assert.equal(edges.length, 24);
  assert.equal(Math.min(...edges.map((p) => p[0])), 117.5);
  assert.equal(Math.max(...edges.map((p) => p[2])), 54.5);
  const full = Array.from({ length: 27 }, (_, i) => i);
  assert.equal(boundaryIndices(full, [3, 3, 3]).length, 26);
  assert.equal(nearestSample([0, 7, 42, 204], 204), 3);
  assert.equal(nearestSample([0, 7, 42, 204], 41), 2);
  console.log(
    'Coronary native geometry: inverse affine, L/A/S, exact membership boundary, CPR indexing, original-distance helpers and half-open cells pass.',
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
