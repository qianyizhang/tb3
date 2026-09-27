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
    vesselCases,
    vesselReference,
    vesselReveal,
    vesselOutput,
    vesselSliceIndex,
    vesselNodePixel,
    vesselVisibleNodes,
    pilotGeometry,
    pilotTrace,
    pilotReference,
    pilotOutput,
    pilotReveal,
    pilotSlabIndex,
    resectCase,
    resectReference,
    resectProjection,
    resectReveal,
    resectSweepIndex,
    resectTeachingOutput,
    identityRows,
    curationRows,
    curationReference,
    respiratory,
    supportRows,
    objectiveSamples,
    analysisRevealed,
    respiratoryRows,
    respiratoryReference,
    respiratoryOutput,
    q06Error,
    planePoint,
    planePixels,
    screenRows,
    screenReference,
    prototypeRows,
    prototypeObjects,
    prototypeVocabulary,
    prototypeDisplay,
    mixedTissueView,
    mixedTissue,
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
      materials = new Set(),
      textures = new Set();
    parent.traverse((o) => {
      if (o.geometry) geometries.add(o.geometry);
      if (o.material) materials.add(o.material);
      if (o.material?.map) textures.add(o.material.map);
    });
    let disposed = 0;
    for (const resource of [...geometries, ...materials, ...textures])
      resource.addEventListener('dispose', () => disposed++);
    content.dispose();
    content.dispose();
    assert.equal(parent.children.length, 0);
    assert.equal(disposed, geometries.size + materials.size + textures.size);
    assert.throws(() => content.update(sampleStory(plan, 0)));
  }
  const analysisPlan = plans.find((p) => p.recipe === 'registration-analysis-v1');
  assert.equal(analysisRevealed(sampleStory(analysisPlan, 0)), false);
  assert.equal(
    analysisRevealed(sampleStory(analysisPlan, analysisPlan.beats[1].endFrame - 1)),
    true,
  );
  assert.ok(Math.abs(supportRows(0)[3].distance - 18.99374121165789) < 1e-10);
  assert.ok(supportRows(1).every((r) => r.distance === 0));
  assert.ok(supportRows(0.5).every((r, i) => r.distance <= supportRows(0)[i].distance));
  const fullCurve = objectiveSamples('q01', 1);
  assert.equal(fullCurve.length, 101);
  assert.equal(fullCurve[0].t, 0);
  assert.equal(fullCurve[100].t, 1);
  assert.ok(Math.abs(fullCurve[0].score - 0.2691879476) < 1e-9);
  assert.ok(Math.abs(fullCurve[100].score - 0.5876808912) < 1e-9);
  assert.equal(JSON.stringify(objectiveSamples('q01', 0)), JSON.stringify([fullCurve[0]]));
  const vesselPlan = plans.find((p) => p.recipe === 'vessel-source-v1');
  assert.ok(isPlanarStory(vesselPlan));
  assert.equal(vesselReveal(sampleStory(vesselPlan, 0)), false);
  assert.equal(vesselOutput(sampleStory(vesselPlan, 0)), null);
  const vs = vesselPlan.beats.find((b) => b.scene === 'states');
  assert.equal(vesselReveal(sampleStory(vesselPlan, vs.startFrame)), false);
  assert.equal(vesselReveal(sampleStory(vesselPlan, vs.endFrame - 1)), true);
  const vi = vesselPlan.beats.find((b) => b.scene === 'inspect');
  assert.equal(vesselSliceIndex(sampleStory(vesselPlan, vi.startFrame).scan), 0);
  assert.equal(vesselSliceIndex(sampleStory(vesselPlan, vi.endFrame - 1).scan), 13);
  assert.equal(vesselSliceIndex(-1), 0);
  assert.equal(vesselSliceIndex(2), 13);
  const vo = vesselPlan.beats.find((b) => b.scene === 'admission');
  assert.equal(vesselOutput(sampleStory(vesselPlan, vo.startFrame)), null);
  const result = vesselOutput(sampleStory(vesselPlan, vo.endFrame - 1));
  assert.equal(result.admitted_defect_fixtures, 0);
  assert.equal(result.local_model_trials, 0);
  assert.ok(result.source_candidates.every((c) => c.status === 'source_candidate_only'));
  for (const [i, c] of vesselCases.entries()) {
    for (const n of vesselReference[i].node_entries) {
      const reconstructed = c.affine_ras_mm
        .slice(0, 3)
        .map((row) => row[3] + row.slice(0, 3).reduce((sum, v, j) => sum + v * n.native_ijk[j], 0));
      assert.ok(reconstructed.every((v, j) => Math.abs(v - n.ras_mm[j]) < 1e-10));
    }
    for (const n of vesselVisibleNodes(i)) {
      const p = vesselNodePixel(c, n);
      assert.ok(p.u >= -0.5 && p.u < c.mip.width - 0.5);
      assert.ok(p.v > -0.5 && p.v <= c.mip.height - 0.5);
    }
    assert.ok(vesselVisibleNodes(i).length < vesselReference[i].node_entries.length);
    const ref = vesselReference[i];
    for (const side of ['left', 'right']) {
      assert.equal(ref.edges[side === 'left' ? 'L-Pcom' : 'R-Pcom'], ref.pcoms[side].components_26);
    }
  }
  for (const p of vesselCases[1].native) {
    const c = vesselCases[1],
      ijk = [...c.roi_origin_ijk];
    ijk[1] += c.roi_size_ijk[1] - 1;
    ijk[2] = p.k;
    p.origin_world_mm.forEach((v, axis) => {
      const row = c.affine_ras_mm[axis];
      assert.ok(
        Math.abs(v - row[3] - ijk.reduce((sum, coord, j) => sum + coord * row[j], 0)) < 1e-10,
      );
      assert.equal(p.dx_world_mm[axis], row[0]);
      assert.equal(p.dy_world_mm[axis], -row[1]);
    });
  }
  const pilotPlan = plans.find((p) => p.recipe === 'resect-pilot-v1');
  assert.ok(isPlanarStory(pilotPlan));
  assert.equal(pilotOutput(sampleStory(pilotPlan, 0)), null);
  assert.equal(pilotReveal(sampleStory(pilotPlan, 0)), false);
  const pb = pilotPlan.beats.find((b) => b.scene === 'reference');
  assert.equal(pilotReveal(sampleStory(pilotPlan, pb.startFrame)), false);
  assert.equal(pilotReveal(sampleStory(pilotPlan, pb.endFrame - 1)), true);
  const pa = pilotOutput(sampleStory(pilotPlan, pb.endFrame - 1));
  const dist = (a, b) => Math.hypot(...a.map((v, i) => v - b[i]));
  pilotReference.cases.forEach((ref, i) => {
    assert.ok(
      Math.abs(dist(pa[i].us_world_mm, ref.reference_world_mm) - ref.final_error_mm) < 1e-12,
    );
    for (const plane of pilotGeometry[i].modalities.us.ras) {
      const p = resectProjection(plane, ref.reference_world_mm);
      const initial = resectProjection(plane, ref.initial_world_mm);
      const recovered = Math.hypot((p.u - initial.u) * 0.5, (p.v - initial.v) * 0.5, p.normal_mm);
      assert.ok(Math.abs(recovered - ref.initial_error_mm) < 1e-10);
    }
  });
  assert.ok(
    Math.abs(
      dist(pilotTrace.cue_world_mm, pilotReference.cases[1].reference_world_mm) -
        pilotReference.cue_error_mm,
    ) < 1e-12,
  );
  assert.ok(pilotReference.cue_error_mm < pilotReference.cases[1].final_error_mm);
  assert.deepEqual([pilotSlabIndex(-1), pilotSlabIndex(0.5), pilotSlabIndex(2)], [0, 2, 4]);
  assert.equal(pilotReveal(sampleStory(pilotPlan, 0)), false, 'Reverse seeking removes reference');
  const resectPlan = plans.find((p) => p.recipe === 'resect-correspondence-v1');
  assert.ok(isPlanarStory(resectPlan));
  const resectStart = sampleStory(resectPlan, 0);
  assert.equal(resectReveal(resectStart), false);
  assert.equal(resectTeachingOutput(resectStart), null);
  const rb = resectPlan.beats.find((b) => b.scene === 'reference');
  assert.equal(resectReveal(sampleStory(resectPlan, rb.startFrame)), false);
  assert.equal(resectReveal(sampleStory(resectPlan, rb.endFrame - 1)), true);
  const outputControl = resectTeachingOutput(sampleStory(resectPlan, rb.endFrame - 1));
  const affine = resectCase.modalities.us.affine;
  const mapped = affine
    .slice(0, 3)
    .map(
      (row) =>
        row[3] + row.slice(0, 3).reduce((sum, v, i) => sum + v * outputControl.us_voxel_ijk[i], 0),
    );
  assert.ok(mapped.every((v, i) => Math.abs(v - resectCase.query_world_mm[i]) < 1e-10));
  assert.equal(outputControl.confidence, 0);
  for (const key of ['mri', 'us'])
    for (const plane of resectCase.modalities[key].ras) {
      const projected = resectProjection(plane, resectCase.query_world_mm);
      assert.ok(
        Math.abs(projected.u - 48) < 1e-10 &&
          Math.abs(projected.v - 48) < 1e-10 &&
          Math.abs(projected.normal_mm) < 1e-10,
      );
      const target = resectProjection(plane, resectReference[1].target_world_mm);
      const distance = Math.hypot((target.u - 48) * 0.5, (target.v - 48) * 0.5, target.normal_mm);
      assert.ok(Math.abs(distance - resectReference[1].initial_error_mm) < 1e-10);
    }
  const oblique = { origin_world_mm: [1, 2, 3], dx_world_mm: [1, 0, 0], dy_world_mm: [0.5, 1, 0] };
  const projected = resectProjection(oblique, [6, 6, 5]);
  assert.ok(
    Math.abs(projected.u - 3) < 1e-10 &&
      Math.abs(projected.v - 4) < 1e-10 &&
      Math.abs(projected.normal_mm - 2) < 1e-10,
  );
  assert.equal(resectSweepIndex(-1), 0);
  assert.equal(resectSweepIndex(0.5), 6);
  assert.equal(resectSweepIndex(2), 12);
  assert.equal(
    resectReveal(sampleStory(resectPlan, 0)),
    false,
    'Reverse seek hides manual references',
  );
  const respiratoryPlan = plans.find((p) => p.recipe === 'respiratory-v1');
  assert.ok(
    respiratoryRows(sampleStory(respiratoryPlan, 0)).every(
      (r) => r.point === null && r.reference === null,
    ),
  );
  const referenceBeat = respiratoryPlan.beats.find((b) => b.scene === 'reference');
  assert.ok(
    respiratoryRows(sampleStory(respiratoryPlan, referenceBeat.startFrame)).every(
      (r) => r.point && !r.reference,
    ),
  );
  assert.equal(
    respiratoryRows(sampleStory(respiratoryPlan, referenceBeat.endFrame - 1)).filter(
      (r) => r.error > 5,
    ).length,
    1,
  );
  assert.ok(Math.abs(q06Error - 6.411513081948768) < 1e-12);
  for (const view of Object.values(respiratory.views)) {
    for (const [i, uv] of view.pixels_uv.entries()) {
      const world = planePoint(view.plane, ...uv);
      assert.ok(world.every((v, j) => Math.abs(v - view.source_world_mm[i][j]) < 1e-10));
      assert.ok(planePixels(view.plane, world).every((v, j) => Math.abs(v - uv[j]) < 1e-10));
    }
  }
  const parentCT = new Group(),
    ct = nativeFactory(respiratoryPlan)(parentCT);
  ct.update(sampleStory(respiratoryPlan, referenceBeat.endFrame - 1));
  const revealedCT = [];
  parentCT.traverse((o) => {
    if (o.isLine && o.visible) revealedCT.push(o);
  });
  assert.equal(revealedCT.length, 4, 'Residual and three radius circles');
  ct.update(sampleStory(respiratoryPlan, 0));
  assert.ok(
    revealedCT.every((o) => !o.visible),
    'Reverse seek removes reference geometry',
  );
  ct.dispose();
  const curation = plans.find((p) => p.recipe === 'anatomy-curation-v1');
  assert.ok(curationRows(sampleStory(curation, 0)).every((r) => r.source === null));
  const revealed = curationRows(sampleStory(curation, curation.beats[1].endFrame - 1));
  assert.equal(revealed.filter((r) => r.source === 'T13').length, 1);
  const selected = curationRows(sampleStory(curation, curation.beats[2].endFrame - 1));
  assert.equal(selected.length, 3);
  assert.equal(selected.find((r) => r.selected).source, 'T10');
  assert.ok(
    Math.abs(
      selected.find((r) => r.selected).volume_ml /
        ((selected[0].volume_ml + selected[2].volume_ml) / 2) -
        0.3335910362925618,
    ) < 1e-12,
  );
  assert.equal(
    Object.values(curationReference).reduce((a, r) => a + r.multiset_correct, 0),
    145,
  );
  assert.equal(
    Object.values(curationReference).reduce((a, r) => a + r.fixed_correct, 0),
    128,
  );
  const full = traceEdges(1);
  const screen = plans.find((p) => p.recipe === 'mask-screen-v1');
  for (const beat of screen.beats) {
    const rows = screenRows(sampleStory(screen, beat.endFrame - 1));
    if (beat.channels.reference[1] === 0)
      assert.ok(rows.every((r) => r.source === null && !r.wrong));
    if (beat.channels.prediction[1] === 0) assert.ok(rows.every((r) => r.predicted === null));
    if (beat.scene === 'ribs-74') {
      assert.deepEqual(
        JSON.parse(JSON.stringify(rows.filter((r) => r.wrong).map((r) => [r.predicted, r.source]))),
        [
          ['rib_left_8', 'rib_left_9'],
          ['rib_left_9', 'rib_left_8'],
        ],
      );
      assert.ok(
        rows.every((r, i) => i === 0 || rows[i - 1].centroid_lps_mm[2] > r.centroid_lps_mm[2]),
      );
    }
    if (beat.scene === 'organs-32' && beat.channels.reference[1] === 1)
      assert.deepEqual(
        JSON.parse(JSON.stringify(rows.filter((r) => r.wrong).map((r) => [r.source, r.predicted]))),
        [['spleen', 'stomach']],
      );
  }
  const heldOut = screenReference.organ_baseline.rows;
  const featureExample = screenReference.feature_example;
  assert.equal(featureExample.features.length, 7);
  assert.equal(featureExample.training_cases.length, 7);
  assert.ok(!featureExample.training_cases.includes(32));
  assert.equal(featureExample.nearest_templates[0].label, 'stomach');
  assert.ok(
    featureExample.nearest_templates.every(
      (r, i) =>
        i === 0 || r.squared_distance > featureExample.nearest_templates[i - 1].squared_distance,
    ),
  );
  assert.equal(
    heldOut.reduce((sum, r) => sum + r.correct, 0),
    screenReference.organ_baseline.correct,
  );
  assert.equal(
    heldOut.reduce((sum, r) => sum + r.total, 0),
    screenReference.organ_baseline.total,
  );
  assert.equal(heldOut.filter((r) => r.all_correct).length, 0);
  const prototype = plans.find((plan) => plan.recipe === 'prototype-identity-v1');
  assert.ok(prototype, 'Exercise actual BR-011 prototype semantics');
  assert.equal(prototypeObjects.length, 17);
  assert.equal(prototypeVocabulary.length, 117);
  for (const beat of prototype.beats.filter((b) => b.channels.reveal[1] === 0))
    assert.ok(
      prototypeRows(sampleStory(prototype, beat.endFrame - 1)).every((row) => row.label === null),
    );
  const prototypeEnd = prototypeRows(sampleStory(prototype, prototype.durationFrames - 1));
  assert.equal(new Set(prototypeEnd.map((r) => r.objectId)).size, 17);
  assert.ok(prototypeEnd.every((r) => prototypeVocabulary.includes(r.label)));
  const inspection = prototype.beats.find(
    (b) => b.channels.focus[0] === 0 && b.channels.focus[1] === 1,
  );
  const holds = new Map();
  for (let f = inspection.startFrame; f < inspection.endFrame; f++) {
    const id = prototypeRows(sampleStory(prototype, f)).find((r) => r.selected).objectId;
    holds.set(id, (holds.get(id) ?? 0) + 1);
  }
  assert.equal(holds.size, 17);
  assert.ok(
    [...holds.values()].every((n) => n >= 24),
    'Each source object must hold for at least a second',
  );
  const a = prototypeObjects[0].points_lps_mm[0],
    b = prototypeObjects[1].points_lps_mm[0];
  const distance = (p, q) => Math.hypot(...p.map((v, i) => v - q[i]));
  assert.ok(Math.abs(distance(a, b) - distance(prototypeDisplay(a), prototypeDisplay(b))) < 1e-9);
  const mixed = plans.find((plan) => plan.recipe === 'mixed-tissue-v1');
  assert.ok(mixed, 'Exercise the mixed-tissue reference boundary');
  const noReference = mixedTissueView(sampleStory(mixed, 0));
  assert.equal(noReference.referenceVisible, false);
  assert.equal(noReference.witnessVisible, false);
  const planeSweep = mixed.beats.find(
    (b) => b.channels.plane[0] === 0 && b.channels.plane[1] === 1,
  );
  const planeFrames = new Map();
  for (let frame = planeSweep.startFrame; frame < planeSweep.endFrame; frame++) {
    const plane = mixedTissueView(sampleStory(mixed, frame)).slice.plane;
    planeFrames.set(plane, (planeFrames.get(plane) ?? 0) + 1);
  }
  assert.equal(planeFrames.size, 3);
  assert.ok(
    [...planeFrames.values()].every((count) => count >= 24),
    'Every inspection plane must hold for at least one second',
  );
  for (const beat of mixed.beats) {
    const view = mixedTissueView(sampleStory(mixed, beat.endFrame - 1));
    assert.equal(view.referenceVisible, beat.channels.reference[1] > 0);
    assert.equal(view.witnessVisible, beat.channels.witness[1] > 0);
  }
  for (const slice of mixedTissue.slices) {
    const [x, y] = slice.witness_pixel.map((v) => v - 0.5);
    const lps = slice.pixel_center_origin_lps_mm.map(
      (v, j) => v + x * slice.pixel_dx_lps_mm[j] + y * slice.pixel_dy_lps_mm[j],
    );
    assert.ok(Math.hypot(...lps.map((v, j) => v - mixedTissue.witness_lps_mm[j])) < 1e-8);
    assert.ok(
      slice.region_cells.includes('M74,74h1v1h-1z'),
      'Witness must lie in displayed reference',
    );
  }
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
