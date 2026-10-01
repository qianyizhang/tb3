const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const m = await loadFrontend(
      '../presentation/frontend/task-visuals/automedbench-full-lidc-idri-denoising-task.ts',
    ),
    t = await loadFrontend('../presentation/frontend/task-visuals/story-timeline.ts');
  const base = {
    recipe: 'automedbench-full-lidc-idri-denoising-task-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(m.referenceVisible({ ...base, scene, reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }), false);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference', reference: 1 }, true), true);
  assert.equal(m.referenceVisible({ ...base, scene: 'reference' }), false);
  const { execFileSync } = require('node:child_process');
  const path = require('node:path');
  const p = JSON.parse(
    execFileSync(
      '/Users/zhangqy/pkgs/tb3/.venv/bin/python',
      [
        '-c',
        "import json;from pathlib import Path;from tb3_medical.explanation_stories import compile_story;print(json.dumps(compile_story(Path.cwd(),Path('presentation/external-tasks/stories/automedbench-full-lidc-idri-denoising-task.story.md'))))",
      ],
      { env: { ...process.env, PYTHONPATH: path.resolve('src') }, encoding: 'utf8' },
    ),
  );
  for (let i = 0; i < 3; i++)
    for (let j = 0; j < 3; j++) {
      const f = m.operationFrame(p, i, j);
      assert.equal(f, i === 1 ? [336, 419, 503][j] : [168, 336, 504][i]);
      const s = t.sampleStory(p, f);
      assert.equal(m.operationIndex(s), i);
      if (i === 1) assert.equal(m.branchIndex(s), j);
    }
  for (const i of [-1, 3, 0.5]) assert.throws(() => m.operationFrame(p, i), /Invalid/);
  assert.throws(() => m.operationFrame(p, 1, 3), /Invalid/);
  assert.equal(m.fixture.actual_output, null);
  assert.equal(m.fixture.clean_reference, null);
  const r = t.sampleStory(p, 840);
  assert.equal(r.scene, 'reference');
  assert.equal(m.referenceVisible(r), false);
  assert.equal(m.referenceVisible(r, true), true);
  assert.equal(m.referenceVisible(t.sampleStory(p, 1008), true), false);
  assert.equal(m.referenceVisible(t.sampleStory(p, 0), true), false);
  assert.equal(m.referenceVisible(t.sampleStory(p, m.operationFrame(p, 1, 2)), true), false);
  assert.equal(m.fixture.branches.join(','), '0,1,2');
  console.log(
    'PASS canonical 3 steps / 3 operator rules, explicit public evaluator rules and reset',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
