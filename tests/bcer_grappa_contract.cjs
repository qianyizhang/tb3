const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/bcer-short-recon-grappa.ts'),
    t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'bcer-grappa-v1',
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
  assert.equal(m.resetOnBackward(100, 99), true);
  assert.equal(m.resetOnBackward(100, 100), false);
  assert.equal(m.resetOnBackward(100, 101), false);
  const beats = [0, 0.5, 1].map((x, i) => ({
      id: `operation-${i}`,
      scene: 'operation',
      channels: { progress: [x, x], detail: i === 1 ? [0, 1] : [0, 0], reference: [0, 0] },
      startFrame: 168 * (i + 1),
      endFrame: 168 * (i + 2),
      frames: 168,
    })),
    p = { recipe: base.recipe, beats, durationFrames: 672 };
  assert.deepEqual(
    [0, 1, 2].map((i) => m.operationFrame(p, 1, i)),
    [336, 419, 503],
  );
  for (let i = 0; i < 3; i++) {
    assert.equal(m.operationIndex(t.sampleStory(p, m.operationFrame(p, i))), i);
    assert.equal(m.branchIndex(t.sampleStory(p, m.operationFrame(p, 1, i))), i);
  }
  for (const invalid of [-1, 3, 0.5, NaN]) {
    assert.throws(() => m.operationFrame(p, invalid), /Invalid/);
    assert.throws(() => m.operationFrame(p, 1, invalid), /Invalid/);
  }
  assert.equal(m.fixture.actual_output, null);
  assert.equal(m.fixture.clean_reference, null);
  assert.equal(m.fixture.sampled_lines.join(','), '28,32,28');
  assert.equal(m.fixture.masks[0].filter(Boolean).length, 28);
  assert.equal(m.fixture.ACS_bounds.join(','), '4,28');
  console.log(
    'PASS canonical3steps/3modeconditions, mask/ACS derivation and validator-reference reset',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
