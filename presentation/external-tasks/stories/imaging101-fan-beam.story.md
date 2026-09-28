---
schema: 2
id: imaging101-fan-beam
title: Reconstruct a fan-beam CT slice
locale: en
purpose: Explain divergent-ray magnification, saved reconstructions and score scope
  using pinned source arrays.
scope: One synthetic phantom and three saved images; source FBP replay and fixed controls,
  no fresh iterative solver or agent.
recipe: imaging101-fan-beam-v1
asset_pack: retained-imaging101-fan-beam-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-ct-fan-beam.md
- presentation/external-tasks/sources/imaging101-fan-beam-audit.json
- scripts/audit_imaging101_fan_beam.py
- scripts/build_imaging101_fan_beam_assets.py
---

# Canonical fan-beam CT explanation

## Two scans sample the same synthetic phantom

```beat
id: inputs
scene: inputs
frames: 480
caption: Two scans sample the same synthetic phantom
narration: The released full scan has one hundred eighty source angles and one hundred
  ninety-two detector bins. The short scan has one hundred sixteen angles over two
  hundred thirty-two point nine degrees. Both exclude their ending angle. Orange markers
  select nearby angles on different sampling grids. Gaussian noise can make projection
  values negative, so both views retain a common signed scale. This is one synthetic
  phantom, not an acquired patient scan.
visual: Show the two native sinograms with exact row counts and nearby selected source
  angles; retain negative values.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## Magnification moves a pixel between detector bins

```beat
id: geometry
scene: geometry
frames: 624
caption: Magnification moves a pixel between detector bins
narration: The executed geometry places the source below the image at angle zero.
  Row coordinates increase down, matching the native array. For each pixel, rotate
  its coordinates and compute the distance U from the source plane. Divide five hundred
  twelve by U to obtain magnification. The pixel contribution splits between two neighboring
  detector bins. These three fixed unit-pixel controls reproduce the source operation.
  The square is a field diagram, not anatomy, and no millimeter calibration is supplied.
visual: Show the source, flat detector, field and selected unit pixel in exact scaled
  coordinates. Visit three audited controls and their two-bin contributions.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect the released short-scan weights

```beat
id: weights
scene: weights
frames: 624
caption: Inspect the released short-scan weights
narration: 'The released Parker helper smoothly changes projection weights near the
  beginning and end of the short scan. The image and three curves show its actual
  values. There is a geometry discrepancy: metadata and the helper divide detector
  position by two hundred fifty-six, while source-to-detector separation is five hundred
  twelve pixels. Their declared half-fan angle is therefore larger than the geometric
  angle. Keep the released angles and weights unchanged; do not present the declared
  sweep as the minimum for this geometry.'
visual: Pair the native 116-by-192 weight image with all samples of three labeled
  curves; disclose the two fan-angle calculations.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Three saved images, one display scale

```beat
id: output
scene: output
frames: 528
caption: Three saved images, one display scale
narration: These are three released images, shown on one relative-attenuation scale.
  Full and short FBP apply source preweighting, filtering, weighted backprojection
  and nonnegative clipping. Replaying those operations from the saved noisy measurements
  reproduces both images exactly after float32 conversion. The third image is the
  saved result labelled TV by the source. We do not run its iterative solver or fabricate
  intermediate reconstructions. Selecting a saved image is not an optimization trajectory.
visual: Select full FBP, short FBP and TV-labelled saved maps without crossfading;
  retain one raw scale and the replay boundary.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal truth, then inspect the native scoring crop

```beat
id: reference
scene: reference
frames: 624
caption: Reveal truth, then inspect the native scoring crop
narration: 'First inspect the saved image with an orange dashed square marking the
  metric crop. Reveal synthetic truth beside it halfway through the chapter. Purple
  dashed framing identifies truth. Next switch both panels to their actual cropped,
  independently normalized images. Removing twelve pixels from every edge retains
  ten thousand eight hundred sixteen of sixteen thousand three hundred eighty-four
  pixels. This transformation belongs to the native scoring method. The reader reveal
  does not imply private evaluation: every assistance packet already contains the
  phantom.'
visual: Reveal raw truth at midpoint; after eighty percent of the chapter switch both
  panels to the actual 104-by-104 normalized crops.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Normalization changes which errors the score sees

```beat
id: scoring
scene: scoring
frames: 672
caption: Normalization changes which errors the score sees
narration: Native scores evaluate a center crop after independently normalizing each
  image. The active generic scorer evaluates the full image without that normalization.
  Both score tables are exact saved-array replays, and the native values match the
  historical notebook. Half-strength truth, an added constant, and errors outside
  the crop can all score perfectly under the native method while changing generic
  error. Historical pass boundaries appear in notebook text, but no metrics file is
  shipped. The actual generic scorer supplies no pass or fail.
visual: Compare saved native and generic metrics, then visit three fixed controls
  that expose scale, offset and crop limits.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Every assistance packet contains the phantom

```beat
id: staging
scene: staging
frames: 528
caption: Every assistance packet contains the phantom
narration: At all three assistance levels, the local runner copies measurements, metadata
  and the complete ground-truth phantom. Level two adds an approach and level three
  adds a software design. The audit reproduced those file copies while intercepting
  every installation command. Source and evaluation directories are not seeded. The
  active output contract requires one reconstruction.npy image. Copying the supplied
  truth can receive perfect metrics, but that does not demonstrate reconstruction
  capability.
visual: Highlight each actual assistance packet, the copied truth archive and the
  single-image submission contract.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## A saved result does not prove the solver guarantees

```beat
id: limits
scene: limits
frames: 624
caption: A saved result does not prove the solver guarantees
narration: 'The full recorded curve contains one hundred fifty data-fidelity values
  and sixty-six increases between successive steps. It omits the TV penalty and supplies
  no intermediate images. Two fixed controls also qualify the algorithm description:
  the forward and backprojection pair fail a Euclidean adjoint check, and the claimed
  radius projection leaves a large vector unchanged. These observations do not rewrite
  the saved image or its scores. No fresh iterative result, agent capability, hidden-reference
  validity, current benchmark pass or patient accuracy is established.'
visual: Plot every saved loss sample with a moving inspection cursor; retain the fixed
  operator controls, attribution and limits.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```
