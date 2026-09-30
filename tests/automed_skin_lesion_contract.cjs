const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
    '../presentation/frontend/task-visuals/automedbench-full-skin-lesion-cls-task.ts',
  );
  const timeline = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'automed-skin-lesion-cls-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }), true);
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.referenceVisible({ ...base, scene, reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference' }), false);
  const beats = [0, 0.5, 1].map((x, i) => ({
    scene: 'operation',
    channels: { progress: [x, x], detail: i === 1 ? [0, 1] : [0, 0], reference: [0, 0] },
    startFrame: 168 * i,
    endFrame: 168 * (i + 1),
    frames: 168,
  }));
  const plan = { recipe: base.recipe, beats, durationFrames: 504 };
  const expected = [
    'actinic_keratoses',
    'basal_cell_carcinoma',
    'benign_keratosis_like_lesions',
    'dermatofibroma',
    'melanoma',
    'melanocytic_nevi',
    'vascular_lesions',
  ];
  for (let i = 0; i < 7; i++) {
    assert.equal(m.canonicalForIndex(i), expected[i]);
    const state = timeline.sampleStory(plan, m.operationFrame(plan, 1, i));
    assert.equal(m.mappingIndex(state), i);
  }
  assert.throws(() => m.canonicalForIndex(7), /Invalid/);
  assert.throws(() => m.operationFrame({ recipe: 'abra-metadata-qa-v1', beats }, 0), /mismatch/);
  console.log('PASS: seven source mappings/eased seeks and reference/reset boundary');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
