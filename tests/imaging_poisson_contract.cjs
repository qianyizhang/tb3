const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
      '../presentation/frontend/task-visuals/imaging101-ct-poisson-lowdose.ts',
    ),
    t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'imaging101-poisson-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.referenceVisible({ ...base, scene, reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference' }), false);
  const beats = [0, 0.5, 1].map((x, i) => ({
      scene: 'operation',
      channels: { progress: [x, x], detail: i === 1 ? [0, 1] : [0, 0], reference: [0, 0] },
      startFrame: 168 * (i + 1),
      endFrame: 168 * (i + 2),
      frames: 168,
    })),
    p = { recipe: base.recipe, beats, durationFrames: 672 };
  assert.equal(m.operationFrame(p, 1, 0), 336);
  assert.equal(m.operationFrame(p, 1, 1), 419);
  assert.equal(m.operationFrame(p, 1, 2), 503);
  for (const bad of [-1, 3, 0.5, NaN]) assert.throws(() => m.operationFrame(p, bad));
  assert.throws(() => m.operationFrame(p, 1, 3));
  for (let i = 0; i < 3; i++) {
    assert.equal(m.operationIndex(t.sampleStory(p, m.operationFrame(p, i))), i);
    assert.equal(m.branchIndex(t.sampleStory(p, m.operationFrame(p, 1, i))), i);
  }
  assert.equal(m.fixture.actual_output, null);
  assert.equal(m.fixture.clean_reference, null);
  const end = [
    {
      scene: 'reference',
      channels: { progress: [1, 1], detail: [0, 0], reference: [1, 1] },
      startFrame: 672,
      endFrame: 840,
      frames: 168,
    },
    {
      scene: 'limits',
      channels: { progress: [1, 1], detail: [0, 0], reference: [0, 0] },
      startFrame: 840,
      endFrame: 1008,
      frames: 168,
    },
  ];
  const initial = {
    scene: 'input',
    channels: { progress: [0, 0], detail: [0, 0], reference: [0, 0] },
    startFrame: 0,
    endFrame: 168,
    frames: 168,
  };
  const q = { ...p, beats: [initial, ...beats, ...end], durationFrames: 1008 };
  assert.equal(m.referenceVisible(t.sampleStory(q, 672)), false);
  assert.equal(m.referenceVisible(t.sampleStory(q, 672), true), true);
  assert.equal(m.referenceVisible(t.sampleStory(q, 840), true), false);
  assert.equal(m.referenceVisible(t.sampleStory(q, 0), true), false);
  assert.equal(m.referenceVisible(t.sampleStory(q, m.operationFrame(q, 1, 2))), false);
  assert.equal(m.illustrativePostlog(0, 300), m.illustrativePostlog(1, 300));
  assert.equal(Math.abs(m.illustrativePostlog(300, 300)), 0);
  assert.ok(m.illustrativePostlog(301, 300) < 0);
  assert.throws(() => m.illustrativePostlog(10, 0));
  assert.equal(
    m.illustrativeWeights([300, 100, 1], 'counts').join(','),
    '1,0.3333333333333333,0.0033333333333333335',
  );
  assert.equal(m.illustrativeWeights([300, 100, 1], 'uniform').join(','), '1,1,1');
  assert.throws(() => m.illustrativeWeights([0], 'counts'));
  assert.equal(m.metricRoutes.length, 3);
  assert.equal(m.resetOnBackward(200, 100), true);
  assert.equal(m.resetOnBackward(100, 200), false);
  assert.equal(m.fixture.I0, 300);
  assert.equal(m.fixture.floored_counts.join(','), '300,100,1');
  assert.ok(Math.abs(m.fixture.dose_shift + Math.log(1000 / 300)) < 1e-12);
  console.log(
    'PASS canonical3steps/3 count conditions, log/dose derivation and conditional expected-fixture/backward reset',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
