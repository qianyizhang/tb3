const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const root = path.resolve(__dirname, '..');
  const plans = JSON.parse(
    execFileSync(
      path.join(root, '.venv/bin/python'),
      [
        '-c',
        'import json; from pathlib import Path; from tb3_medical.explanation_stories import compile_story; r=Path.cwd(); print(json.dumps([compile_story(r,p) for pattern in ["groups/*/presentation/stories/*.story.md","presentation/external-tasks/stories/*.story.md"] for p in r.glob(pattern)]))',
      ],
      { cwd: root, encoding: 'utf8' },
    ),
  );
  const {
    sampleStory,
    identityRows,
    storyPresentation,
    nativeFactory,
    isPlanarStory,
    Group,
    traceEdges,
    graph,
    residualM,
    level0Point,
  } = await loadFrontend('expansion_fixture.mjs');
  const baseline = JSON.parse(
    fs.readFileSync(path.join(__dirname, 'fixtures/story-baseline.json')),
  );
  for (const witness of baseline.stories)
    assert.ok(
      plans.some((plan) => plan.id === witness.id),
      'Missing original story: ' + witness.id,
    );
  let frames = 0,
    native = 0;
  for (const plan of plans) {
    const snapshots = Array.from({ length: plan.durationFrames }, (_, frame) =>
      JSON.stringify(sampleStory(plan, frame)),
    );
    const witness = baseline.stories.find((s) => s.id === plan.id);
    if (witness) {
      assert.equal(plan.source_sha256, witness.source_sha256);
      const oldStates = snapshots.map((value) => {
        const state = JSON.parse(value);
        delete state.operation;
        delete state.showDeformedTarget;
        return state;
      });
      assert.equal(
        crypto.createHash('sha256').update(JSON.stringify(oldStates)).digest('hex'),
        witness.state_sha256,
        plan.id + ' pre-refactor state witness',
      );
    }
    const renamed = structuredClone(plan);
    renamed.id = 'renamed-story';
    renamed.beats.forEach((beat, i) => {
      beat.id = `renamed-${i}`;
    });
    assert.equal(
      JSON.stringify(storyPresentation(plan)),
      JSON.stringify(storyPresentation(renamed)),
    );
    for (const beat of plan.beats) {
      const original = { ...sampleStory(plan, beat.endFrame - 1), beatId: null };
      const other = { ...sampleStory(renamed, beat.endFrame - 1), beatId: null };
      assert.equal(JSON.stringify(original), JSON.stringify(other), plan.id + ' rename semantics');
    }
    frames += snapshots.length;
    for (const frame of [plan.durationFrames - 1, 0, ...plan.beats.map((b) => b.startFrame), 17]) {
      const state = sampleStory(plan, frame);
      assert.equal(JSON.stringify(state), snapshots[frame]);
      assert.ok(Object.isFrozen(state));
      assert.equal(state.recipe, plan.recipe);
    }
    assert.throws(() => sampleStory(plan, 1.5));
    if (isPlanarStory(plan)) continue;
    native++;
    const parent = new Group(),
      content = nativeFactory(plan)(parent);
    assert.equal(parent.children.length, 1);
    for (const beat of plan.beats) content.update(sampleStory(plan, beat.endFrame - 1));
    const geometries = new Set(),
      materials = new Set();
    parent.traverse((o) => {
      if (o.geometry) geometries.add(o.geometry);
      if (o.material) materials.add(o.material);
    });
    let disposed = 0;
    for (const resource of [...geometries, ...materials])
      resource.addEventListener('dispose', () => disposed++);
    content.dispose();
    content.dispose();
    assert.equal(parent.children.length, 0);
    assert.equal(disposed, geometries.size + materials.size);
    assert.throws(() => content.update(sampleStory(plan, 0)));
  }
  const full = traceEdges(1);
  const identity = plans.find((plan) => plan.recipe === 'anatomy-identity-v1');
  assert.ok(identity, 'Exercise supplied-object identity semantics');
  for (const beat of identity.beats.filter((beat) => beat.channels.reveal[1] === 0)) {
    const rows = identityRows(sampleStory(identity, beat.endFrame - 1));
    assert.ok(
      rows.every((row) => row.label === null),
      'No names before the reveal',
    );
    assert.equal(rows.filter((row) => row.selected).length, 1);
  }
  const identityEnd = identityRows(sampleStory(identity, identity.durationFrames - 1));
  assert.equal(new Set(identityEnd.map((row) => row.objectId)).size, 7);
  assert.equal(new Set(identityEnd.map((row) => row.label)).size, 7);
  assert.ok(identityEnd.every((row) => row.label && /^T\d\d$/.test(row.objectId)));
  assert.equal(full.length, 3);
  for (const { edge, points } of full) assert.equal(points.length, edge.points.length);
  assert.equal(new Set(graph.edges.map((e) => e.id)).size, 7);
  assert.ok(residualM(3) < 1e-12 && residualM(4) < 1e-12);
  assert.equal(JSON.stringify(level0Point([70, 110])), JSON.stringify([2680, 2040]));
  assert.equal(JSON.stringify(level0Point([0, 0])), JSON.stringify([2400, 1600]));
  console.log(
    `PASS: ${plans.length} stories / ${frames} deterministic frames / ${native} native lifetimes; connected trace and held-out rigid witnesses`,
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
