const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
    '../presentation/frontend/task-visuals/automed-msd-pancreas-ctsr.ts',
  );
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const { execFileSync } = require('node:child_process');
  const path = require('node:path');
  const p = JSON.parse(
    execFileSync(
      '/Users/zhangqy/pkgs/tb3/.venv/bin/python',
      [
        '-c',
        "import json;from pathlib import Path;from tb3_medical.explanation_stories import compile_story;print(json.dumps(compile_story(Path.cwd(),Path('presentation/external-tasks/stories/automedbench-full-msd-pancreas-ctsr-task.story.md'))))",
      ],
      { env: { ...process.env, PYTHONPATH: path.resolve('src') }, encoding: 'utf8' },
    ),
  );
  const expectedFrames = [576, 687, 752, 863];
  for (let i = 0; i < 4; i++) {
    assert.equal(m.operationFrame(p, i), expectedFrames[i]);
    const s = t.sampleStory(p, expectedFrames[i]);
    assert.equal(s.scene, 'operation');
    assert.equal(s.reference, 0);
    assert.equal(m.operationIndex(s.progress), i);
  }
  assert.throws(
    () => m.operationFrame({ ...p, recipe: 'automed-iu-xray-report-v1' }, 0),
    /Invalid/,
  );
  for (const i of [-1, 4, 0.5]) assert.throws(() => m.operationFrame(p, i), /Invalid/);
  for (const rule of ['raw', 'ssim', 'rating', 'completion', 'workflow'])
    assert.equal(m.canonicalRule(rule), rule);
  assert.equal(m.canonicalRule('clinical_accuracy'), null);
  assert.ok(m.resetOnBackward(20, 19));
  assert.equal(m.resetOnBackward(19, 20), false);
  assert.equal(m.automedMsdPancreasCtsrPack.helper.weights, null);
  assert.match(m.formatRequirement('checked'), /missing outputs/);
  assert.match(m.formatRequirement('declared'), /3D NIfTI/);
  console.log(
    JSON.stringify({
      canonical_frames: expectedFrames,
      metric_rules: ['raw', 'ssim', 'rating', 'completion', 'workflow'],
      private_reference: 0,
    }),
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
