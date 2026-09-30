const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
    '../presentation/frontend/task-visuals/automedbench-full-chest-xray-pneumonia-cls-task.ts',
  );
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'automed-pneumonia-cls-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  for (const scene of ['input', 'operation', 'output', 'limits']) {
    assert.equal(m.referenceVisible({ ...base, scene, reference: 1 }), false);
    assert.equal(m.publicTrainingLabel({ ...base, scene, reference: 1 }), null);
  }
  assert.equal(m.publicTrainingLabel({ ...base, scene: 'reference', reference: 1 }), 'normal');
  assert.equal(m.publicTrainingLabel({ ...base, scene: 'reference' }), null);
  const scenes = ['input', 'operation', 'operation', 'operation', 'output', 'reference', 'limits'];
  const values = [0, 0, 0.5, 1, 1, 1, 1];
  const beats = scenes.map((scene, j) => ({
    scene,
    channels: {
      progress: [values[j], values[j]],
      detail: [0, 0],
      reference: scene === 'reference' ? [1, 1] : [0, 0],
    },
    startFrame: 168 * j,
    endFrame: 168 * (j + 1),
    frames: 168,
  }));
  const p = { recipe: base.recipe, beats, durationFrames: 1176 };
  for (let i = 0; i < 3; i++) {
    assert.equal(m.operationFrame(p, i), 168 * (i + 1));
    assert.equal(m.operationIndex(t.sampleStory(p, m.operationFrame(p, i))), i);
    assert.equal(m.publicTrainingLabel(t.sampleStory(p, m.operationFrame(p, i))), null);
  }
  assert.equal(m.publicTrainingLabel(t.sampleStory(p, 840)), 'normal');
  for (const frame of [0, 672, 1008])
    assert.equal(m.publicTrainingLabel(t.sampleStory(p, frame)), null);
  assert.throws(() => m.operationFrame({ ...p, recipe: 'abra-metadata-qa-v1' }, 0), /mismatch/);
  console.log('PASS canonical3steps, public label late reveal/backward/exit/reset before paint');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
