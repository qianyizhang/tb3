const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/automed-medframeqa.ts');
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const p = {
    recipe: 'automed-medframeqa-v1',
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
  assert.throws(() => m.operationFrame({ ...p, recipe: 'unrelated-recipe-v1' }, 0), /Invalid/);
  for (const i of [-1, 4, 0.5]) assert.throws(() => m.operationFrame(p, i), /Invalid/);
  assert.ok(m.resetOnBackward(20, 19));
  assert.equal(m.resetOnBackward(19, 20), false);
  assert.equal(m.automedMedframeqaPack.frames.length, 2);
  assert.equal(m.automedMedframeqaPack.helper.valid_labels.join(''), 'ABCDE');
  assert.equal(m.automedMedframeqaPack.helper.source_options, 6);
  assert.match(m.automedMedframeqaPack.output.format_gate, />=0.5/);
  assert.match(m.automedMedframeqaPack.output.accuracy, /all evaluator-selected question_ids/);
  console.log('PASS: MedFrameQA canonical seeks and rule/reset boundaries');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
