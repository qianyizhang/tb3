const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
    '../presentation/frontend/task-visuals/automedbench-full-pathology-caption-500-task.ts',
  );
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const b = {
    recipe: 'automed-pathology-caption-500-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  assert.equal(m.referenceVisible({ ...b, scene: 'reference', reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...b, scene: 'reference' }, true), true);
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.referenceVisible({ ...b, scene, reference: 1 }, true), false);
  assert.equal(m.referenceVisible({ ...b, scene: 'reference' }), false);
  const beats = [0, 0.5, 1].map((x, i) => ({
    scene: 'operation',
    channels: { progress: [x, x], detail: [0, 0], reference: [0, 0] },
    startFrame: 168 * i,
    endFrame: 168 * (i + 1),
    frames: 168,
  }));
  const plan = { recipe: b.recipe, beats, durationFrames: 504 };
  for (let i = 0; i < 3; i++)
    assert.equal(m.operationIndex(t.sampleStory(plan, m.operationFrame(plan, i))), i);
  assert.throws(() => m.operationFrame({ recipe: 'abra-metadata-qa-v1', beats }, 0), /mismatch/);
  for (const index of [-1, 3, 0.5]) assert.throws(() => m.operationFrame(plan, index), /Invalid/);
  assert.equal(m.resetOnBackward(20, 19), true);
  assert.equal(m.resetOnBackward(19, 20), false);
  console.log('PASS: PathCap500 canonical operation seeks and reference/reset boundary');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
