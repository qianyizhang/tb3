const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
    '../presentation/frontend/task-visuals/automedbench-full-synthrad2025-mrct-task.ts',
  );
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const p = JSON.parse(
    execFileSync(
      '/Users/zhangqy/pkgs/tb3/.venv/bin/python',
      [
        '-c',
        "import json;from pathlib import Path;from tb3_medical.explanation_stories import compile_story;print(json.dumps(compile_story(Path.cwd(),Path('presentation/external-tasks/stories/automedbench-full-synthrad2025-mrct-task.story.md'))))",
      ],
      { env: { ...process.env, PYTHONPATH: path.resolve('src') }, encoding: 'utf8' },
    ),
  );
  const frames = [168, 336, 504, 672];
  for (let j = 0; j < 4; j++) {
    assert.equal(m.operationFrame(p, j), frames[j]);
    const s = t.sampleStory(p, frames[j]);
    assert.equal(s.scene, 'operation');
    assert.equal(m.operationIndex(s), j);
    assert.equal(m.referenceVisible(s, true), false);
  }
  for (const v of [-1, 0.5, 4]) assert.throws(() => m.operationFrame(p, v));
  for (const v of ['MAE', 'PSNR', 'SSIM']) assert.equal(m.canonicalMetric(v), v);
  assert.equal(m.canonicalMetric('clinical_accuracy'), null);
  const late = t.sampleStory(p, 1008);
  assert.equal(late.scene, 'reference');
  assert.equal(m.referenceVisible(late), false);
  assert.equal(m.referenceVisible(late, true), true);
  for (const f of [0, 168, 840, 1176])
    assert.equal(m.referenceVisible(t.sampleStory(p, f), true), false);
  assert.equal(m.resetOnBackward(1009, 1008), true);
  assert.equal(m.resetOnBackward(1008, 1008), false);
  console.log(
    JSON.stringify({
      canonical_frames: frames,
      metric_states: ['MAE', 'PSNR', 'SSIM'],
      reader_reference_frame: 1008,
      private_CT: 0,
    }),
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
