---
schema: 2
id: longitudinal-mri
title: 'Longitudinal MRI: locate, measure and qualify'
locale: en
purpose: Explain native image citations, phase and sequence selection, explicit extent
  definitions, uncertainty and forecasts using the retained BR037 MRI tasks.
scope: Three selected public I-SPY2 cases, two solver-visible visits, three neutral
  attempts and one same-image cue attempt. Source crops and saved-method diagnostics
  are reader aids; mechanical completion is not clinical validation.
recipe: longitudinal-mri-v1
asset_pack: retained-longitudinal-mri-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-mri.md
- groups/longitudinal-reading/presentation/sources/longitudinal-mri-audit.json
- groups/longitudinal-reading/experiments/br037/protocol.md
- groups/longitudinal-reading/findings/longitudinal-reading-current-synthesis.json
- docs/evidence/br037-curation.json
- docs/evidence/br037-freeze.json
- docs/evidence/br037-results.json
- docs/research-rounds/BR-037-results.md
- scripts/build_longitudinal_mri_assets.py
---

# Read the images, define the measurement, retain uncertainty

## Start with full MRI volumes

```beat
id: inputs
scene: inputs
frames: 192
caption: Start with full MRI volumes
narration: Three selected public cases provide two complete available MRI exams each.
  The solver sees reconstructed volumes, sequence metadata, native affines and relative
  timing. Target locations, later exams and clinical outcomes are withheld. These
  middle slices only preview the larger input packet.
visual: Six actual input middle slices with case, visit, relative day and native slice
  labels.
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

## Cite the finding in its native frame

```beat
id: locate
scene: locate
frames: 216
caption: Cite the finding in its native frame
narration: A saved P02 observation names visit one, series twenty, phase one and voxel
  three eighty-six, one fifty-five, eighty-four. The native affine maps that citation
  into RAS millimetres. The point supports an inspectable statement, not a lesion
  boundary. Visits are not registered.
visual: Reveal the amber saved point on the cited native slice and display voxel-to-RAS
  coordinates.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Hold the window fixed; inspect the phases

```beat
id: phases
scene: phases
frames: 264
caption: Hold the window fixed; inspect the phases
narration: Now reveal reader-only crops selected from source measurement regions.
  That removes the localization search. Compare phases zero, one, two and six using
  a fixed window within each visit. The changing appearance makes phase choice consequential,
  but does not validate a clinical diameter.
visual: Advance both visits through four actual dynamic phases with acquisition offsets
  and fixed within-visit windows.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Cross-check another sequence

```beat
id: sequences
scene: sequences
frames: 192
caption: Cross-check another sequence
narration: T2 fat-suppressed crops provide another sequence-specific view. Each crop
  uses its own native affine and source center. This is a reader comparison, not image
  registration. Separate observed signal from the interpretation and the uncertainty
  it leaves.
visual: Actual native T2 crops with series and native-center labels; reader reference
  selection stays visible.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Define the object before measuring it

```beat
id: measure
scene: measure
frames: 240
caption: Define the object before measuring it
narration: The saved P03 neutral method subtracts precontrast from first postcontrast,
  smooths by one voxel, and thresholds at thirty percent. A connected component produces
  a three-dimensional bounding box. Its longest voxel-edge span reproduces twenty-one
  point two five and twenty millimetres, without establishing a clinical boundary.
visual: Actual P03 crops reveal amber projected component boxes, labelled as a reproduced
  method rather than ground truth.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Compare methods without claiming causality

```beat
id: change
scene: change
frames: 240
caption: Compare methods without claiming causality
narration: The neutral method gives a five point nine percent decrease; the cue method
  gives twenty-seven point two percent. They use identical images but different phases,
  thresholds, smoothing and box conventions. Both saved answers reject disappearance.
  One pair cannot isolate a causal cue effect or ordinary run variability.
visual: Compare recomputed millimetres and percentage changes beside all four consequential
  method choices.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Keep source endpoints separate

```beat
id: reference
scene: reference
frames: 240
caption: Keep source endpoints separate
narration: Reveal source longest-diameter and functional-volume changes. Their directions
  can differ, as in P03. Workbook diameter units remain unresolved, so percentage
  change avoids assuming millimetres. Functional volume uses enhancement criteria
  and a source region. Neither measure directly establishes viable tumor or pathological
  complete response.
visual: Reveal three source diameter and FTV percent-change rows, with unresolved
  units and endpoint limits adjacent.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Return a qualified assessment

```beat
id: output
scene: output
frames: 216
caption: Return a qualified assessment
narration: 'Return citations for both visits, measurements with methods, a comparison,
  an impression with alternatives and uncertainty, and a forecast with assumptions.
  Include a report, analysis code and key figures. Null diameter is allowed: a schema-valid
  null does not adjudicate whether residual extent is clinically unmeasurable.'
visual: Show exact output sections and file names, with saved P02 numeric-to-null
  example and the checker boundary.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Compare the forecast with a baseline

```beat
id: forecast
scene: forecast
frames: 216
caption: Compare the forecast with a baseline
narration: Future exams were hidden from the solver. All three neutral answers forecast
  smaller extent, and all three next-visit source diameters decreased. An always-smaller
  baseline also matches three of three. The cue run reuses P03, so it is not a fourth
  patient. Individualized forecasting advantage remains unestablished.
visual: Reveal the future source direction and neutral versus always-smaller baseline
  denominators.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Separate completion from clinical evidence

```beat
id: limits
scene: limits
frames: 216
caption: Separate completion from clinical evidence
narration: All four attempts completed and passed the mechanical contract. Those checks
  validate structure and citation bounds, not clinical correctness. Three stratified
  public cases cannot establish population performance or held-out generalization.
  Measurement references and causal cue attribution remain limited; original scores
  and uncertainty are preserved.
visual: Contrast four mechanical completions with explicitly unassessed clinical success
  and study limits.
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
