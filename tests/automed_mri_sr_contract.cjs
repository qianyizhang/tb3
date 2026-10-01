const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/automed-mri-sr.ts');
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const p = {
    recipe: 'automed-mri-sr-v1',
    durationFrames: 288,
    beats: [
      {
        scene: 'operation',
        frames: 288,
        startFrame: 0,
        endFrame: 288,
        channels: { progress: [0, 1], detail: [0, 1], reference: [0, 0] },
      },
    ],
  };
  for (let i = 0; i < 4; i++) {
    const s = t.sampleStory(p, m.operationFrame(p, i));
    assert.equal(s.scene, 'operation');
    assert.equal(s.reference, 0);
    assert.equal(m.operationIndex(s.progress), i);
  }
  assert.throws(
    () => m.operationFrame({ ...p, recipe: 'automed-iu-xray-report-v1' }, 0),
    /Invalid/,
  );
  for (const i of [-1, 4, 0.5]) assert.throws(() => m.operationFrame(p, i), /Invalid/);
  for (const rule of ['raw', 'lpips', 'rating', 'normalization', 'pass'])
    assert.equal(m.canonicalRule(rule), rule);
  assert.equal(m.canonicalRule('clinical_accuracy'), null);
  assert.ok(m.resetOnBackward(20, 19));
  assert.equal(m.resetOnBackward(19, 20), false);
  assert.equal(m.automedMriSrPack.helper.weights, null);
  assert.match(m.formatRequirement('checked'), /no intensity/);
  assert.match(m.formatRequirement('declared'), /float32/);
  console.log('PASS: MRI SR canonical seeks and rule/reset boundaries');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
