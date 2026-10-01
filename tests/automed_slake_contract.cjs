const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/automed-slake.ts');
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const plan = {
    recipe: 'automed-slake-v1',
    durationFrames: 288,
    beats: [0, 1 / 3, 2 / 3, 1].map((v, i) => ({
      id: `step-${i}`,
      scene: 'operation',
      frames: 72,
      startFrame: 72 * i,
      endFrame: 72 * (i + 1),
      channels: { progress: [v, v], detail: [0, 1], reference: [0, 0] },
    })),
  };
  for (let i = 0; i < 4; i++)
    assert.equal(m.operationIndex(t.sampleStory(plan, m.operationFrame(plan, i))), i);
  for (const i of [-1, 4, 0.5]) assert.throws(() => m.operationFrame(plan, i), /Invalid/);
  assert.throws(
    () => m.operationFrame({ ...plan, recipe: 'automed-medxpert-mm-v1' }, 0),
    /mismatch/,
  );
  assert.throws(() => m.operationFrame({ ...plan, beats: [] }, 0), /Missing/);
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.readerVisible({ scene }, true), false);
  assert.equal(m.readerVisible({ scene: 'helper', reference: 1 }), false);
  assert.equal(m.readerVisible({ scene: 'helper', reference: 1 }, true), true);
  assert.equal(m.readerVisible({ scene: 'helper', reference: 0 }, true), false);
  assert.equal(m.resetOnBackward(100, 0), true);
  assert.equal(m.resetOnBackward(100, 99), true);
  assert.equal(m.resetOnBackward(99, 100), false);
  assert.equal(m.automedSlakePack.source.answer, undefined);
  assert.equal(m.automedSlakePack.source.full_membership, null);
  console.log(
    'PASS four canonical steps, explicit public annotation, exit/backward/reset gates and no input answer',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
