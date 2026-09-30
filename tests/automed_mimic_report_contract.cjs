const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/automed-mimic-report.ts');
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const p = {
    recipe: 'automed-mimic-report-v1',
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
    /mismatch/,
  );
  for (const i of [-1, 4, 0.5]) assert.throws(() => m.operationFrame(p, i), /Invalid/);
  assert.equal(m.canonicalTier('standard'), 'standard');
  assert.equal(m.canonicalTier('pro'), null);
  assert.equal(m.canonicalMetric('micro'), 'micro');
  assert.equal(m.canonicalMetric('clinical'), null);
  assert.ok(m.resetOnBackward(20, 19));
  console.log('PASS: MIMIC four canonical seeks, tiers, macro/micro and reset boundaries');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
