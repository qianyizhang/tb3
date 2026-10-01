const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend('../presentation/frontend/task-visuals/automed-ctorg-ctsr.ts');
  const t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const { execFileSync } = require('node:child_process');
  const path = require('node:path');
  const p = JSON.parse(
    execFileSync(
      '/Users/zhangqy/pkgs/tb3/.venv/bin/python',
      [
        '-c',
        "import json;from pathlib import Path;from tb3_medical.explanation_stories import compile_story;print(json.dumps(compile_story(Path.cwd(),Path('presentation/external-tasks/stories/automedbench-full-ctorg-ctsr-task.story.md'))))",
      ],
      { env: { ...process.env, PYTHONPATH: path.resolve('src') }, encoding: 'utf8' },
    ),
  );
  const expected = [0, 1, 2, 3].map((i) => {
    let best = 0,
      d = Infinity;
    for (let k = 0; k < 288; k++) {
      const u = k / 287,
        v = Math.abs(u * u * (3 - 2 * u) - i / 3);
      if (v < d - 1e-12) {
        d = v;
        best = k;
      }
    }
    return 576 + best;
  });
  for (let i = 0; i < 4; i++) {
    assert.equal(m.operationFrame(p, i), expected[i]);
    const s = t.sampleStory(p, m.operationFrame(p, i));
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
  assert.equal(m.automedCtorgCtsrPack.helper.weights, null);
  assert.match(m.formatRequirement('checked'), /missing outputs/);
  assert.match(m.formatRequirement('declared'), /3D NIfTI/);
  for (const frame of [0, 288, 576, 864, 1152]) assert.equal(t.sampleStory(p, frame).reference, 0);
  for (const key of ['prediction', 'reference', 'score', 'shape'])
    assert.equal(m.automedCtorgCtsrPack.output[key], null);
  for (const rule of ['raw', 'ssim', 'rating', 'completion', 'workflow'])
    assert.ok(m.automedCtorgCtsrPack.output.rules[rule].length > 0);
  console.log('PASS: CT-ORG canonical seeks and rule/reset boundaries');
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
