const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/automed-vqa-rad.ts');
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = { recipe: 'automed-vqa-rad-v1', scene: 'input', progress: 0, frame: 0 };
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.publicAnnotationVisible({ ...base, scene }, true), false);
  assert.equal(m.publicAnnotationVisible({ ...base, scene: 'helper' }), false);
  assert.equal(m.publicAnnotationVisible({ ...base, scene: 'helper' }, true), true);
  const p = {
    recipe: base.recipe,
    durationFrames: 864,
    beats: [
      {
        scene: 'operation',
        startFrame: 576,
        endFrame: 864,
        frames: 288,
        channels: { progress: [0, 1], detail: [0, 1], reference: [0, 0] },
      },
    ],
  };
  for (let i = 0; i < 4; i++)
    assert.equal(m.operationIndex(t.sampleStory(p, m.operationFrame(p, i))), i);
  for (const i of [-1, 4, 0.5]) assert.throws(() => m.operationFrame(p, i), /mismatch/);
  assert.equal(m.resetOnBackward(20, 19), true);
  assert.equal(m.resetOnBackward(19, 20), false);
  assert.equal(m.automedVqaRadPack.source.public_answer, undefined);
  assert.equal(m.automedVqaRadPack.helper.public_answer, 'yes');
  console.log('PASS canonical4steps and explicit public helper gate/reset');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
