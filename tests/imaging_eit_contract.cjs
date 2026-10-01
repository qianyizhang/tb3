const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/imaging-eit.ts');
  const c = await loadFrontend('../presentation/frontend/task-visuals/imaging-eit-controls.ts');
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const beats = [0, 1, 2, 3].map((i) => ({
    id: 'operation-' + i,
    scene: 'operation',
    startFrame: 384 + 168 * i,
    endFrame: 552 + 168 * i,
    frames: 168,
    channels: { progress: [i / 3, i / 3], detail: [0, 1], reference: [0, 0] },
  }));
  const p = { recipe: 'imaging-eit-v1', durationFrames: 1056, beats };
  for (let i = 0; i < 4; i++)
    for (let j = 0; j < 3; j++) {
      const frame = m.operationFrame(p, i, j);
      assert.equal(frame, 384 + 168 * i + [0, 83, 167][j]);
      const state = t.sampleStory(p, frame);
      assert.equal(m.operationIndex(state), i);
      assert.equal(m.methodIndex(state), j);
    }
  for (const x of [-1, 4, 0.5, NaN]) assert.throws(() => m.operationFrame(p, x), /Invalid/);
  for (const x of [-1, 3, 0.5, NaN]) assert.throws(() => m.operationFrame(p, 0, x), /Invalid/);
  assert.equal(c.publicTruthVisible('helper'), false);
  assert.equal(c.publicTruthVisible('helper', true), true);
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(c.publicTruthVisible(scene, true), false);
  assert.equal(c.resetOnBackward(10, 9), true);
  assert.equal(c.resetOnBackward(10, 10), false);
  assert.equal(c.toyGaugeDifference(3, 1), 2);
  assert.equal(c.toyGaugeDifference(3, 1, 10), 2);
  assert.throws(() => c.toyGaugeDifference(NaN, 1), /finite/);
  assert.equal(c.measurementRow(207, 208), 207);
  assert.equal(c.measurementRow(208, 208), null);
  assert.equal(c.measurementRow(-1, 208), null);
  assert.equal(c.measurementRow(1.5, 208), null);
  assert.equal(m.imagingEitPack.output.prediction, null);
  assert.equal(m.imagingEitPack.output.map, null);
  console.log(
    'PASS source-only4canonical×3methods/earliesttie/publictruthgate/backward/authoredgauge/boundednativeindex; compiled timeline parity',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
