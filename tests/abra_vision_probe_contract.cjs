const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/abra-vision-probe.ts');
  const timeline = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'abra-vision-probe-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  assert.equal(m.probeReferenceVisible({ ...base, scene: 'reference', reference: 1 }), true);
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.probeReferenceVisible({ ...base, scene, reference: 1 }), false);
  assert.equal(m.probeReferenceVisible({ ...base, scene: 'reference' }), false);
  const beats = Array.from({ length: 6 }, (_, i) => ({
    scene: 'operation',
    channels: { progress: [i / 5, i / 5], detail: [0, 1], reference: [0, 0] },
    startFrame: 168 * i,
    endFrame: 168 * (i + 1),
    frames: 168,
  }));
  for (let c = 0; c < 6; c++)
    for (let j = 0; j < 5; j++) {
      const f = m.probeOperationFrame({ recipe: base.recipe, beats }, c, j);
      const sampled = timeline.sampleStory({ recipe: base.recipe, beats, durationFrames: 1008 }, f);
      const detail = sampled.detail;
      assert.equal(m.conditionIndex(sampled), c);
      assert.equal(m.selectedIndexSlot({ ...base, detail }), j);
    }
  assert.throws(
    () => m.probeOperationFrame({ recipe: 'abra-metadata-qa-v1', beats }, 0, 0),
    /mismatch/,
  );
  console.log('PASS: 30 canonical condition/index seeks and explicit reference/reset boundary');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
