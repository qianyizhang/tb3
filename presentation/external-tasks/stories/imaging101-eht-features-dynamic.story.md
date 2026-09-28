---
schema: 2
id: imaging101-eht-features-dynamic
title: Follow a changing crescent and its uncertainty
locale: en
purpose: Explain independent geometric inference, retained weighted distributions
  and distinct scoring limits.
scope: One synthetic sequence and retained posteriors; no new training or calibration
  claim.
recipe: imaging101-eht-features-dynamic-v1
asset_pack: retained-imaging101-eht-features-dynamic-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-eht-black-hole-feature-extraction-dynamic.md
- presentation/external-tasks/sources/imaging101-eht-features-dynamic-audit.json
- scripts/audit_imaging101_eht_features_dynamic.py
- scripts/build_imaging101_eht_features_dynamic_assets.py
---

# Canonical dynamic feature-distribution explanation

## Infer geometry from ten sparse snapshots

```beat
id: inputs
scene: inputs
frames: 576
caption: Infer geometry from ten sparse snapshots
narration: The released synthetic example contains ten snapshots, from zero to seven point two
  hours. Eight EHT-inspired stations provide twenty-eight complex visibility measurements at each
  time. The left panel shows their spatial frequencies; the right shows real and imaginary components.
  Earth rotation changes the coverage while the synthetic source also changes. Some station pairs
  overlap in the view, but remain separate stored rows. This is not a real black-hole observation.
  The player visits existing epochs without generating measurements.
visual: Visit all ten native epochs on fixed UV and visibility axes. Retain 28 stored rows, original
  times, units and real/imaginary colors; no added conjugate measurements.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## Combine measurements to cancel station gains

```beat
id: closures
scene: closures
frames: 576
caption: Combine measurements to cancel station gains
narration: A closure phase adds two baseline phases and subtracts the third around a triangle.
  A log closure amplitude adds two log amplitudes and subtracts two others across four stations.
  Station-based gains cancel in these combinations. The table applies fixed gains to the same
  recorded measurements; individual entries change while each closure stays the same. The source
  constructs fifty-six phase combinations and seventy amplitude combinations, but their linear
  ranks are only twenty-one and nineteen. Many combinations reuse the same data.
visual: Cycle through phase and amplitude controls at epochs 0, 4 and 9. Preserve exact station pairs,
  baseline signs, recorded before/after values and wrapped phase units. Station-node positions
  are conceptual, not geographical.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Fit four parameters independently at each time

```beat
id: model
scene: model
frames: 672
caption: Fit four parameters independently at each time
narration: The source constrains each image to an asymmetric Gaussian ring. Its four parameters
  set the ring-center diameter, Gaussian width, brightness asymmetry and angle. The paired images
  are fixed examples showing one parameter change at a time; they are not inferred outputs. A
  normalizing flow represents a distribution over these parameters, and predicted closures are
  compared with measurements. The source starts a separate fit at every snapshot. There is no
  temporal model passing information between neighboring frames.
visual: Show four fixed parameter pairs on a stated 0–0.0045 unit-flux scale. Keep all other parameters
  fixed and distinguish model examples from data. A small flow-to-closure diagram is conceptual,
  not training playback.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Ten thousand samples need not mean much effective support

```beat
id: posterior
scene: posterior
frames: 864
caption: Ten thousand samples need not mean much effective support
narration: These histograms use every released parameter sample with its original normalized importance
  weight. Each row is one independent snapshot. The player changes the parameter being inspected,
  while all ten times remain visible. Every parameter uses sixty fixed bins; each ridge height
  is normalized separately for readability. No density smoothing or new samples are added. Although
  ten thousand samples are stored per frame, effective sample sizes range from about four to one
  hundred eleven. At the last epoch, one sample carries almost forty-six percent of the weight.
visual: Show all four parameter histograms, original weighted mass and matching bin widths. Display
  all ten effective sample sizes beside them; normalized ridge heights do not compare probability
  mass between epochs. Keep supplied truth absent.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the supplied reference without changing its role

```beat
id: reference
scene: reference
frames: 864
caption: Reveal the supplied reference without changing its role
narration: The supplied reference remains hidden until this chapter’s midpoint. Then inspect every
  truth frame beside the saved posterior mean and absolute error. Both brightness stacks share
  one intensity scale, and error has its own labeled scale. Stored images sum to approximately
  one; the observation generator instead used point six Janskys. Array row and column axes are
  explicit. Actual assistance levels expose the truth archive and an additional metadata file
  containing the parameters. This reveal controls reading order, not evaluator privacy.
visual: Keep truth and error absent in the first half. At the midpoint reveal all ten native 64×64
  triplets, matched epoch, common unit-flux image scale, separate full error scale and dashed
  reference borders. No crop or celestial-coordinate assertion.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## A narrow-looking distribution can still be displaced

```beat
id: diagnostics
scene: diagnostics
frames: 768
caption: A narrow-looking distribution can still be displaced
narration: Now compare saved weighted means and standard deviations with the supplied parameters.
  The source holds diameter, width and asymmetry fixed while its angle changes. At frame four,
  the saved angle mean is about twenty-six degrees below truth, but its weighted standard deviation
  is only about seven degrees. The other panels reveal different errors and spreads. Joining lines
  help follow the snapshots; they do not imply temporal coupling. Weighted spread is not a guaranteed
  coverage interval, and one synthetic sequence does not establish uncertainty calibration.
visual: Cycle through all four parameter summaries with ten native observations each. Show green
  means and one-SD bars, dashed purple truth and orange frame 4 emphasis. Keep original units and
  exact frame 4 mean, truth, bias and SD beside each plot.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Keep image accuracy and uncertainty evaluation separate

```beat
id: scoring
scene: scoring
frames: 768
caption: Keep image accuracy and uncertainty evaluation separate
narration: The native parameter recipe reports about six degrees of mean absolute angle error.
  The live generic scorer instead compares the mean-image stack and reports cosine correlation
  near point nine nine six; it rejects the posterior-sample shape. Neither measure directly evaluates
  uncertainty calibration. An oracle placing all probability at the supplied truth has zero error
  and zero spread, illustrating the gap. A separate pair of angles near the wrap boundary also
  exposes linear-summary limits. That boundary is absent from the released samples and does not
  explain their observed bias.
visual: Highlight native point error, generic image score, oracle point distribution and fixed
  wrap counterexample in turn. Keep oracle answer access and absent pass thresholds visible. Do
  not imply either control is a legitimate blind solution.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Preserve the source limits and original outcomes

```beat
id: limits
scene: limits
frames: 672
caption: Preserve the source limits and original outcomes
narration: The pinned source weights likelihood seventy times more during training than during
  importance reweighting, relative to the same log-density term. Checkpoints and latent-density
  records are missing, so corrected outcomes cannot be inferred. All assistance levels expose
  answers. Stored image units and generic output requirements differ from parts of the task description,
  and an older runner fallback cannot find the released reference format. This review establishes
  source identities, fixed arithmetic and saved-array behavior. It does not establish a new agent
  pass, calibrated uncertainty or performance on actual sky observations.
visual: 'Highlight four source-limit cards: answer access, likelihood weighting, output/units
  and evidence scope. End with the bounded result and no new training statement; preserve all
  original arrays and scores.'
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```
