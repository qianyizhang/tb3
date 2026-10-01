const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
    '../presentation/frontend/task-visuals/automedbench-full-medxpertqa-mm-task.ts',
  );
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'automed-medxpert-mm-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.referenceVisible({ ...base, scene, reference: 1 }, true), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference' }, true), true);
  const beats = [0, 0.5, 1].map((x, i) => ({
    scene: 'operation',
    channels: { progress: [x, x], detail: i === 1 ? [0, 1] : [0, 0], reference: [0, 0] },
    startFrame: 168 * i,
    endFrame: 168 * (i + 1),
    frames: 168,
  }));
  const plan = { recipe: base.recipe, beats, durationFrames: 504 };
  for (let i = 0; i < 3; i++)
    assert.equal(m.operationIndex(t.sampleStory(plan, m.operationFrame(plan, i))), i);
  for (let o = 0; o < 5; o++) {
    const state = t.sampleStory(plan, m.operationFrame(plan, 1, o));
    assert.equal(m.optionIndex(state), o);
    assert.equal(typeof m.source.source_question.options[m.letters[o]], 'string');
  }
  for (const i of [-1, 3, 0.5]) assert.throws(() => m.operationFrame(plan, i), /Invalid/);
  for (const o of [-1, 5, 0.5]) assert.throws(() => m.operationFrame(plan, 1, o), /Invalid/);
  assert.throws(() => m.operationFrame({ ...plan, recipe: 'abra-metadata-qa-v1' }, 0), /mismatch/);
  assert.equal(m.resetOnBackward(100, 99), true);
  assert.equal(m.resetOnBackward(99, 100), false);
  assert.equal(m.resetOnBackward(100, 0), true);
  assert.equal(m.source.source_question.label, undefined);
  assert.equal(m.source.public_reference, undefined);
  assert.equal(m.source.preview_data_uri, undefined);
  console.log(
    'PASS3canonical steps/5option seeks, explicit reader reveal/exit/backward/reset and no input gold',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
