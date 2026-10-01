const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/bcer-short-superres.ts'),
    t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'bcer-superres-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.referenceVisible({ ...base, scene, reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference' }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }, true), true);
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.referenceVisible({ ...base, scene, reference: 1 }, true), false);
  assert.equal(m.resetOnBackward(100, 20), true);
  assert.equal(m.resetOnBackward(20, 100), false);
  const beats = [0, 0.5, 1].map((x, i) => ({
      scene: 'operation',
      channels: { progress: [x, x], detail: i === 1 ? [0, 1] : [0, 0], reference: [0, 0] },
      startFrame: 168 * (i + 1),
      endFrame: 168 * (i + 2),
      frames: 168,
    })),
    p = { recipe: base.recipe, beats, durationFrames: 672 };
  // Independent canonical target-beat endpoints and earliest midpoint tie.
  assert.equal(m.operationFrame(p, 1, 0), 336);
  assert.equal(m.operationFrame(p, 1, 1), 419);
  assert.equal(m.operationFrame(p, 1, 2), 503);
  for (let i = 0; i < 3; i++) {
    assert.equal(m.operationIndex(t.sampleStory(p, m.operationFrame(p, i))), i);
    assert.equal(m.branchIndex(t.sampleStory(p, m.operationFrame(p, 1, i))), i);
  }
  for (const bad of [-1, 3, 0.5, NaN]) assert.throws(() => m.operationFrame(p, bad));
  assert.throws(() => m.operationFrame(p, 1, 3));
  assert.equal(m.gridCount([641, 641, 22]) - m.gridCount([640, 640, 21]), 437782);
  assert.equal(m.interpolationModes.join(','), 'linear,nearest,bspline');
  assert.equal(m.fixture.actual_output, null);
  assert.equal(m.fixture.clean_reference, null);
  assert.equal(
    m.fixture.derived_size.map((x) => x.join(',')).join(';'),
    '640,640,21;640,640,42;1280,1280,42',
  );
  assert.equal(m.fixture.rounded_spacing_example.derived_size.join(','), '641,641,22');
  console.log(
    'PASS canonical3steps/3targetgrids, exactceil derivation and explicit grader eligibility/backward reset',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
