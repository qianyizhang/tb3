const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
      '../presentation/frontend/task-visuals/imaging101-mri-t2-mapping.ts',
    ),
    t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'imaging101-t2-mapping-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.referenceVisible({ ...base, scene, reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }, true), true);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference' }), false);
  const beats = [0, 0.5, 1].map((x, i) => ({
      scene: 'operation',
      channels: { progress: [x, x], detail: i === 1 ? [0, 1] : [0, 0], reference: [0, 0] },
      startFrame: 168 * i,
      endFrame: 168 * (i + 1),
      frames: 168,
    })),
    p = { recipe: base.recipe, beats, durationFrames: 504 };
  for (let i = 0; i < 3; i++) {
    assert.equal(m.operationIndex(t.sampleStory(p, m.operationFrame(p, i))), i);
    assert.equal(m.branchIndex(t.sampleStory(p, m.operationFrame(p, 1, i))), i);
  }
  for (let i = 0; i < 3; i++)
    for (let j = 0; j < 3; j++) {
      const sampled = t.sampleStory(p, m.operationFrame(p, i, j));
      assert.equal(m.operationIndex(sampled), i);
      if (i === 1) assert.equal(m.branchIndex(sampled), j);
    }
  assert.equal(m.fixture.actual_output, null);
  assert.equal(m.fixture.clean_reference, null);
  const end = [
    {
      scene: 'reference',
      channels: { progress: [1, 1], detail: [0, 0], reference: [1, 1] },
      startFrame: 504,
      endFrame: 672,
      frames: 168,
    },
    {
      scene: 'limits',
      channels: { progress: [1, 1], detail: [0, 0], reference: [0, 0] },
      startFrame: 672,
      endFrame: 840,
      frames: 168,
    },
  ];
  const q = { ...p, beats: [...beats, ...end], durationFrames: 840 };
  assert.equal(m.referenceVisible(t.sampleStory(q, 504), true), true);
  assert.equal(m.referenceVisible(t.sampleStory(q, 672)), false);
  assert.equal(m.referenceVisible(t.sampleStory(q, 0)), false);
  assert.equal(m.referenceVisible(t.sampleStory(q, m.operationFrame(q, 1, 2))), false);
  assert.equal(m.fixture.branches.join(','), '10,50,100');
  assert.equal(m.fixture.toy_signal.length, 3);
  assert.equal(m.fixture.toy_signal[0] > m.fixture.toy_signal[2], true);
  console.log(
    'PASS canonical 3 steps / 3 native echo displays, T2 rules and validator-reference reset',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
