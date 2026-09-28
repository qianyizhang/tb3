---
schema: 2
id: rex-topcow
title: Learn named vessels from CTA
locale: en
purpose: Train and submit named-vessel masks while preserving the prepared split,
  native geometry and actual score semantics.
scope: One native CTA and held-out source reference; filename-only preparation and
  nonclinical scorer fixtures. No model run.
recipe: rex-topcow-v1
asset_pack: retained-rex-topcow-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle.md
- presentation/external-tasks/sources/rex-topcow-audit.json
- scripts/audit_rex_topcow.py
- scripts/build_rex_topcow_assets.py
---

# Canonical TopCoW CTA task explanation

## Train a model, then label unseen CTA volumes

```beat
id: inputs
scene: inputs
frames: 288
caption: Train a model, then label unseen CTA volumes
narration: The task asks an agent to develop and train a segmentation pipeline, then
  label unseen CT angiography. Case twelve is a native two hundred sixty-six by three
  hundred seventy-one by three hundred eleven volume. These three teaching sections
  were selected post hoc using the source annotations. They are not supplied targets,
  predictions or an agent search trajectory.
visual: Three native axial views, without source masks or ROI crop.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## An upstream training case can become a ReX test case

```beat
id: split
scene: split
frames: 432
caption: An upstream training case can become a ReX test case
narration: The complete release directory contains one hundred twenty-five matched
  CTA pairs. The pinned preparer sorts the names, then uses seed forty-two to split
  one hundred training and twenty-five test cases. Replaying that code on filename-only
  placeholders places case twelve in test. Its CTA is public to the solver; its label
  is private. The preparer copies no ROI or vessel-edge annotations. This resolves
  the earlier unverified split note, under the complete-release assumption.
visual: Concrete 125 to 100/25 partition with separate public and private records.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Each integer names one vessel class

```beat
id: labels
scene: labels
frames: 624
caption: Each integer names one vessel class
narration: The public vocabulary has thirteen foreground IDs and zero for background.
  One is basilar. Two and three name right and left posterior cerebral arteries. Four
  through seven name the internal carotid and middle cerebral arteries. Eight and
  nine are posterior communicating arteries. Ten is the anterior communicating artery.
  Eleven and twelve are the right and left anterior cerebral arteries; fifteen is
  the third A-two segment. Names and integer identities must remain paired.
visual: Thirteen named IDs highlighted in sequence; no patient reference occupancy
  yet.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Submit a CSV and one label volume per test case

```beat
id: submission
scene: submission
frames: 432
caption: Submit a CSV and one label volume per test case
narration: The sample CSV pairs each image ID and CTA modality with a prediction path.
  Return a single integer NIfTI in the input geometry for every test case. The task
  requires model training and inference, and forbids hand-labeling test data. Inspected
  validation checks ID sets and prediction files, but does not enforce the modality
  column or duplicate row count. Follow the declared format regardless. This is an
  example row, not a produced submission.
visual: Source sample CSV and requested versus inspected validation requirements.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the held-out source labels and ROI

```beat
id: reference
scene: reference
frames: 576
caption: Reveal the held-out source labels and ROI
narration: The chapter starts with the CTA alone. Playback explicitly reveals the
  source mask and an annotation-selected crop for the reader. The dashed white box
  marks that crop in the full plane; magnification adds no source resolution. Colors
  match the local key. Eleven classes occupy the full annotation; IDs eight and fifteen
  do not. Annotation absence is not an independent clinical conclusion. Some labels
  extend beyond the crop. These public-release bytes remain held-out reference material
  in the pinned ReX split.
visual: Input-only start; native overlays and ROI appear halfway, then three source
  planes advance.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Overlap, vessel names and continuity can disagree

```beat
id: metrics
scene: metrics
frames: 720
caption: Overlap, vessel names and continuity can disagree
narration: Five nonclinical nine-cubed fixtures isolate scorer behavior. Exact labels
  match two toy vessels. Removing one voxel disconnects a vessel and raises mean Betti-zero
  error, yet the simplified anterior topology test still passes. Swapping vessel names
  makes class Dice zero while binary centerline Dice stays one. Adding an absent class
  leaves reference-present class Dice near one but fails the anterior verdict. All
  background misses both vessels. These are selected-function reproductions, not patient
  masks or model scores.
visual: Five exact synthetic voxel projections, metric rows and synchronized explanations.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## The pinned topology test checks presence and overlap

```beat
id: topology
scene: topology
frames: 480
caption: The pinned topology test checks presence and overlap
narration: For each named class, the simplified source test requires intersection
  over union of at least one quarter when the reference is present. When the reference
  is absent, the prediction must omit that class. Every class check must pass for
  a regional verdict. There is no adjacency-graph test. The two graph accuracy fields
  duplicate the corresponding anterior and posterior match rates. Separately, group-two
  F-one assigns zero to an all-true-negative class, so the exact two-vessel toy receives
  zero there.
visual: Presence/IoU rules, broken-vessel counterexample and duplicated regional verdict
  rates.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## A permissive cast does not establish correct geometry

```beat
id: geometry
scene: geometry
frames: 432
caption: A permissive cast does not establish correct geometry
narration: The declared output keeps the input shape, spacing, origin, direction and
  integer IDs. The inspected grader resamples shape mismatches with nearest neighbors.
  A separate replay of its preprocessing fragment shows a same-shaped toy origin shifted
  by one hundred millimeters being overwritten with reference metadata. Fractional
  values eleven point five and twelve point five become eleven and twelve after unsigned-eight-bit
  casting. This is fragment behavior, not whole-grader acceptance or valid physical
  alignment.
visual: Required native-grid contract versus two isolated preprocessing observations.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## The primary prose and final ranking are different

```beat
id: ranking
scene: ranking
frames: 576
caption: The primary prose and final ranking are different
narration: The description names mean Dice, but the implementation ranks nine measures
  against a supplied leaderboard and averages their positions. Lower mean position
  is better; ties use minimum rank. Reusing an existing row as a constructed tie yields
  nineteen ninths, about two point one one one. Eight selected metrics were replayed
  on synthetic arrays. The ninth, ninety-fifth-percentile Hausdorff distance, was
  inspected only in source. Its path uses prediction-to-reference edges and a ninety-millimeter
  empty-mask fallback. No full grader or new benchmark result was executed.
visual: Metric directions, constructed nine-position rank arithmetic and explicit
  HD95 execution limit.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## One source-backed task explanation, no capability result

```beat
id: limits
scene: limits
frames: 336
caption: One source-backed task explanation, no capability result
narration: The native CTA, mask and ROI match release sizes and CRCs and retain SHA-two-fifty-six
  hashes. The complete filename inventory resolves the pinned split. Selected nonclinical
  functions explain important scoring differences. This review does not include HD95
  execution, full runtime isolation, training, test predictions, clinical judgments
  or the other nineteen ReX challenge tasks.
visual: Four source, boundary, reproduction and limitation cards.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```
