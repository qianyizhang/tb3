---
schema: 2
id: imaging101-nlos
title: Reconstruct a hidden scene from timed light
locale: en
purpose: Explain exact confocal time alignment, Stolt mapping and saved-volume evaluation
  boundaries.
scope: One published measurement cube, saved reconstruction and small operator diagnostics;
  no agent or fresh full-size inverse.
recipe: imaging101-nlos-v1
asset_pack: retained-imaging101-nlos-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-confocal-nlos-fk.md
- presentation/external-tasks/sources/imaging101-nlos-audit.json
- scripts/audit_imaging101_nlos.py
- scripts/build_imaging101_nlos_assets.py
---

# Canonical confocal NLOS explanation

## Record when indirect light returns

```beat
id: inputs
scene: inputs
frames: 336
caption: Record when indirect light returns
narration: A pulsed source illuminates a relay wall and the detector records indirect
  light returning to the same scan point. The released cube has one hundred twenty-eight
  by one hundred twenty-eight wall locations and two thousand forty-eight time bins.
  Each bin is thirty-two picoseconds. The map sums photon counts over time; it is
  not a photograph of the hidden object. The source attributes these measurements
  to an outdoor scene with a ten minute exposure.
visual: Inspect the native wall sum and three exact raw photon histograms.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## Align time zero, then crop 512 bins

```beat
id: alignment
scene: alignment
frames: 576
caption: Align time zero, then crop 512 bins
narration: The calibration grid gives a delay for each wall location. Divide by thirty-two
  picoseconds, take the floor, then circularly shift by its negative. Three selected
  points shift by seven hundred forty-eight, eight hundred sixteen and nine hundred
  three bins. Keep the first five hundred twelve bins and move time to the first axis.
  The source display then spans zero to two point four five seven six metres in depth.
  Original raw counts remain unchanged.
visual: Show raw and exactly aligned counts for three native wall coordinates; link
  each shift to its calibration value.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Sample temporal frequencies on the Stolt curve

```beat
id: stolt
scene: stolt
frames: 576
caption: Sample temporal frequencies on the Stolt curve
narration: The source migration scales amplitude, pads each dimension by two, and
  takes a three-dimensional Fourier transform. The Stolt step samples the temporal
  spectrum on a curved coordinate map for each target depth frequency. Inspect three
  exact map evaluations with fixed lateral frequencies. Interpolate real and imaginary
  parts, apply the positive-frequency mask and Jacobian, then invert the transform
  and square its magnitude. These are operator illustrations; only a small published
  fixture was executed, not the full measurement reconstruction.
visual: Advance three frequency samples and exact interpolation coordinates with their
  Jacobian weights.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect the released 3D reconstruction

```beat
id: output
scene: output
frames: 480
caption: Inspect the released 3D reconstruction
narration: The release contains a saved five hundred twelve by one hundred twenty-eight
  by one hundred twenty-eight float32 volume, ordered by depth, y and x. Front, top
  and side panels take maxima over different stated axes. Native image pixels are
  retained; square-root display contrast and eight-bit color make the projections
  readable. The maximum occurs at the final depth plane. The displayed depth axis
  is a source convention, not independent evidence of object depth.
visual: Cycle native front/top/side max projections with physical axes and explicit
  saved-output status.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal a baseline with identical values

```beat
id: reference
scene: reference
frames: 480
caption: Reveal a baseline with identical values
narration: The baseline appears halfway through this chapter inside a dashed purple
  frame. All eight million three hundred eighty-eight thousand six hundred eight values
  equal the saved output. A third reconstruction archive has the same values too.
  This establishes stored-array agreement, not independent scene ground truth or a
  new solver result. The display reveal is for the reader; the released solver packet
  already contains the baseline.
visual: Keep baseline image absent initially, then reveal its separately derived projection
  and exact equality.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 1
cut: intentional-cut
```

## The released input packet includes the baseline

```beat
id: staging
scene: staging
frames: 528
caption: The released input packet includes the baseline
narration: All three assistance levels include the complete data directory. Reproducing
  the selected file-copy functions confirms that each receives baseline reference
  dot n p z. Every installation command was intercepted. Level two adds approach guidance
  and level three adds software design. Source code and evaluation outputs are not
  seeded by this local path. The Docker source mounts the whole task read-only, which
  does not make its references private. No Docker runtime was launched.
visual: Advance three source assistance cards and keep copied baseline visibility
  explicit.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Perfect agreement is a saved-output check

```beat
id: scoring
scene: scoring
frames: 672
caption: Perfect agreement is a saved-output check
narration: The active generic scorer selects the saved reconstruction as its reference.
  Both the saved array and a copy of the visible baseline get correlation one and
  normalized error zero. Halving the amplitude leaves cosine correlation one but gives
  normalized error zero point zero two zero five seven four. The native main function
  normalizes each volume first, so it removes that amplitude difference. A front projection
  fails the required volume shape. Shipped metric records contain no pass boundaries,
  so a benchmark pass is unresolved.
visual: Compare saved output, baseline-copy control and half amplitude; keep shape
  errors and missing thresholds distinct.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Retain the useful operation and its limits

```beat
id: limits
scene: limits
frames: 576
caption: Retain the useful operation and its limits
narration: This review establishes exact source inputs, calibration examples, a bounded
  operator check, a saved volume and scorer behavior. It does not establish a fresh
  agent reconstruction, independent ground truth or hidden-reference evaluation. The
  original MATLAB program permutes lateral axes and removes the last eleven depth
  planes; the Python adaptation retains its final plane. Byte equivalence to original-author
  output is unverified. Source data terms allow academic and other non-commercial
  use, and those terms remain attached to the derived views.
visual: Separate established numerical evidence from source lineage, evaluation and
  acquisition limits.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```
