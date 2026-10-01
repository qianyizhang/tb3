const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
      '../presentation/frontend/task-visuals/automedbench-full-vqa-omnimedvqa-task.ts',
    ),
    t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'automed-omni-v1',
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
      startFrame: 168 * i,
      endFrame: 168 * (i + 1),
      frames: 168,
    })),
    p = { recipe: base.recipe, beats, durationFrames: 504 };
  for (let i = 0; i < 3; i++) {
    assert.equal(m.operationIndex(t.sampleStory(p, m.operationFrame(p, i))), i);
    assert.equal(m.branchIndex(t.sampleStory(p, m.operationFrame(p, 1, i))), i);
  }
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }, true), true);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 0 }, true), false);
  assert.equal(m.resetOnBackward(100, 0), true);
  assert.equal(m.resetOnBackward(0, 100), false);
  for (const i of [-1, 3, 0.5]) assert.throws(() => m.operationFrame(p, i), /Invalid/);
  for (const j of [-1, 3, 0.5]) assert.throws(() => m.operationFrame(p, 1, j), /Invalid/);
  assert.equal(m.source.source_question.answer, undefined);
  assert.deepEqual(Array.from(m.fixture.parsed_examples), ['A', null, null]);
  assert.equal(m.fixture.actual_prediction, null);
  assert.equal(m.fixture.actual_reference, null);
  assert.equal(m.source.source_question.gt_answer, undefined);
  console.log(
    'PASS canonical3steps/3parsercontrols, allowed-set boundary and source-reference reset',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
