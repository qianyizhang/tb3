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
    dtiInput,
    dtiData,
    dtiReference,
    dtiReveal,
    dtiScalar,
    dtiFa,
    deflectometryReveal,
    deflectometryInput,
    deflectometryData,
    deflectometryReference,
    deflectometryPhase,
    deflectometrySag,
    fanBeamReveal,
    fanBeamInput,
    fanBeamData,
    fanBeamReference,
    fanBeamProject,
    dualEnergyReveal,
    dualEnergyInput,
    dualEnergyData,
    dualEnergyReference,
    dualEnergyRayPixel,
    dualEnergyExpected,
    ptychographyReveal,
    ptychographyInput,
    ptychographyData,
    ptychographyCorner,
    nlosReveal,
    nlosInputs,
    nlosContract,
    carsReveal,
    carsResidual,
    carsInput,
    carsContract,
    rexInputs,
    rexReference,
    rexContract,
    rexSelection,
    rexReveal,
    rexNativeIndex,
    automedInputs,
    automedReference,
    automedContract,
    automedSelection,
    bcerInputs,
    bcerContract,
    bcerSelection,
    bcerPixel,
    abraInputs,
    abraReference,
    abraSelection,
    abraPixel,
    abraLps,
    landmarkSource,
    landmarkOutputs,
    landmarkReference,
    landmarkWorld,
    landmarkProjection,
    landmarkSelection,
    cavityCases,
    cavityOutputs,
    cavityReferences,
    cavitySelection,
    cavitySectionPath,
    decodeCavity,
    revisedSource,
    revisedViews,
    revisedRef,
    revisedIndex,
    revisedReference,
    revisedOutput,
    ctNativePoint,
    recoveredIdentities,
    sizeSummary,
    ctSource,
    ctVisits,
    ctReference,
    ctFrameIndex,
    ctShowReference,
    ctShowOutput,
    ctEdges,
    ctEligibleGroups,
    mriSource,
    mriP02,
    mriP03,
    mriRef,
    mriPhaseIndex,
    mriShowReference,
    mriShowOutput,
    percentChange,
    projectedMethodBox,
    tigerSource,
    tigerViews,
    tigerRef,
    tigerReveal,
    tissueArea,
    pooledDensity,
    slidePoint,
    hubmapSource,
    hubmapDetail,
    hubmapTiles,
    hubmapRef,
    hubmapReveal,
    slideFit,
    toLocal,
    toLevel0,
    profileArea,
    hubmapRows,
    brainCases,
    brainRefs,
    brainResult,
    brainReveal,
    brainOutput,
    brainSelection,
    brainPlaneFit,
    brainPixel,
    airwayCases,
    airwayOutput,
    airwayReference,
    airwayReveal,
    airwayReturned,
    airwayCaseIndex,
    airwaySliceIndex,
    airwayAngleIndex,
    airwayRouteIndex,
    airwayDisplay,
    airwayBounds,
    airwayCPRRowEdges,
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
  const stitched = cavitySectionPath([
    [
      [1, 0],
      [1, 1],
    ],
    [
      [0, 0],
      [1, 0],
    ],
    [
      [0, 1],
      [0, 0],
    ],
    [
      [1, 1],
      [0, 1],
    ],
  ]);
  assert.equal((stitched.match(/M/g) || []).length, 1);
  assert.equal((stitched.match(/L/g) || []).length, 4);
  const {
    dentalSelection,
    dentalSource,
    dentalOutputs,
    dentalReference,
    dentalGates,
    dentalSwapId,
    dentalDisplayedItems,
  } = await loadFrontend('expansion_fixture.mjs');
  const {
    aneurysmSelection,
    aneurysmCases,
    aneurysmOutputs,
    aneurysmReference,
    aneurysmPixel,
    aneurysmDepths,
    calibrationSelection,
    calibrationSource,
    calibrationOutput,
    calibrationReference,
    dentalV3Selection,
    dentalV3Reference,
    dentalV3Outputs,
    dentalV3Stages,
    dentalV2Selection,
    dentalV2Reference,
    dentalV2Stages,
    dentalV2Outputs,
  } = await loadFrontend('expansion_fixture.mjs');
  const {
    localizedVisits,
    localizedSelection,
    localizedPixel,
    localizedReference,
    localizedOutput,
  } = await loadFrontend('expansion_fixture.mjs');
  const {
    contextInputs,
    contextOutput,
    contextReference,
    contextFields,
    contextSelection,
    contextPixel,
  } = await loadFrontend('expansion_fixture.mjs');
  const cp = plans.find((p) => p.recipe === 'ct-context-v1');
  assert.ok(cp);
  assert.deepEqual(JSON.parse(JSON.stringify(contextOutput.counts)), {
    observed: 0,
    inferred: 2,
    unknown: 7,
  });
  assert.deepEqual(
    Array.from(contextFields, (f) => f[0]),
    Object.keys(contextOutput.fields),
  );
  assert.equal(contextInputs.images.length, 4);
  for (const v of contextInputs.images) {
    assert.equal(v.width, v.bounds[1] - v.bounds[0]);
    assert.equal(v.height, v.bounds[3] - v.bounds[2]);
    if (v.point) {
      const [x, y] = contextPixel(v, v.point);
      assert.ok(x > 0 && x < v.width && y > 0 && y < v.height);
    }
  }
  assert.deepEqual(
    Array.from(contextReference.diagnostics, (d) => d.contract_valid),
    [true, true, false, false],
  );
  assert.ok(contextReference.diagnostics.every((d) => d.scientific_score === null));
  assert.deepEqual(
    Array.from(contextReference.rewards, (d) => d.reward),
    [1, 1, 0],
  );
  const contextFieldsBeat = cp.beats.find((b) => b.scene === 'fields'),
    seen = new Set();
  for (let f = contextFieldsBeat.startFrame; f < contextFieldsBeat.endFrame; f++)
    seen.add(contextSelection(sampleStory(cp, f)).field);
  assert.deepEqual([...seen], [0, 1, 2, 3, 4, 5, 6, 7, 8]);
  const contextRevealBeat = cp.beats.find((b) => b.scene === 'reference');
  for (let f = 0; f <= contextRevealBeat.startFrame; f++)
    assert.equal(contextSelection(sampleStory(cp, f)).reference, false);
  assert.equal(contextSelection(sampleStory(cp, contextRevealBeat.endFrame - 1)).reference, true);
  assert.equal(contextSelection(sampleStory(cp, 0)).output, false);
  const { historySource, historyReference, historySelection } =
    await loadFrontend('expansion_fixture.mjs');
  const historyPlan = plans.find((p) => p.recipe === 'history-sourcing-v1');
  assert.ok(historyPlan);
  const counts = historySource.counts;
  assert.equal(
    counts.indexed_records - counts.automatic_reviews - counts.other_long_titles,
    counts.navigable_records,
  );
  assert.equal(new Set(historySource.excerpts.map((e) => e.raw_record_sha256)).size, 8);
  assert.equal(new Set(historySource.excerpts.map((e) => e.session_id)).size, 6);
  assert.equal(historySource.candidates[4].task, null);
  assert.equal(historySource.candidates[4].endpoint, 'Not tested');
  assert.equal(historyReference.tasks.length, 4);
  assert.equal(
    historyReference.tasks.reduce((n, t) => n + t.source_files, 0),
    76,
  );
  for (const t of historyReference.tasks) {
    assert.equal(t.trials.length, 3);
    assert.ok(t.trials.every((r) => r.task_checksum === t.task_checksum));
    assert.equal(t.trials.find((r) => r.agent === 'codex').reward, 1);
    assert.equal(t.trials.find((r) => r.agent === 'oracle').reward, 1);
    assert.equal(t.trials.find((r) => r.agent === 'nop').reward, 0);
  }
  for (const [scene, key, count] of [
    ['excerpts', 'excerpt', 8],
    ['candidates', 'candidate', 5],
    ['lineage', 'task', 4],
    ['controls', 'task', 4],
  ]) {
    const b = historyPlan.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let f = b.startFrame; f < b.endFrame; f++)
      seen.add(historySelection(sampleStory(historyPlan, f))[key]);
    assert.deepEqual(
      [...seen],
      Array.from({ length: count }, (_, i) => i),
    );
  }
  const historyReveal = historyPlan.beats.find((b) => b.scene === 'reference');
  for (let f = 0; f <= historyReveal.startFrame; f++)
    assert.equal(historySelection(sampleStory(historyPlan, f)).reference, false);
  assert.equal(
    historySelection(sampleStory(historyPlan, historyReveal.endFrame - 1)).reference,
    true,
  );
  const { mriInputs, mriOutput, mriSelection, mriSlot, mriPoint, mriCorners, mriGray } =
    await loadFrontend('expansion_fixture.mjs');
  const mrPlan = plans.find((p) => p.recipe === 'mri-importer-v1');
  assert.ok(mrPlan);
  assert.equal(mriSelection(sampleStory(mrPlan, 0)).reference, false);
  assert.equal(mriSelection(sampleStory(mrPlan, 0)).output, false);
  for (const [scene, key, count] of [
    ['association', 'frame', 12],
    ['geometry', 'corner', 8],
  ]) {
    const b = mrPlan.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let f = b.startFrame; f < b.endFrame; f++)
      seen.add(mriSelection(sampleStory(mrPlan, f))[key]);
    assert.deepEqual(
      [...seen],
      Array.from({ length: count }, (_, i) => i),
    );
  }
  const mrOutputBeat = mrPlan.beats.find((b) => b.scene === 'outputs');
  assert.deepEqual(
    Array.from(
      mriInputs.cases[1].rows[mriSelection(sampleStory(mrPlan, mrOutputBeat.endFrame - 1)).frame]
        .target,
    ),
    [0, 0, 0],
  );
  const mrReveal = mrPlan.beats.find((b) => b.scene === 'reference');
  assert.equal(mriSelection(sampleStory(mrPlan, mrReveal.startFrame)).reference, false);
  assert.equal(mriSelection(sampleStory(mrPlan, mrReveal.endFrame - 1)).reference, true);
  for (let ci = 0; ci < mriInputs.cases.length; ci++) {
    const c = mriInputs.cases[ci],
      answer = mriOutput.cases[ci];
    assert.equal(new Set(c.rows.map((f) => mriSlot(f, c.shape))).size, c.rows.length);
    for (const f of c.rows) {
      assert.deepEqual(f.pixels, answer.pixels[f.target[0]][f.target[1]][f.target[2]]);
      assert.equal(answer.temporal_indices[f.target[0]], f.time);
      assert.equal(answer.echo_ms[f.target[1]], f.echo_ms);
      assert.ok(
        mriPoint(answer.affine_lps, [0, 0, f.target[2]]).every(
          (v, i) => Math.abs(v - f.position_lps[i]) < 1e-10,
        ),
      );
    }
    assert.equal(mriCorners(c.shape).length, 8);
    assert.ok(
      mriCorners(c.shape).some((p) =>
        p.every((v, i) => v === [c.shape[4] - 1, c.shape[3] - 1, c.shape[2] - 1][i]),
      ),
    );
  }
  assert.equal(mriGray(-3000), 0);
  assert.equal(mriGray(3000), 255);
  assert.equal(mriGray(0), 128);
  const localizedPlan = plans.find((p) => p.recipe === 'localized-ct-v1');
  assert.ok(localizedPlan);
  assert.equal(localizedSelection(sampleStory(localizedPlan, 0)).reference, false);
  assert.equal(localizedSelection(sampleStory(localizedPlan, 0)).output, false);
  for (const [scene, key, expected] of [
    ['axial', 'axial', [0, 1, 2, 3]],
    ['orthogonal', 'orthogonal', ['i-0', 'i-1', 'i-2', 'j-0', 'j-1', 'j-2']],
    ['serial', 'serial', Array.from({ length: 12 }, (_, i) => i)],
  ]) {
    const b = localizedPlan.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let f = b.startFrame; f < b.endFrame; f++)
      seen.add(localizedSelection(sampleStory(localizedPlan, f))[key]);
    assert.deepEqual([...seen], expected);
  }
  const localizedReveal = localizedPlan.beats.find((b) => b.scene === 'reference');
  assert.equal(
    localizedSelection(sampleStory(localizedPlan, localizedReveal.startFrame)).reference,
    false,
  );
  assert.equal(
    localizedSelection(sampleStory(localizedPlan, localizedReveal.endFrame - 1)).reference,
    true,
  );
  for (const visit of Object.values(localizedVisits))
    for (const p of Object.values(visit.views)) {
      const pos = localizedPixel(p, visit.native_ijk, visit.spacing_mm);
      assert.ok(pos.x > 0 && pos.x < p.width && pos.y > 0 && pos.y < p.height);
      assert.equal(pos.x + p.bounds[2 * p.u_axis] - 0.5, visit.native_ijk[p.u_axis]);
      assert.equal(
        p.flip_v ? p.bounds[2 * p.v_axis + 1] - pos.y - 0.5 : pos.y + p.bounds[2 * p.v_axis] - 0.5,
        visit.native_ijk[p.v_axis],
      );
      assert.equal(pos.offset, (p.index - visit.native_ijk[p.axis]) * visit.spacing_mm[p.axis]);
      assert.equal(p.extent_mm[0], p.width * visit.spacing_mm[p.u_axis]);
      assert.equal(p.extent_mm[1], p.height * visit.spacing_mm[p.v_axis]);
    }
  assert.equal(localizedOutput.events.groups.length, 0);
  assert.ok(localizedOutput.judgments.candidates.every((r) => r.judgment === 'normal_or_benign'));
  assert.equal(localizedReference.controls['rejected-with-oracle-masks'].valid, true);
  assert.equal(localizedReference.controls['rejected-with-oracle-masks'].detected, 2);
  const aneurysmPlan = plans.find((p) => p.recipe === 'aneurysm-localization-v1');
  assert.ok(aneurysmPlan);
  assert.equal(aneurysmSelection(sampleStory(aneurysmPlan, 0)).output, false);
  assert.equal(aneurysmSelection(sampleStory(aneurysmPlan, 0)).reference, false);
  for (const [scene, field, expected] of [
    ['slabs', 'slab', Array.from({ length: 12 }, (_, i) => i)],
    ['depth', 'depth', Array.from(aneurysmDepths)],
  ]) {
    const beat = aneurysmPlan.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let f = beat.startFrame; f < beat.endFrame; f++)
      seen.add(aneurysmSelection(sampleStory(aneurysmPlan, f))[field]);
    assert.deepEqual([...seen], expected);
  }
  const aneurysmReveal = aneurysmPlan.beats.find((b) => b.scene === 'reference');
  assert.equal(
    aneurysmSelection(sampleStory(aneurysmPlan, aneurysmReveal.startFrame)).reference,
    false,
  );
  assert.equal(
    aneurysmSelection(sampleStory(aneurysmPlan, aneurysmReveal.endFrame - 1)).reference,
    true,
  );
  const aneurysmPoint = aneurysmOutputs.cases.n02.answer.aneurysms[0];
  for (const id of ['n01', 'n02', 'n03']) {
    assert.equal(aneurysmOutputs.cases[id].answer.aneurysms.length, id === 'n02' ? 1 : 0);
    assert.equal(aneurysmOutputs.cases[id].trace.annotation_inventory_exposed, id === 'n03');
  }
  for (let axis = 0; axis < 3; axis++) {
    const plane = aneurysmCases.n02.views[`point-${axis}`];
    const pixel = aneurysmPixel(plane, aneurysmPoint, aneurysmCases.n02.spacing_mm);
    assert.equal(pixel.offset_mm, 0);
    assert.ok(pixel.x > 0 && pixel.x < plane.width && pixel.y > 0 && pixel.y < plane.height);
    assert.equal(pixel.x + plane.bounds[plane.u_axis * 2] - 0.5, aneurysmPoint[plane.u_axis]);
    assert.equal(plane.bounds[plane.v_axis * 2 + 1] - pixel.y - 0.5, aneurysmPoint[plane.v_axis]);
  }
  const aneurysmDistance = Math.hypot(
    ...aneurysmPoint.map(
      (p, a) =>
        (p - aneurysmReference.cases.n02.regions[0].center_ijk[a]) *
        aneurysmCases.n02.spacing_mm[a],
    ),
  );
  assert.ok(Math.abs(aneurysmDistance - aneurysmReference.n02_point_to_centroid_mm) < 1e-12);
  assert.equal(aneurysmReference.n02_inside_source_region, true);
  const slabCoverage = Array(aneurysmCases.n02.shape[2]).fill(0);
  for (let i = 0; i < 12; i++) {
    const b = aneurysmCases.n02.views[`slab-${i}`].bounds;
    for (let k = b[4]; k < b[5]; k++) slabCoverage[k]++;
  }
  assert.ok(
    slabCoverage.every((n) => n === 1),
    'Every native axial slice belongs to one slab',
  );
  for (const [key, ref] of Object.entries(aneurysmReference.views)) {
    const [id, name] = key.split('/'),
      plane = aneurysmCases[id].views[name];
    assert.ok(ref.weak.pixels <= ref.accepted.pixels);
    for (const region of [ref.weak, ref.accepted])
      for (const path of region.paths)
        for (const [x, y] of path)
          assert.ok(
            x >= 0 && y >= 0 && x <= plane.width && y <= plane.height,
            key + ' contour bounds',
          );
  }
  const calPlan = plans.find((p) => p.recipe === 'segmentation-calibration-v1');
  assert.ok(calPlan);
  const calStart = calibrationSelection(sampleStory(calPlan, 0));
  assert.equal(calStart.output, false);
  assert.equal(calStart.reveal, false);
  assert.equal(calStart.box, false);
  for (const [scene, field, expected] of [
    ['sampling', 'sample', ['pancreas_q25', 'pancreas_q50', 'pancreas_q75']],
    [
      'sensitivity',
      'sample',
      ['liver', 'kidney_right', 'gallbladder', 'pancreas', 'adrenal_gland_right', 'duodenum'].map(
        (o) => o + '_q50',
      ),
    ],
    ['duodenum', 'condition', ['tight', 'loose']],
    ['backend', 'sample', ['adrenal_gland_right_q50', 'liver_q25']],
  ]) {
    const b = calPlan.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let frame = b.startFrame; frame < b.endFrame; frame++)
      seen.add(calibrationSelection(sampleStory(calPlan, frame))[field]);
    assert.deepEqual([...seen], expected);
  }
  for (const row of calibrationReference.replays) {
    const view = calibrationSource.views[row.id],
      [x0, y0, x1, y1] = view.detail_bounds_xyxy;
    const mask = calibrationOutput.views[row.id][row.tag][row.condition];
    assert.equal(mask.pixels, row.pred_pixels);
    for (const path of mask.paths)
      for (const [x, y] of path)
        assert.ok(x >= x0 && x <= x1 && y >= y0 && y <= y1, 'Crop clips retained mask');
    assert.ok(
      Math.abs((2 * row.intersection) / (row.pred_pixels + row.gt_pixels) - row.dice) < 1e-12,
    );
  }
  for (const tag of ['sam2-mps', 'lite-mps', 'sam2-cpu'])
    for (const condition of ['tight', 'loose']) {
      const rows = calibrationReference.replays.filter(
        (r) => r.tag === tag && r.condition === condition,
      );
      const mean = rows.reduce((n, r) => n + r.dice, 0) / rows.length;
      assert.ok(Math.abs(mean - calibrationReference.aggregates[tag][condition].mean_dice) < 1e-12);
    }
  const refBeat = calPlan.beats.find((b) => b.scene === 'reference');
  assert.equal(calibrationSelection(sampleStory(calPlan, refBeat.startFrame)).reveal, false);
  assert.equal(calibrationSelection(sampleStory(calPlan, refBeat.endFrame - 1)).reveal, true);
  const v3Plan = plans.find((p) => p.recipe === 'dental-v3-v1');
  assert.ok(v3Plan);
  const v3Start = dentalV3Selection(sampleStory(v3Plan, 0));
  assert.equal(v3Start.reveal, false);
  assert.equal(v3Start.helper, false);
  assert.equal(v3Start.output, false);
  for (const [scene, field, expected] of [
    ['pulp-reach', 'stage', Array.from(dentalV3Stages)],
    ['pulp-gain', 'gainView', ['pulp-122-j43', 'pulp-122-j50']],
    ['pulp-loss', 'lossView', ['pulp-127-j156', 'pulp-127-j160', 'pulp-127-j162']],
    ['canal-crop', 'canalView', ['canal-104-k201', 'canal-104-k204', 'canal-104-k207']],
    ['canal-extent', 'projection', ['canal-4-along-i', 'canal-4-along-j', 'canal-4-along-k']],
  ]) {
    const beat = v3Plan.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let frame = beat.startFrame; frame < beat.endFrame; frame++)
      seen.add(dentalV3Selection(sampleStory(v3Plan, frame))[field]);
    assert.deepEqual([...seen], expected);
  }
  const v3Transfer = v3Plan.beats.find((b) => b.scene === 'transfer');
  assert.equal(dentalV3Selection(sampleStory(v3Plan, v3Transfer.startFrame)).transfer, 0);
  assert.equal(dentalV3Selection(sampleStory(v3Plan, v3Transfer.endFrame - 1)).transfer, 1);
  assert.equal(dentalV3Selection(sampleStory(v3Plan, v3Transfer.endFrame - 1)).reveal, false);
  assert.equal(dentalV3Outputs.registration.atlas_plane_exactly_reproduced, true);
  assert.equal(dentalV3Outputs.registration.warped_ct_plane_exactly_reproduced, true);
  assert.equal(dentalV3Outputs.registration.optimization_rerun, false);
  const reach = dentalV3Reference.pulp_stages.find((r) => r.label === 127);
  assert.ok(
    reach.after_component_filter.intersection <= reach.retained_or_geometry_eligible.intersection,
  );
  assert.ok(reach.retained_or_geometry_eligible.intersection < reach.gt_voxels_full_volume);
  assert.equal(reach.gt_voxels_in_tooth_crop, reach.gt_voxels_full_volume);
  const crop = dentalV3Reference.canal_stages.find((r) => r.label === 104);
  assert.equal(crop.gt_voxels_in_search_crop, 0);
  assert.equal(crop.final.intersection, 0);
  assert.notEqual(crop.prior.prediction_voxels, crop.final.prediction_voxels);
  const four = dentalV3Reference.metrics.map((m) => ({
    dice: m.score.per_label.find((r) => r.id === 4).dice,
    hd95: m.score.canal_surface_metrics['4'].hd95_mm,
  }));
  assert.ok(four[1].dice > four[0].dice && four[1].hd95 > four[0].hd95);
  for (let i = 0; i < 2; i++) {
    const c = dentalV3Reference.conditions[i],
      m = dentalV3Reference.metrics[i].score;
    const active = m.per_label.filter((r) => r.dice !== null);
    assert.equal(active.length, c.active_labels);
    assert.ok(
      Math.abs(active.reduce((sum, r) => sum + r.dice, 0) / active.length - c.original_macro_dice) <
        1e-12,
    );
  }
  const v2Plan = plans.find((p) => p.recipe === 'dental-v2-v1');
  assert.ok(v2Plan);
  const v2Start = dentalV2Selection(sampleStory(v2Plan, 0));
  assert.equal(v2Start.reveal, false);
  assert.equal(v2Start.helper, false);
  assert.equal(v2Start.output, false);
  for (const [scene, field, expected] of [
    ['pulp-clip', 'stage', Array.from(dentalV2Stages)],
    ['pulp-contents', 'pulpId', [116, 131]],
    ['canals', 'canalView', ['canals-145', 'canals-205']],
    ['small-canals', 'canalId', [103, 104]],
  ]) {
    const beat = v2Plan.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let frame = beat.startFrame; frame < beat.endFrame; frame++)
      seen.add(dentalV2Selection(sampleStory(v2Plan, frame))[field]);
    assert.deepEqual([...seen], expected);
  }
  const transfer = v2Plan.beats.find((b) => b.scene === 'transfer');
  assert.equal(dentalV2Selection(sampleStory(v2Plan, transfer.startFrame)).transfer, 0);
  assert.equal(dentalV2Selection(sampleStory(v2Plan, transfer.endFrame - 1)).transfer, 1);
  assert.equal(dentalV2Selection(sampleStory(v2Plan, transfer.endFrame - 1)).reveal, false);
  assert.equal(dentalV2Outputs.registration.atlas_plane_exactly_reproduced, true);
  const {
    before_true_overlap: before,
    after_true_overlap: after,
    removed_true_pulp_voxels: removed,
  } = dentalV2Reference.clipping;
  assert.equal(
    before - removed,
    after,
    'Saved exclusion preserves exact reference-retention accounting',
  );
  for (let i = 0; i < 2; i++) {
    const c = dentalV2Reference.conditions[i],
      m = dentalV2Reference.metrics[i].score;
    const active = m.per_label.filter((r) => r.dice !== null);
    assert.equal(active.length, c.active_labels);
    assert.ok(
      Math.abs(active.reduce((sum, r) => sum + r.dice, 0) / active.length - c.original_macro_dice) <
        1e-12,
    );
    const common = c.common_label_set.map((id) => m.per_label.find((r) => r.id === id).dice || 0);
    assert.ok(
      Math.abs(
        common.reduce((a, b) => a + b, 0) / common.length - c.posthoc_common_label_macro_dice,
      ) < 1e-12,
    );
    const detected = c.tooth_matches.filter((r) => r.dice >= 0.5);
    assert.equal(detected.length, c.identity_counts.detected);
    assert.equal(
      detected.filter((r) => r.correct_fdi).length,
      c.identity_counts.correct_among_detected,
    );
  }
  const dentalPlan = plans.find((p) => p.recipe === 'dental-original-v1');
  assert.ok(dentalPlan);
  const initialDental = dentalSelection(sampleStory(dentalPlan, 0));
  assert.equal(initialDental.output, false);
  assert.equal(initialDental.reveal, false);
  assert.equal(initialDental.key, 'input-f018');
  for (const [scene, field, expected] of [
    ['pulp', 'gate', Array.from(dentalGates)],
    ['canals', 'key', ['canals-145', 'canals-205']],
  ]) {
    const b = dentalPlan.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let f = b.startFrame; f < b.endFrame; f++)
      seen.add(dentalSelection(sampleStory(dentalPlan, f))[field]);
    assert.deepEqual([...seen], expected);
  }
  for (const id of Object.keys(dentalSource.labels).map(Number))
    assert.equal(dentalSwapId(dentalSwapId(id)), id, 'ID permutation must be an involution');
  for (const id of [0, 1, 2, 7, 8, 9, 10, 105]) assert.equal(dentalSwapId(id), id);
  assert.equal(dentalSwapId(11), 21);
  assert.equal(dentalSwapId(138), 148);
  const unchanged = dentalOutputs.views.identity.xhigh;
  const swapped = dentalDisplayedItems(unchanged, true);
  for (let i = 0; i < unchanged.length; i++) {
    assert.equal(swapped[i].paths, unchanged[i].paths, 'Diagnostic may not move contours');
    assert.equal(swapped[i].center, unchanged[i].center, 'Diagnostic may not move labels');
    assert.equal(swapped[i].pixels, unchanged[i].pixels);
  }
  for (const run of dentalReference.diagnostics) {
    const active = run.per_label.filter((r) => r.original_dice !== null);
    const diagnostic = run.per_label.filter((r) => r.lr_diagnostic_dice !== null);
    assert.equal(active.length, run.active_labels_original);
    assert.equal(diagnostic.length, run.active_labels_lr_diagnostic);
    assert.ok(
      Math.abs(
        active.reduce((s, r) => s + r.original_dice, 0) / active.length - run.original_macro,
      ) < 1e-12,
    );
    assert.ok(
      Math.abs(
        diagnostic.reduce((s, r) => s + r.lr_diagnostic_dice, 0) / diagnostic.length -
          run.fixed_lr_diagnostic_macro,
      ) < 1e-12,
    );
  }
  assert.deepEqual(
    Array.from(dentalReference.diagnostics, (r) => [
      r.active_labels_original,
      r.active_labels_lr_diagnostic,
    ]),
    [
      [70, 68],
      [70, 68],
      [62, 57],
    ],
  );
  const canals = dentalReference.diagnostics[2].per_label.filter((r) =>
    [3, 4, 103, 104, 105].includes(r.id),
  );
  assert.ok(canals.every((r) => r.gt_voxels > 0 && r.pred_voxels === 0));
  assert.deepEqual(
    Object.values(dentalOutputs.gate_description.overlap_counts),
    [850, 844, 1, 1, 0],
  );
  for (const p of Object.values(dentalSource.views)) {
    const [[u0, u1], [v0, v1]] = p.bounds_uv;
    assert.equal(u1 - u0, p.width);
    assert.equal(v1 - v0, p.height);
    const u = (u0 + u1 - 1) / 2,
      v = (v0 + v1 - 1) / 2,
      x = u - u0 + 0.5,
      y = v1 - v - 0.5;
    assert.equal(u0 + x - 0.5, u);
    assert.equal(v1 - y - 0.5, v);
  }
  const { ctOrganSelection, ctOrganSource, ctOrganOutputs, ctOrganReference } =
    await loadFrontend('expansion_fixture.mjs');
  const organPlan = plans.find((p) => p.recipe === 'ct-organ-v1');
  assert.ok(organPlan);
  assert.equal(ctOrganSelection(sampleStory(organPlan, 0)).output, false);
  assert.equal(ctOrganSelection(sampleStory(organPlan, 0)).reveal, false);
  for (const [scene, expected] of [
    ['polygon', [235, 236, 237, 238, 239, 240]],
    ['tool', [235, 236, 237, 238, 239, 240]],
    ['inventory', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
    ['regressions', [4, 7, 8]],
  ]) {
    const b = organPlan.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let frame = b.startFrame; frame < b.endFrame; frame++) {
      const v = ctOrganSelection(sampleStory(organPlan, frame));
      seen.add(['tool', 'polygon'].includes(scene) ? v.method.k : v.id);
    }
    assert.deepEqual([...seen], expected);
  }
  assert.deepEqual(
    Array.from(ctOrganOutputs.methods, (m) => m.polygon_explicit),
    [true, false, false, false, false, true],
  );
  assert.deepEqual(
    Array.from(ctOrganOutputs.methods, (m) => m.box_explicit),
    [true, false, false, false, false, true],
  );
  for (const m of ctOrganOutputs.methods) {
    const b = ctOrganSource.views[`method-${m.k}`].bounds_ij;
    assert.ok(Math.abs(m.box[0] + b[0][0] - 0.5 - m.native_image_box_xyxy[0]) < 1e-10);
    assert.ok(Math.abs(m.box[1] + 265 - b[1][1] - 0.5 - m.native_image_box_xyxy[1]) < 1e-10);
    assert.ok(m.tool_candidate.length && m.raw_polygon.length);
    const plane = ctOrganSource.views[`method-${m.k}`];
    for (const layer of [m.raw_polygon, m.tool_candidate, m.baseline_final, m.tool_final])
      for (const contour of layer)
        for (const [x, y] of contour)
          assert.ok(
            x > 0 && x < plane.width && y > 0 && y < plane.height,
            'method contour clipped by crop',
          );
    assert.ok(
      m.box[0] > 0 &&
        m.box[1] > 0 &&
        m.box[0] + m.box[2] < plane.width &&
        m.box[1] + m.box[3] < plane.height,
      'method prompt clipped by crop',
    );
  }
  const metrics = ctOrganReference.metrics;
  assert.equal(metrics.medium.per_label.length, 10);
  assert.equal(
    metrics.tool.per_label.filter((r, i) => r.dice > metrics.medium.per_label[i].dice).length,
    7,
  );
  assert.equal(ctOrganReference.overlap_voxels, 57);
  for (const m of Object.values(metrics))
    assert.ok(
      Math.abs(m.per_label.reduce((s, r) => s + r.dice, 0) / 10 - m.semantic_macro_dice) < 1e-12,
    );
  assert.equal(ctOrganReference.matched_macro.authored_polygon.n, 119);
  assert.equal(ctOrganReference.matched_macro.interpolated_shape.n, 372);
  const landmarkPlan = plans.find((p) => p.recipe === 'named-landmarks-v1');
  assert.ok(landmarkPlan);
  assert.equal(landmarkSelection(sampleStory(landmarkPlan, 0)).reveal, false);
  assert.equal(landmarkSelection(sampleStory(landmarkPlan, 0)).output, false);
  const partial = landmarkOutputs.partial;
  assert.equal(partial.sol.T5.status, 'out_of_fov');
  assert.equal(partial.sol.T5.ijk, null);
  assert.equal(landmarkReference.points.partial.T5.status, 'observed');
  assert.equal(landmarkReference.points.partial.T4.status, 'out_of_fov');
  const p = partial.terra.T4.ijk;
  const q = landmarkReference.points.partial.T5.ijk;
  const wp = landmarkWorld('partial', p),
    wq = landmarkWorld('partial', q);
  assert.ok(Math.abs(Math.hypot(...wp.map((v, i) => v - wq[i])) - 2.14) < 0.005);
  for (const plane of landmarkSource.views['partial-T5']) {
    const projected = landmarkProjection(plane, 'partial', p);
    const u = (projected.u - 0.5) * plane.step + plane.origin_uv[0];
    const v = (plane.height - projected.v - 0.5) * plane.step + plane.origin_uv[1];
    assert.ok(Math.abs(u - p[plane.u_axis]) < 1e-10);
    assert.ok(Math.abs(v - p[plane.v_axis]) < 1e-10);
    assert.equal(
      projected.offset,
      (p[plane.axis] - plane.index) * landmarkSource.cases.partial.spacing[plane.axis],
    );
  }
  const grade = landmarkReference.grades.partial.sol;
  assert.equal(grade.score.localized_visible, 12);
  assert.equal(grade.score.missed_visible, 1);
  assert.equal(grade.success_counts['5'], 4);
  const sweepBeat = landmarkPlan.beats.find((b) => b.scene === 'search');
  const visitedSlices = new Set();
  for (let frame = sweepBeat.startFrame; frame < sweepBeat.endFrame; frame++) {
    const state = landmarkSelection(sampleStory(landmarkPlan, frame));
    assert.equal(state.output, false);
    assert.equal(state.reveal, false);
    visitedSlices.add(state.planes[0].index);
  }
  assert.deepEqual(
    [...visitedSlices],
    Array.from(landmarkSource.views['partial-sweep'], (p) => p.index),
  );
  const cavityPlan = plans.find((p) => p.recipe === 'clinical-cavity-v1');
  assert.ok(cavityPlan);
  const inputState = sampleStory(cavityPlan, 0);
  assert.equal(inputState.output, 0);
  assert.equal(inputState.helper, 0);
  assert.equal(cavitySelection(inputState).reveal, false);
  for (const key of ['primary', 'patient', 'preserved']) {
    const data = cavityCases[key],
      output = cavityOutputs[key].mesh;
    assert.equal(data.frames, { primary: 18, patient: 35, preserved: 48 }[key]);
    assert.equal(output.frames, data.frames);
    assert.equal(cavityReferences[key].mesh.frames, data.frames);
    assert.deepEqual(decodeCavity(output).frames[0], decodeCavity(data.initial).frames[0]);
    const beat = cavityPlan.beats.find(
      (b) => b.scene === { primary: 'tracking', patient: 'patient', preserved: 'preserved' }[key],
    );
    const visited = new Set();
    for (let frame = beat.startFrame; frame < beat.endFrame; frame++) {
      const selection = cavitySelection(sampleStory(cavityPlan, frame));
      visited.add(selection.imageFrame);
      assert.equal(selection.frame, selection.imageFrame);
      assert.equal(selection.refFrame, selection.imageFrame);
      for (const plane of data.planes)
        assert.ok(plane.frames[selection.imageFrame].png.startsWith('data:image/png;base64,'));
    }
    assert.equal(visited.size, data.frames, 'Every native frame must appear');
  }
  const original = decodeCavity(cavityOutputs.primary.mesh);
  for (const scene of ['static', 'shift']) {
    const beat = cavityPlan.beats.find((b) => b.scene === scene);
    const visited = new Set();
    for (let frame = beat.startFrame; frame < beat.endFrame; frame++) {
      const selection = cavitySelection(sampleStory(cavityPlan, frame));
      const expected = scene === 'static' ? 0 : (selection.frame - 5 + 18) % 18;
      assert.equal(selection.imageFrame, expected);
      assert.deepEqual(
        decodeCavity(selection.output).frames[selection.frame],
        original.frames[expected],
      );
      assert.equal(
        selection.output.volume_ml[selection.frame],
        cavityOutputs.primary.mesh.volume_ml[expected],
      );
      assert.equal(
        selection.reveal,
        false,
        'Clinical reference must not masquerade as a counterfactual control',
      );
      visited.add(selection.frame);
    }
    assert.equal(visited.size, 18);
  }
  const revealBeat = cavityPlan.beats.find((b) => b.id === 'reveal');
  assert.equal(cavitySelection(sampleStory(cavityPlan, revealBeat.startFrame)).reveal, false);
  assert.equal(cavitySelection(sampleStory(cavityPlan, revealBeat.endFrame - 1)).reveal, true);
  const cavityParent = new Group(),
    cavityContent = nativeFactory(cavityPlan)(cavityParent);
  cavityContent.update(sampleStory(cavityPlan, revealBeat.startFrame));
  const beforeRevealScale = cavityParent.children[0].scale.toArray();
  cavityContent.update(sampleStory(cavityPlan, revealBeat.endFrame - 1));
  assert.deepEqual(
    cavityParent.children[0].scale.toArray(),
    beforeRevealScale,
    'Reference reveal must not change the displayed mm scale',
  );
  cavityContent.dispose();
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
  const airwayPlan = plans.find((p) => p.recipe === 'airway-repair-v1');
  const airwayState = (scene, end = false) => {
    const b = airwayPlan.beats.find((b) => b.scene === scene);
    return sampleStory(airwayPlan, end ? b.endFrame - 1 : b.startFrame);
  };
  assert.equal(airwayReveal(airwayState('inputs')), false);
  assert.equal(airwayReturned(airwayState('inputs')), false);
  assert.equal(airwayReturned(airwayState('repair')), false);
  assert.equal(airwayReturned(airwayState('repair', true)), true);
  assert.equal(airwayReveal(airwayState('reference')), false);
  assert.equal(airwayReveal(airwayState('reference', true)), true);
  assert.equal(airwayReveal(airwayState('controls')), false);
  assert.equal(airwayCaseIndex(airwayState('controls')), 1);
  assert.equal(airwayCaseIndex(airwayState('controls', true)), 2);
  assert.equal(airwaySliceIndex(airwayState('inspect')), 0);
  assert.equal(airwaySliceIndex(airwayState('inspect', true)), 8);
  assert.equal(airwayAngleIndex(airwayState('cpr')), 0);
  assert.equal(airwayAngleIndex(airwayState('cpr', true)), 7);
  assert.equal(airwayRouteIndex(airwayState('route', true)), airwayOutput[0].route.length - 1);
  assert.deepEqual(airwayBounds(0), airwayBounds(2));
  for (let i = 0; i < 3; i++) {
    const c = airwayCases[i],
      out = airwayOutput[i];
    const distance = (a, b) => Math.hypot(...a.map((v, k) => v - b[k]));
    assert.ok(
      Math.abs(distance(...c.anchors) - distance(...c.anchors.map((p) => airwayDisplay(p, i)))) <
        1e-10,
      'Display rotation preserves physical distance',
    );
    for (const p of c.sections) {
      const a = Math.hypot(...p.dx_world_mm),
        b = Math.hypot(...p.dy_world_mm);
      assert.ok(a > 0 && b > 0);
      assert.ok(Math.abs(p.dx_world_mm.reduce((v, x, j) => v + x * p.dy_world_mm[j], 0)) < 1e-12);
      assert.equal(atob(p.gray_u8).length, p.width * p.height);
    }
    for (const angle of out.cpr) {
      assert.equal(angle.display_arc_mm.length, 2 * angle.arc_mm.length - 1);
      assert.equal(angle.display_arc_mm[0], angle.arc_mm[0]);
      assert.equal(angle.display_arc_mm.at(-1), angle.arc_mm.at(-1));
      const edges = airwayCPRRowEdges(angle.arc_mm);
      for (let j = 0; j < angle.arc_mm.length; j++) {
        assert.ok(edges[j] < angle.arc_mm[j] && edges[j + 1] > angle.arc_mm[j]);
        if (j) assert.equal(edges[j], (angle.arc_mm[j - 1] + angle.arc_mm[j]) / 2);
      }
      assert.equal(angle.offsets_mm[0], -8);
      assert.equal(angle.offsets_mm.at(-1), 8);
      assert.equal(angle.sampling_edges.length, out.route.length);
      for (let j = 0; j < out.route.length; j++) {
        const [a, b] = angle.sampling_edges[j];
        assert.ok(Math.abs(distance(a, b) - 16) < 1e-9, 'CPR ribbon spans actual physical offsets');
        assert.ok(
          distance(
            a.map((v, k) => (v + b[k]) / 2),
            out.route[j],
          ) < 1e-9,
          'CPR centre matches saved route',
        );
      }
    }
    if (i) {
      assert.equal(airwayReference[i].connectivity.added, 0);
      assert.equal(airwayReference[i].connectivity.after.anchors_connected, true);
      assert.deepEqual(
        Array.from(airwayReference[i].connectivity.after.anchors_in_largest_component),
        [false, false],
      );
    }
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
  const revisedPlan = plans.find((p) => p.recipe === 'longitudinal-ct-revised-v1');
  assert.ok(revisedPlan && isPlanarStory(revisedPlan));
  assert.equal(revisedReference(sampleStory(revisedPlan, 0)), false);
  assert.equal(revisedOutput(sampleStory(revisedPlan, 0)), false);
  assert.deepEqual(
    Array.from(revisedSource.overview, (v) => v.spacing_mm[2]),
    [3, 3, 2, 2.5],
  );
  assert.deepEqual(
    [0, 0.34, 0.67, 1].map((v) => revisedIndex(v)),
    [0, 1, 2, 2],
  );
  assert.deepEqual(
    Array.from(revisedViews[0].partition, (v) => v.k),
    [108, 116, 120],
  );
  assert.deepEqual(
    Array.from(revisedViews[3].new_focus, (v) => v.k),
    [527, 529, 531],
  );
  assert.equal(
    JSON.stringify(recoveredIdentities('case2-image')),
    JSON.stringify(recoveredIdentities('case2-context')),
  );
  assert.deepEqual(Array.from(recoveredIdentities('case2-image')), [
    'baseline:4',
    'followup:13',
    'followup:4',
  ]);
  for (const c of ['case2-image', 'case2-context']) {
    assert.deepEqual(
      Array.from(sizeSummary(c), (r) => [r.total, r.matched]),
      [
        [11, 0],
        [9, 1],
        [2, 2],
      ],
    );
    const m = revisedRef.results[c].metrics;
    assert.equal(m.association.events_conditional_on_detection.eligible_gt_groups, 2);
    assert.equal(m.association.events_conditional_on_detection.total_gt_groups, 15);
  }
  for (const [i, v] of revisedViews.entries()) {
    if (!v.excluded) continue;
    const p = ctNativePoint(v.excluded.reported_point_ijk, v.excluded);
    assert.ok(p.every((x) => x >= 0 && x < 256));
    assert.equal(
      v.excluded.fov_mm,
      v.excluded.width_pixels * revisedSource.overview[i].spacing_mm[0],
    );
    assert.deepEqual(Array.from(ctNativePoint(v.excluded.origin_ij, v.excluded)), [0, 0]);
  }
  for (const point of revisedRef.point_checks) {
    assert.equal(point.reference_id, 2);
    assert.equal(point.context_mask_at_point, 0);
  }
  const satellite = revisedRef.instances.find(
    (v) => v.case === 'case2' && v.visit === 'followup' && v.id === 13,
  );
  assert.deepEqual(
    Array.from(satellite.components_6).sort((a, b) => a - b),
    [1, 1207],
  );
  const decisionBeat = revisedPlan.beats.find((b) => b.scene === 'decisions');
  assert.equal(revisedReference(sampleStory(revisedPlan, decisionBeat.startFrame)), false);
  assert.equal(revisedOutput(sampleStory(revisedPlan, decisionBeat.startFrame)), true);
  assert.equal(revisedReference(sampleStory(revisedPlan, decisionBeat.endFrame - 1)), true);
  const ctPlan = plans.find((p) => p.recipe === 'longitudinal-ct-original-v1');
  assert.ok(ctPlan && isPlanarStory(ctPlan));
  assert.equal(ctShowReference(sampleStory(ctPlan, 0)), false);
  assert.equal(ctShowOutput(sampleStory(ctPlan, 0)), false);
  assert.deepEqual(
    Array.from(ctSource.overview, (v) => v.shape[2]),
    [261, 274],
  );
  assert.deepEqual(
    [0, 0.2, 0.4, 0.6, 0.8, 1].map((v) => ctFrameIndex(v)),
    [0, 1, 2, 3, 4, 5],
  );
  assert.deepEqual(
    Array.from(ctVisits[0].boundary_frames, (v) => v.k),
    [114, 115, 116, 118, 119, 120],
  );
  assert.equal(ctEdges(ctReference.groups).length, 4);
  assert.equal(ctEligibleGroups(ctReference.groups, [4], [4]).length, 0);
  assert.equal(ctEligibleGroups(ctReference.groups, [1, 2, 3, 4], [3, 4]).length, 2);
  assert.equal(ctEdges([{ event: 'unresolved', baseline_ids: [1], followup_ids: [2] }]).length, 0);
  for (const [i, v] of ctVisits.entries()) {
    assert.equal(v.focus.fov_mm, v.focus.width_pixels * ctSource.overview[i].spacing_mm[0]);
    assert.equal(v.focus.k, i === 0 ? 213 : 216);
    assert.equal(
      v.saved_output_view.reference,
      undefined,
      'Output-selected view must not carry a reference overlay',
    );
  }
  for (const row of ctReference.coverage.filter((v) => v.reference_id === 3))
    assert.equal(row.astra_fraction_covered, 0);
  assert.equal(
    ctReference.conditions[0].metrics.association.links_conditional_on_detection.eligible_gt_edges,
    1,
  );
  assert.equal(
    ctReference.conditions[0].metrics.association.events_conditional_on_detection
      .eligible_gt_groups,
    0,
  );
  assert.equal(ctReference.conditions[1].metrics.valid, true);
  assert.equal(ctReference.conditions[1].events.groups.length, 0);
  const mriPlan = plans.find((p) => p.recipe === 'longitudinal-mri-v1');
  assert.ok(mriPlan && isPlanarStory(mriPlan));
  assert.equal(mriShowReference(sampleStory(mriPlan, 0)), false);
  assert.equal(mriShowOutput(sampleStory(mriPlan, 0)), false);
  assert.deepEqual(
    Array.from(mriSource.cases, (c) => c.frames),
    [1288, 2936, 1930],
  );
  assert.deepEqual(Array.from(mriP02.citation.voxel), [386, 155, 84]);
  assert.deepEqual([0, 0.3, 0.6, 1].map(mriPhaseIndex), [0, 1, 2, 3]);
  assert.equal(percentChange(0, 1), null);
  assert.equal(mriRef.clinical_success_rate, null);
  assert.equal(
    mriRef.answers[1].assessment.comparison.size_measurements_mm[1].longest_diameter_mm,
    null,
  );
  for (const method of mriP03.methods) {
    const [first, second] = method.visits;
    assert.ok(
      Math.abs(percentChange(first.diameter_mm, second.diameter_mm) - method.change_percent) <
        1e-10,
    );
    for (const v of method.visits) {
      assert.equal(v.phase, 0, 'Separate P03 acquisition phases are 3D files');
      const box = projectedMethodBox(v),
        edge = v.method.bbox_convention === 'voxel edges' ? 1 : 0;
      assert.ok(box.x >= 0 && box.y >= 0 && box.x + box.width <= 120 && box.y + box.height <= 120);
      assert.equal(box.width, v.bbox_native_max[0] - v.bbox_native_min[0] + edge);
      assert.ok(Math.abs(Math.max(...v.bbox_mm) - v.diameter_mm) < 1e-10);
    }
  }
  for (const scene of ['phases', 'sequences', 'reference', 'forecast']) {
    const b = mriPlan.beats.find((b) => b.scene === scene);
    assert.ok(mriShowReference(sampleStory(mriPlan, b.endFrame - 1)));
  }
  assert.deepEqual(
    Array.from(mriRef.cases, (c) => Math.sign(c.ftv_change_percent)),
    [-1, -1, 1],
  );
  const tigerPlan = plans.find((p) => p.recipe === 'tiger-context-v1');
  assert.ok(isPlanarStory(tigerPlan));
  const tissue = tigerPlan.beats.find((b) => b.scene === 'tissue');
  assert.equal(tigerReveal(sampleStory(tigerPlan, 0)), false);
  assert.equal(tigerReveal(sampleStory(tigerPlan, tissue.startFrame)), false);
  assert.equal(tigerReveal(sampleStory(tigerPlan, tissue.endFrame - 1)), true);
  assert.equal(tigerReveal(sampleStory(tigerPlan, 0)), false);
  assert.equal(tigerSource.mpp, 20000 / 43793);
  assert.deepEqual(
    Array.from(tigerViews, (v) => v.coco_id),
    [942, 940, 941],
  );
  assert.deepEqual(
    Array.from(tigerRef.rois, (r) => r.cells.length),
    [20, 175, 323],
  );
  const stroma = tigerRef.rois[1].rows.filter((r) => [2, 6].includes(r.code));
  assert.ok(Math.abs(tissueArea(324146) - 0.06760693754371358) < 1e-15);
  assert.ok(Math.abs(pooledDensity(stroma) - 2049.191821737891) < 1e-9);
  assert.notEqual(pooledDensity(stroma), stroma.reduce((a, r) => a + r.density_per_mm2, 0) / 2);
  assert.equal(pooledDensity([{ cells: 0, area_mm2: 0 }]), null);
  assert.equal(tigerRef.rois[1].rows[0].density_per_mm2, null);
  assert.equal(tigerRef.rois[1].rows[3].density_per_mm2, null);
  assert.equal(tigerRef.rois[1].rows[1].density_per_mm2, 0);
  assert.deepEqual(Array.from(slidePoint([10, 20], tigerViews[1].bounds_level0)), [33198, 13964]);
  for (const r of tigerRef.rois) {
    assert.equal(
      r.rows.reduce((a, row) => a + row.pixels, 0),
      r.bounds_level0[2] * r.bounds_level0[3],
    );
    assert.equal(
      r.rows.reduce((a, row) => a + row.cells, 0),
      r.cells.length,
    );
    assert.ok(
      r.cells.every(
        (c) =>
          c.center[0] === c.bbox[0] + c.bbox[2] / 2 && c.center[1] === c.bbox[1] + c.bbox[3] / 2,
      ),
    );
  }
  assert.equal(tigerRef.boundary.distance_px, Math.sqrt(13));
  assert.notEqual(tigerRef.boundary.source_code, tigerRef.boundary.shifted_code);
  const hubmapPlan = plans.find((p) => p.recipe === 'hubmap-inventory-v1');
  assert.ok(isPlanarStory(hubmapPlan));
  const outline = hubmapPlan.beats.find((b) => b.scene === 'outline');
  assert.equal(hubmapReveal(sampleStory(hubmapPlan, 0)), false);
  assert.equal(hubmapReveal(sampleStory(hubmapPlan, outline.startFrame)), false);
  assert.equal(hubmapReveal(sampleStory(hubmapPlan, outline.endFrame - 1)), true);
  // Reset is an absolute seek, including all reference-derived output.
  assert.equal(hubmapReveal(sampleStory(hubmapPlan, 0)), false);
  const obj = hubmapRef.objects[0];
  assert.equal(hubmapRef.objects.length, 99);
  assert.ok(Math.abs(profileArea(obj.area_px2) - 15458.43) < 1e-8);
  assert.notEqual(profileArea(obj.area_px2), obj.area_px2 * hubmapSource.mpp);
  const fit = slideFit(hubmapSource.overview, 280, 309);
  assert.ok(Math.abs(fit.width / fit.height - 13013 / 18484) < 1e-12);
  assert.notEqual(
    fit.width / fit.height,
    563 / 800,
    'rounded thumbnail dimensions must not set native geometry',
  );
  assert.equal(slideFit(hubmapDetail, 280, 309).width, 280);
  for (const [i, tile] of hubmapTiles.entries()) {
    const global = toLevel0(hubmapRef.duplicate.local_centers[i], tile.bounds_level0);
    assert.deepEqual(Array.from(global), Array.from(obj.center_level0));
    for (const point of obj.ring) {
      const local = toLocal(point, tile.bounds_level0);
      assert.ok(local.every((v, axis) => v >= 0 && v < tile.bounds_level0[axis + 2]));
      assert.deepEqual(Array.from(toLevel0(local, tile.bounds_level0)), Array.from(point));
    }
  }
  assert.equal(new Set(hubmapRef.objects.map((o) => o.id)).size, 99);
  assert.equal(new Set(hubmapRef.objects.map((o) => o.source_id)).size, 1);
  assert.equal(hubmapRows(0), 1);
  assert.equal(hubmapRows(1), 5);
  assert.equal(hubmapRows(0.8), 5, 'completed table needs reading time before the next chapter');
  const brainPlan = plans.find((p) => p.recipe === 'topbrain-screen-v1');
  assert.ok(isPlanarStory(brainPlan));
  assert.equal(brainReveal(sampleStory(brainPlan, 0)), false);
  assert.equal(brainOutput(sampleStory(brainPlan, 0)), false);
  const bridge = brainPlan.beats.find((b) => b.id === 'calibration');
  assert.equal(brainOutput(sampleStory(brainPlan, bridge.startFrame)), false);
  assert.equal(brainOutput(sampleStory(brainPlan, bridge.endFrame - 1)), true);
  const referenceCheck = brainPlan.beats.find((b) => b.id === 'reference');
  assert.equal(brainReveal(sampleStory(brainPlan, referenceCheck.startFrame)), false);
  assert.equal(brainReveal(sampleStory(brainPlan, referenceCheck.endFrame - 1)), true);
  const contactBeat = brainPlan.beats.find((b) => b.scene === 'contacts');
  const inspected = new Set();
  for (let f = contactBeat.startFrame; f < contactBeat.endFrame; f++) {
    const s = brainSelection(sampleStory(brainPlan, f));
    inspected.add(`${s.case.id}:${s.plane}`);
  }
  assert.deepEqual(
    [...inspected],
    ['004:0', '004:1', '004:2', '007:0', '007:1', '007:2', '011:0', '011:1', '011:2'],
  );
  assert.equal(brainResult.coding_agent_trials, 0);
  assert.equal(brainResult.hard_cases_admitted, 0);
  // A square in physical space must stay square despite a 2:1 voxel-count ratio.
  const physicalSquare = brainPlaneFit(
    { width: 60, height: 30, pixel_spacing_mm: [0.3, 0.6] },
    200,
    300,
  );
  assert.equal(physicalSquare.width, 200);
  assert.equal(physicalSquare.height, 200);
  for (const c of brainCases) {
    const planes = [
      c.overview,
      c.variant,
      c.parent,
      ...(c.contacts || []),
      ...(c.calibration?.gap_sections || []),
      c.calibration?.overview,
    ].filter(Boolean);
    for (const p of planes) {
      for (const source of [p.image, p.prediction]) {
        const bytes = Buffer.from(source.split(',')[1], 'base64');
        assert.equal(bytes.readUInt32BE(16), p.width);
        assert.equal(bytes.readUInt32BE(20), p.height);
      }
      const dims = [0, 1, 2].filter((a) => a !== p.axis);
      const point = [...p.origin_ijk];
      point[dims[1]] = p.end_ijk_exclusive[dims[1]] - 1;
      if (p.index !== null) point[p.axis] = p.index;
      assert.deepEqual(Array.from(brainPixel(p, point)), [0, 0]);
      point[dims[0]] += 3;
      point[dims[1]] -= 4;
      assert.deepEqual(Array.from(brainPixel(p, point)), [3, 4]);
      c.affine_ras_mm.slice(0, 3).forEach((row, axis) => {
        const native = row[3] + point.reduce((sum, v, j) => sum + v * row[j], 0);
        const displayed = p.origin_ras_mm[axis] + 3 * p.dx_ras_mm[axis] + 4 * p.dy_ras_mm[axis];
        assert.ok(Math.abs(native - displayed) < 1e-10);
      });
      const fit = brainPlaneFit(p, 254, 240);
      assert.ok(
        Math.abs(
          fit.width / fit.height -
            (p.width * p.pixel_spacing_mm[0]) / (p.height * p.pixel_spacing_mm[1]),
        ) < 1e-10,
      );
    }
  }
  const cal = brainCases[0].calibration;
  assert.equal(cal.cpr.length, 8);
  assert.equal(cal.cpr[7].angle, 315);
  assert.equal(
    brainRefs['004'].calibration.checks.cpr_samples,
    8 * cal.arc_mm.length * cal.offsets_mm.length,
  );
  assert.ok(
    Math.abs(cal.cpr_display_extent_mm[1] - (cal.offsets_mm.at(-1) - cal.offsets_mm[0] + 0.2)) <
      1e-10,
  );
  assert.equal(brainReveal(sampleStory(brainPlan, 0)), false, 'Reverse seek removes reference');
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
  const dti = plans.find((p) => p.recipe === 'imaging101-dti-v1');
  assert(dti);
  const dtiRef = dti.beats.find((b) => b.scene === 'reference');
  const dtiMid = Math.floor((dtiRef.startFrame + dtiRef.endFrame) / 2);
  assert.equal(dtiReveal(sampleStory(dti, dtiMid - 1)), false);
  assert.equal(dtiReveal(sampleStory(dti, dtiMid)), true);
  assert.equal(dtiScalar(sampleStory(dti, dtiMid)), 'fa');
  assert.equal(dtiScalar(sampleStory(dti, dtiRef.endFrame - 1)), 'md');
  assert.equal(dtiReveal(sampleStory(dti, 0)), false);
  dtiInput.gradients.design_matrix.forEach((row, i) => {
    const [x, y, z] = dtiInput.gradients.bvecs[i],
      b = dtiInput.gradients.bvals[i];
    const expected = [
      1,
      -b * x * x,
      -2 * b * x * y,
      -2 * b * x * z,
      -b * y * y,
      -2 * b * y * z,
      -b * z * z,
    ];
    row.forEach((v, j) => assert.ok(Math.abs(v - expected[j]) < 1e-10));
  });
  for (const method of ['ols', 'wls']) {
    const fit = dtiData.fixed_pixel_fits[method];
    fit.tensor_elements.forEach((e, i) => {
      const params = [Math.log(fit.fitted_s0[i]), ...e];
      dtiInput.gradients.design_matrix.forEach((row, j) => {
        const predicted = Math.exp(row.reduce((total, v, k) => total + v * params[k], 0));
        assert.ok(Math.abs(predicted - fit.predicted_signal[i][j]) < 1e-12);
        if (method === 'ols')
          assert.ok(Math.abs(predicted ** 2 - dtiData.wls_weights[i][j]) < 1e-12);
      });
    });
  }
  for (const t of [
    ...dtiData.tensor_probes.ols,
    ...dtiData.tensor_probes.wls,
    ...dtiReference.tensor_probes,
  ]) {
    assert.ok(Math.abs(dtiFa(t.eigenvalues) - t.fa) < 2e-7);
    assert.ok(Math.abs(t.eigenvalues.reduce((a, b) => a + b, 0) / 3 - t.md) < 1e-9);
    for (const projection of t.projections) {
      const [a, b] = projection.axes;
      const product = (i, j) =>
        t.matrix[i].reduce((sum, v, k) => sum + v * t.matrix[k][j], 0) * 1e6;
      const aa = product(a, a),
        ab = product(a, b),
        bb = product(b, b),
        determinant = aa * bb - ab * ab;
      for (const [x, y] of projection.points) {
        const ellipse = (bb * x * x - 2 * ab * x * y + aa * y * y) / determinant;
        assert.ok(
          Math.abs(ellipse - 1) < 1e-10,
          'Tensor projection must be the silhouette of its own eigenvalue-scaled glyph',
        );
      }
    }
  }
  assert.equal(dtiReference.solver_visible_all_levels, true);
  assert.equal(dtiData.thresholds_available, false);
  assert.equal(dtiData.custom_scoring.oracle_fa_with_zero_md_and_tensor.nrmse, 0);
  assert.deepEqual(Array.from(dtiData.generic_scoring.oracle_md.selected_reference_keys), [
    'fa_map',
  ]);
  assert.deepEqual(Array.from(dtiData.generic_scoring.oracle_tensor.selected_reference_keys), [
    'tensor_elements',
  ]);
  assert.equal(dtiData.fallback.runner_commands_executed, 0);
  const deflectometry = plans.find((p) => p.recipe === 'imaging101-deflectometry-v1');
  assert(deflectometry);
  const deflectometryRef = deflectometry.beats.find((b) => b.scene === 'reference');
  assert.equal(deflectometryReveal(sampleStory(deflectometry, deflectometryRef.startFrame)), false);
  assert.equal(
    deflectometryReveal(sampleStory(deflectometry, deflectometryRef.endFrame - 1)),
    true,
  );
  assert.equal(deflectometryReveal(sampleStory(deflectometry, 0)), false);
  for (const probe of deflectometryInput.fixture_probes) {
    assert.ok(Math.abs(deflectometryPhase(probe.values) - probe.phase) < 1e-12);
    assert.equal(probe.values.reduce((a, b) => a + b, 0) / 4, probe.mean);
    assert.ok(
      Math.abs((probe.delta[0] ** 2 + probe.delta[1] ** 2) / 4 - probe.squared_modulation) < 1e-9,
    );
  }
  for (const profile of [
    deflectometryData.initial_profile,
    deflectometryData.saved_profile,
    deflectometryReference.profile,
  ]) {
    profile.r.forEach((r, i) => {
      assert.ok(Math.abs(deflectometrySag(profile.curvatures[0], r) - profile.front[i]) < 1e-12);
      assert.ok(
        Math.abs(profile.thickness + deflectometrySag(profile.curvatures[1], r) - profile.back[i]) <
          1e-12,
      );
    });
  }
  assert.equal(deflectometryInput.raw_available, false);
  assert.equal(deflectometryReference.solver_visible_all_levels, true);
  assert.equal(deflectometryReference.pose_truth_available, false);
  assert.deepEqual(deflectometryData.pose_control.score, deflectometryData.custom_score);
  assert.ok(Object.values(deflectometryData.generic_scoring).some((r) => r.error));
  assert.ok(Object.values(deflectometryData.generic_scoring).some((r) => r.nrmse === 'inf'));
  const fan = plans.find((p) => p.recipe === 'imaging101-fan-beam-v1');
  assert(fan);
  const fanRef = fan.beats.find((b) => b.scene === 'reference');
  assert.equal(fanBeamReveal(sampleStory(fan, fanRef.startFrame)), false);
  assert.equal(fanBeamReveal(sampleStory(fan, fanRef.endFrame - 1)), true);
  assert.equal(fanBeamReveal(sampleStory(fan, 0)), false);
  for (const c of fanBeamData.pixel_controls) {
    const projected = fanBeamProject(c.row, c.column, c.angle_degrees);
    assert.deepEqual(projected.bins, c.bins);
    assert.ok(Math.abs(projected.detector - c.detector_coordinate) < 1e-10);
    projected.weights.forEach((v, i) => assert.ok(Math.abs(v - c.weights[i]) < 1e-10));
  }
  for (const map of fanBeamData.maps) {
    assert.deepEqual(map.shape, fanBeamReference.map.shape);
    assert.deepEqual(map.range, fanBeamReference.map.range);
  }
  assert.deepEqual(fanBeamInput.sinograms[0].range, fanBeamInput.sinograms[1].range);
  assert.ok(fanBeamInput.sinograms[0].range[0] < 0);
  assert.deepEqual(Array.from(fanBeamData.normalized_maps[2].shape), [104, 104]);
  assert.deepEqual(fanBeamData.normalized_maps[2].range, fanBeamReference.normalized_map.range);
  assert.equal(fanBeamData.loss.values.length, 150);
  assert.equal(
    fanBeamData.loss.values.slice(1).filter((v, i) => v > fanBeamData.loss.values[i]).length,
    66,
  );
  assert.equal(fanBeamData.native['half-truth'].nrmse, 0);
  assert.ok(fanBeamData.generic['half-truth'].nrmse > 0.1);
  assert.equal(fanBeamData.native['outside-crop-plus-ten'].nrmse, 0);
  assert.ok(fanBeamData.generic['outside-crop-plus-ten'].nrmse > 5);
  const dual = plans.find((p) => p.recipe === 'imaging101-dual-energy-v1');
  assert(dual);
  const dualRef = dual.beats.find((b) => b.scene === 'reference');
  assert.equal(dualEnergyReveal(sampleStory(dual, dualRef.startFrame)), false);
  assert.equal(dualEnergyReveal(sampleStory(dual, dualRef.endFrame - 1)), true);
  assert.equal(dualEnergyReveal(sampleStory(dual, 0)), false);
  for (const ray of dualEnergyData.rays) {
    const p = dualEnergyRayPixel(ray.detector_bin, ray.angle_degrees);
    assert.ok(p.x > 48 && p.x < 300 && p.y > 20 && p.y < 200);
    const expected = dualEnergyExpected(ray.saved_material_integrals_g_cm2);
    expected.forEach((v, i) => assert.ok(Math.abs(v - ray.saved_predicted_counts[i]) < 1e-8));
  }
  for (let m = 0; m < 2; m++) {
    assert.deepEqual(dualEnergyData.maps[m].shape, dualEnergyReference.maps[m].shape);
    assert.deepEqual(dualEnergyData.maps[m].range, dualEnergyReference.maps[m].range);
  }
  assert.equal(dualEnergyInput.energies.length, dualEnergyInput.mus[0].length);
  assert.equal(dualEnergyData.native['half-density'].mean_ncc, 1);
  assert.ok(dualEnergyData.native['half-density'].mean_nrmse > 0.3);
  assert.deepEqual(dualEnergyData.native['outside-body-added'], dualEnergyData.native.saved);
  assert.ok(dualEnergyData.generic['two-truth-maps'].error);
  assert.equal(dualEnergyData.generic['truth-bone-sinogram'].ncc, 1);
  assert.equal(dualEnergyData.generic['truth-tissue-only'].ncc, 1);
  const ptychography = plans.find((p) => p.recipe === 'imaging101-ptychography-v1');
  assert(ptychography);
  const ptychographyReferenceBeat = ptychography.beats.find((b) => b.scene === 'reference');
  assert.equal(
    ptychographyReveal(sampleStory(ptychography, ptychographyReferenceBeat.startFrame)),
    false,
  );
  assert.equal(
    ptychographyReveal(sampleStory(ptychography, ptychographyReferenceBeat.endFrame - 1)),
    true,
  );
  assert.equal(ptychographyReveal(sampleStory(ptychography, 0)), false);
  for (let j = 0; j < ptychographyInput.positions.length; j++)
    assert.deepEqual(
      ptychographyCorner(ptychographyInput.encoders[j]),
      ptychographyInput.positions[j],
    );
  for (const sample of ptychographyInput.samples) {
    assert.deepEqual(sample.measured.shape, sample.projected.shape);
    assert.deepEqual(sample.measured.range, sample.projected.range);
    assert.ok(sample.after_relative_l1 < sample.before_relative_l1 / 1000);
  }
  assert.deepEqual(
    ptychographyData.generic['truth-copy'],
    ptychographyData.generic['phase-erased-unit'],
  );
  assert.deepEqual(
    ptychographyData.generic['truth-copy'],
    ptychographyData.generic['conjugated-truth'],
  );
  assert.equal(ptychographyData.native_phase['phase-erased-unit'].ncc, 0);
  assert.ok(ptychographyData.native_phase['conjugated-truth'].ncc < -0.999);
  const nlos = plans.find((p) => p.recipe === 'imaging101-nlos-v1');
  assert(nlos);
  const nb = nlos.beats.find((b) => b.scene === 'reference');
  assert.equal(nlosReveal(sampleStory(nlos, nb.startFrame)), false);
  assert.equal(nlosReveal(sampleStory(nlos, nb.endFrame - 1)), true);
  assert.equal(nlosReveal(sampleStory(nlos, 0)), false);
  for (const h of nlosInputs.histograms) {
    for (let i = 0; i < h.aligned.length; i++)
      assert.equal(h.aligned[i], h.raw[(i - h.shift_bins) % h.raw.length]);
  }
  for (const p of nlosContract.stolt.probes) {
    assert.ok(p.sample_kf > p.kz && p.weight > 0 && p.weight < 1);
    assert.ok(Math.abs(p.sample_kf * p.weight - p.kz) < 1e-12);
  }
  const cars = plans.find((p) => p.recipe === 'imaging101-cars-v1');
  assert(cars);
  const cb = cars.beats.find((b) => b.scene === 'reference');
  assert.equal(carsReveal(sampleStory(cars, cb.startFrame)), false);
  assert.equal(carsReveal(sampleStory(cars, cb.endFrame - 1)), true);
  assert.equal(carsReveal(sampleStory(cars, 0)), false);
  for (const i of [50, 113, 182])
    assert.equal(carsResidual(i), carsContract.fit[i] - carsInput.measured[i]);
  assert.equal(carsInput.nu.length, 200);
  assert.equal(carsInput.nu[0], 2280);
  assert.equal(carsInput.nu[199], 2330);
  const rex = plans.find((p) => p.recipe === 'rex-topcow-v1');
  assert.equal(rex.reference_policy, 'reader-reference-reveal');
  assert.deepEqual(
    Array.from(rexInputs.views, (v) => v.z),
    [108, 118, 128],
  );
  assert.ok(rexInputs.views.every((v) => !('crop_png' in v)));
  assert.equal(rexContract.split.public_label_012, false);
  assert.equal(rexContract.split.private_label_012, true);
  assert.ok(rexContract.split.test_ids.includes('012'));
  assert.deepEqual(
    Array.from(
      rexReference.structures.filter((r) => r.voxels === 0),
      (r) => r.id,
    ),
    [8, 15],
  );
  assert.deepEqual(Array.from(rexNativeIndex(0, 0, 118)), [265, 0, 118]);
  assert.deepEqual(Array.from(rexNativeIndex(0, 0, 118, true)), [187, 113, 118]);
  assert.deepEqual(Array.from(rexNativeIndex(101, 64, 118, true)), [86, 177, 118]);
  assert.equal(rexContract.fixtures[1].anterior_topology, 1);
  assert.equal(rexContract.fixtures[1].b0_error, 0.5);
  assert.equal(rexContract.fixtures[2].dice, 0);
  assert.equal(rexContract.fixtures[2].cldice, 1);
  for (const [scene, count] of [
    ['inputs', 3],
    ['labels', 13],
    ['reference', 3],
    ['metrics', 5],
    ['topology', 2],
    ['geometry', 2],
  ]) {
    const b = rex.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let f = b.startFrame; f < b.endFrame; f++) {
      const state = sampleStory(rex, f);
      seen.add(rexSelection(state));
      assert.equal(rexReveal(state), scene === 'reference' && state.reference > 0.5);
    }
    assert.deepEqual(
      [...seen],
      Array.from({ length: count }, (_, i) => i),
    );
  }
  for (const b of rex.beats) assert.equal(rexReveal(sampleStory(rex, b.startFrame)), false);
  const automed = plans.find((p) => p.recipe === 'automed-multiorgan-v1');
  assert.equal(automed.reference_policy, 'reader-reference-reveal');
  assert.deepEqual(
    Array.from(automedInputs.views, (v) => v.y),
    [144, 164, 184],
  );
  assert.deepEqual(
    Array.from(automedContract.remap, (r) => [r.model_id, r.benchmark_id]),
    [
      [3, 42],
      [2, 43],
      [5, 44],
      [1, 84],
      [52, 3],
    ],
  );
  assert.ok(automedReference.structures.every((r) => r.plane_voxels > 0));
  assert.deepEqual(
    Array.from(automedContract.examples, (e) => [e.format_valid, e.task_score]),
    [
      [true, 1],
      [true, 0.9829],
      [true, 0.9829],
      [false, 0],
      [false, 0],
      [true, 0.5],
      [true, 0],
    ],
  );
  for (const [scene, count] of [
    ['inputs', 3],
    ['workflow', 5],
    ['remap', 5],
    ['geometry', 2],
    ['reference', 5],
    ['scoring', 2],
    ['coverage', 7],
  ]) {
    const b = automed.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let f = b.startFrame; f < b.endFrame; f++)
      seen.add(automedSelection(sampleStory(automed, f)));
    assert.deepEqual(
      [...seen],
      Array.from({ length: count }, (_, i) => i),
    );
  }
  const bcer = plans.find((p) => p.recipe === 'bcer-workflow-v1');
  assert.equal(bcer.reference_policy, 'no-reference-assets');
  assert.deepEqual(Array.from(bcerPixel([0, 0])), [0.5, 0.5]);
  assert.equal(bcerInputs.sequences.length, 3);
  assert.deepEqual(
    Array.from(bcerInputs.sequences, (s) => Array.from(s.size_xyz)),
    [
      [640, 640, 21],
      [120, 128, 21],
      [120, 128, 21],
    ],
  );
  assert.equal(bcerContract.template.nodes.length, 8);
  assert.equal(bcerContract.contract.required_artifacts.length, 4);
  assert.equal(bcerContract.template.nodes[4].required, false);
  assert.ok(bcerContract.contract.required_stage_success.includes('extract_roi_features'));
  assert.deepEqual(
    Array.from(bcerContract.validator_examples, (r) => [
      r.base_success_rule,
      r.tcr.completed,
      r.invariants_passed,
    ]),
    [
      [true, 6, 0],
      [true, 10, 0],
      [true, 10, 5],
      [true, 10, 4],
      [false, 9, 5],
    ],
  );
  for (const [scene, count] of [
    ['geometry', 3],
    ['dependencies', 8],
    ['artifacts', 4],
    ['metrics', 5],
  ]) {
    const beat = bcer.beats.find((b) => b.scene === scene),
      seen = new Set();
    for (let f = beat.startFrame; f < beat.endFrame; f++)
      seen.add(bcerSelection(sampleStory(bcer, f)));
    assert.deepEqual(
      [...seen],
      Array.from({ length: count }, (_, i) => i),
    );
  }
  const abra = plans.find((p) => p.recipe === 'abra-annotation-v1');
  assert.ok(abra);
  assert.deepEqual(Array.from(abraPixel([313, 292], true)), [0.5, 0.5]);
  assert.deepEqual(Array.from(abraPixel([128, 256])), [128.5, 256.5]);
  assert.deepEqual(
    Array.from(abraLps([0, 0], 66)),
    Array.from(abraInputs.full.find((v) => v.k === 66).origin_lps_mm),
  );
  assert.equal(abraReference.frames.length, 8);
  assert.equal(abraReference.frames.find((v) => v.k === 66).pixels, 629);
  assert.equal(abraReference.ordinary.expected_outcome.slice_index, 66);
  assert.equal(abraReference.ordinary.max_turns, 15);
  assert.equal(abraReference.oracle.max_turns, 10);
  const ordinaryStart = abraSelection(sampleStory(abra, 0));
  assert.equal(ordinaryStart.k, 0);
  assert.ok(!ordinaryStart.reference && !ordinaryStart.helper && !ordinaryStart.output);
  const abraReferenceBeat = abra.beats.find((b) => b.scene === 'reference');
  const abraVisibleFrames = new Set();
  for (let f = abraReferenceBeat.startFrame; f < abraReferenceBeat.endFrame; f++) {
    const selection = abraSelection(sampleStory(abra, f));
    if (selection.reference) abraVisibleFrames.add(selection.frame);
  }
  assert.deepEqual([...abraVisibleFrames], [0, 1, 2, 3, 4, 5, 6, 7]);
  const abraOracleBeat = abra.beats.find((b) => b.scene === 'oracle');
  for (let f = abraOracleBeat.startFrame; f < abraOracleBeat.endFrame; f++) {
    const selection = abraSelection(sampleStory(abra, f));
    assert.ok(!selection.output || selection.helper, 'Transfer must follow oracle assistance');
  }
  assert.deepEqual(
    Array.from(abraReference.scorer_arithmetic, (r) =>
      Number(r.reference_copy_polygon_score.toFixed(10)),
    ),
    [1, 0.8, 0.6, 0.4, 0, 1],
  );
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
