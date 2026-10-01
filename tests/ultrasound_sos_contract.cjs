const assert = require('node:assert/strict');
const path = require('node:path');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
    '../presentation/frontend/task-visuals/imaging-ultrasound-sos-controls.ts',
  );
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const { execFileSync } = require('node:child_process');
  const plan = JSON.parse(
    execFileSync(
      '/Users/zhangqy/pkgs/tb3/.venv/bin/python',
      [
        '-c',
        "import json;from pathlib import Path;from tb3_medical.explanation_stories import compile_story;print(json.dumps(compile_story(Path.cwd(),Path('presentation/external-tasks/stories/imaging101-ultrasound-sos-tomography.story.md'))))",
      ],
      {
        env: { ...process.env, PYTHONPATH: require('node:path').resolve('src') },
        encoding: 'utf8',
      },
    ),
  );

  for (let i = 0; i < 3; i++)
    for (let j = 0; j < 3; j++) {
      const expected = i === 1 ? [336, 419, 503][j] : [168, 336, 504][i];
      const frame = m.operationFrame(plan, i, j);
      assert.equal(frame, expected);
      const s = t.sampleStory(plan, frame);
      assert.equal(m.operationIndex(s.progress), i);
      if (i === 1) assert.equal(m.branchIndex(s.detail), j);
      assert.equal(s.reference, 0);
    }
  for (const method of ['fbp', 'sart', 'tv']) assert.equal(m.canonicalMethod(method), method);
  assert.equal(m.canonicalMethod('admm'), null);
  for (const i of [0, 30, 59]) assert.equal(m.nativeAngle(i), i);
  for (const i of [-1, 60, 0.5, NaN]) assert.equal(m.nativeAngle(i), null);
  assert.ok(m.signedSlowness(1450) > 0);
  assert.equal(m.signedSlowness(1500), 0);
  assert.ok(m.signedSlowness(2500) < 0);
  for (const c of [0, -1, Infinity, NaN]) assert.equal(m.signedSlowness(c), null);
  assert.equal(m.resetOnBackward(12, 11), true);
  assert.equal(m.resetOnBackward(12, 12), false);
  for (const i of [-1, 3, 0.5]) assert.throws(() => m.operationFrame(plan, i), /Invalid/);
  assert.throws(() => m.operationFrame({ ...plan, recipe: 'bad' }, 0), /mismatch/);
  assert.throws(() => m.operationFrame({ ...plan, beats: [] }, 0), /absent/);
  console.log(
    'PASS nine canonical requests, 168/336/504 and 336/419/503; units/sign/native bounds/reset',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
