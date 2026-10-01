const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
      '../presentation/frontend/task-visuals/automedbench-full-pathvqa-task.ts',
    ),
    t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'automed-pathvqa-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.referenceVisible({ ...base, scene, reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }, true), true);
  assert.equal(m.referenceVisible({ ...base, scene: 'limits', reference: 1 }, true), false);
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
  for (const i of [-1, 3, 0.5]) assert.throws(() => m.operationFrame(p, i), /mismatch/);
  assert.ok(m.resetOnBackward(20, 19));
  assert.equal(m.resetOnBackward(19, 20), false);
  assert.equal(m.source.source_question.answer, undefined);
  assert.equal(m.fixture.nonbinary.EM, 0);
  assert.ok(Math.abs(m.fixture.nonbinary.token_F1 - 2 / 3) < 1e-9);
  assert.equal(m.fixture.binary.strict_match, 0);
  console.log('PASS canonical3steps/3metricbranches, toyderivation and train-reference reset');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
