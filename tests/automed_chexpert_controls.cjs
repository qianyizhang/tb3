const assert = require('node:assert/strict');
const fs = require('node:fs');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const plan = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const m = await loadFrontend(
    '../presentation/frontend/task-visuals/automed-chexpert-report-controls.ts',
  );
  const timeline = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  for (let i = 0; i < 4; i++) {
    const frame = m.operationFrame(plan, i);
    const state = timeline.sampleStory(plan, frame);
    assert.equal(state.scene, 'operation');
    assert.equal(m.operationIndex(state.progress), i);
    assert.equal(state.reference, 0);
  }
  console.log('PASS: four actual compiled-story canonical operation seeks');
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
