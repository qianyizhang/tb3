---
schema: 2
id: resect-point-pilot
title: Correct two MRI-to-ultrasound point correspondences
locale: en
purpose: Explain retained point correction with a solver-visible coordinate cue and exact
  reference boundaries.
scope: One eligible Astra/medium attempt, two selected public training queries. Original world-output
  scores, actual delivered views and later verifier diagnostics. No unaided capability or
  clinical claim.
recipe: resect-pilot-v1
asset_pack: retained-resect-pilot-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/registration/presentation/briefs/tb3-resect-point-pilot.md
- groups/registration/findings/resect-point-audit-context.md
- groups/registration/findings/evidence/resect-point-audit-astra-medium.json
- groups/registration/findings/evidence/resect-point-prompt-cue-audit.json
- groups/registration/reviews/review-5ca5fad5d4504f24.json
- groups/registration/experiments/resect-point-audit-astra-medium/protocol.md
- groups/registration/presentation/sources/resect-sample.json
- presentation/task-explorer/resect-pilot/manifest.json
- scripts/build_resect_pilot_assets.py
- scripts/build_resect_assets.py
- scripts/build_respiratory_assets.py
---

# RESECT pilot with a supplied cue

## inputs

```beat
id: inputs
frames: 240
scene: inputs
caption: One attempt receives two image pairs and two supplied MRI queries.
narration: The executed pilot supplies complete native FLAIR and pre-resection ultrasound
  volumes. Each initial ultrasound candidate copies its MRI world point. These full native
  sections preview both cases. The two public training points were selected before inference
  using tags and mask centroids; selection was not blinded. The prompt also supplies a helpful
  Case B example.
visual: Show both cases and both modalities through their public query; withhold manual targets.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## cue

```beat
id: cue
frames: 288
scene: cue
caption: 'The frozen prompt gives Case B a specific candidate: [-30, 15, 15].'
narration: The viewer example includes this ultrasound coordinate. Trace step five delivers
  the exact instruction, step eighteen renders the candidate, and step nineteen displays these
  panels. MRI and ultrasound are independently centred, so matching screen centres do not
  establish registration. Reference coordinates and physical errors remain hidden.
visual: Show actual delivered axial panels, the prompt command and trace attribution.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## inspect

```beat
id: inspect
frames: 240
scene: inspect
caption: Five actual neighbouring slabs change the view, not the candidate.
narration: These are crops from the final-candidate slabs displayed at step twenty-five. Five
  axial planes span minus two to plus two millimetres from each modality's own centre. MRI
  is centred on the query and ultrasound on the candidate. The gold cross projects the centre
  on each plane; only the middle plane contains it.
visual: Animate five retained source panels in order with offset labels and independent-centre
  disclosure.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## search

```beat
id: search
frames: 288
scene: search
caption: The agent used local correlation, with the prompt cue already present.
narration: Retained step-twenty-one output shows three patch sizes and different Case B peaks.
  The small-patch peak is near the final answer. Case A also has alternative peaks, but the
  agent keeps its supplied point. The search is centred on the original MRI query, not the
  cue; therefore the cue's causal necessity is unresolved. These are correlation scores, not
  confidence or reference agreement.
visual: Show rounded retained peaks and the original-query search centre; run no optimizer.
channels:
  view:
  - 0.5
  - 0.5
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## output

```beat
id: output
frames: 240
scene: output
caption: Return US world millimetres, confidence, evidence and a report.
narration: 'Reveal the actual answer: Case A is retained and Case B is moved. The table shows
  ultrasound world millimetres and subjective confidence, not calibrated probability. Ordered
  result entries, nonempty evidence and a report satisfy the artifact contract. These world
  coordinates belong to the executed pilot, not the separate proposed voxel-output task.'
visual: Reveal the retained two-row answer beside actual final-candidate slabs.
channels:
  view:
  - 0.5
  - 0.5
  output:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## reference

```beat
id: reference
frames: 288
scene: reference
caption: Reveal the manual target and compare initial, supplied and returned points.
narration: Reveal the manual paired target on unchanged ultrasound planes. Compare three-dimensional
  error for the initial, supplied and returned points; two-dimensional projections alone are
  insufficient. Case A remains unchanged and Case B improves relative to its designated initialization.
  The supplied example is closer to the reference than the returned point. Preserve the original
  scores while excluding unaided recovery and superiority to all supplied cues.
visual: Reveal manual crosses on fixed initial-centred source planes, signed plane offsets
  and exact three-dimensional errors.
channels:
  view:
  - 0.5
  - 0.5
  output:
  - 1
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## controls

```beat
id: controls
frames: 240
scene: controls
caption: Artifact reward can pass both unchanged and cue-copy coordinates.
narration: Original oracle reward is one; the original no-op fails because result.json is
  absent. Later synthetic diagnostic artifacts that copy the initialization, or Case A plus
  the Case B cue, both pass. Their errors differ. These are verifier counterexamples, not
  model attempts. The earlier credential failure remains an infrastructure exclusion; saved-output
  replay is not fresh execution.
visual: Compare original controls and clearly labeled post-hoc synthetic copies.
channels:
  view:
  - 0.5
  - 0.5
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## limits

```beat
id: limits
frames: 240
scene: limits
caption: Retain exact observations and narrow the capability claim.
narration: The result remains usable as a description of one cue-present attempt on two selected
  public points. It does not isolate unaided ability, the cue's causal effect, unseen-data
  performance or clinical accuracy. The example coordinate's origin remains unknown. A separately
  authorized prompt-neutral revision and preregistered points would be required to reopen
  unaided capability. No new trial was run.
visual: Show retained evidence, excluded claims, unresolved cue origin and explicit reopening
  conditions.
channels:
  view:
  - 0.5
  - 0.5
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```
