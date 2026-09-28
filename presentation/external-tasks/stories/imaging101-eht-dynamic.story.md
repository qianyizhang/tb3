---
schema: 2
id: imaging101-eht-dynamic
title: Recover a changing source from sparse snapshots
locale: en
purpose: Explain temporal coupling, retained video quality and motion-sensitive scoring
  limits.
scope: One synthetic EHT sequence; retained outputs and oracle controls. No fresh reconstruction
  or sky-motion claim.
recipe: imaging101-eht-dynamic-v1
asset_pack: retained-imaging101-eht-dynamic-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-eht-black-hole-dynamic.md
- presentation/external-tasks/sources/imaging101-eht-dynamic-audit.json
- scripts/audit_imaging101_eht_dynamic.py
- scripts/build_imaging101_eht_dynamic_assets.py
---

# Canonical dynamic EHT explanation

## Coverage and source brightness both change

```beat
id: inputs
scene: inputs
frames: 576
caption: Coverage and source brightness both change
narration: The released example contains twelve epochs over six hours. Eight EHT-inspired stations
  provide twenty-eight complex visibility measurements at each epoch. The left panel shows the
  native spatial frequencies; the right shows real and imaginary components of the same measurements.
  Noise bars follow the generator’s complex-root-mean-square convention. Some station pairs overlap
  in this view, but they remain separate stored rows. This is a synthetic rotating crescent, not
  an observed black-hole movie. The animation steps through native epochs without generating new
  observations.
visual: Visit all twelve epochs in original order. Preserve common u-v and visibility axes, native
  measurement count, component legends and epoch labels.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## A Fourier sample combines the entire image

```beat
id: operator
scene: operator
frames: 576
caption: A Fourier sample combines the entire image
narration: Each complex visibility is a weighted sum of all nine hundred image values. The two
  panels show real and imaginary Fourier weights for four fixed baseline rows at the first epoch.
  Their signed colors represent measurement weights, not image brightness. Longer baselines produce
  more rapidly changing weights. Twenty-eight complex samples give only fifty-six real constraints
  for a thirty-by-thirty image. Even a perfectly implemented forward model therefore leaves ambiguity;
  the reconstruction needs assumptions beyond one snapshot.
visual: Step through fixed baseline rows zero, eight, sixteen and twenty-seven at epoch zero.
  Display real and imaginary DFT kernels on a shared minus-one to plus-one scale, exact station
  pairs and baseline coordinates.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Temporal assumptions share information across snapshots

```beat
id: temporal
scene: temporal
frames: 672
caption: Temporal assumptions share information across snapshots
narration: StarWarps models neighboring images as a Gaussian Markov process. A parameterized warp
  predicts the next image, while process noise permits departures from that prediction. Forward
  and backward messages share information across time. Expectation-maximization alternates image
  statistics and warp updates. The source defaults to four affine parameters without translation
  and a fixed process covariance. Its image prior is the displayed super-Gaussian formula. Moving
  highlights illustrate message direction only; they are not saved optimizer states or a fresh
  reconstruction.
visual: Show the source-formula prior beside five schematic nodes representing twelve epochs.
  Highlight forward then backward edges without moving source pixels or pretending to replay EM
  iterations.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect every frame of both saved reconstructions

```beat
id: output
scene: output
frames: 864
caption: Inspect every frame of both saved reconstructions
narration: These are the released static-per-frame and StarWarps reconstructions, displayed in
  original order on one brightness scale. The static method treats each epoch independently; StarWarps
  couples them through the temporal model. Its saved frames vary more smoothly, and the original
  image metrics are better on this sequence. The sidebar reports the twelve-frame averages, while
  the table follows each frame. These numbers reproduce the retained report. They are not new
  inference results, and image similarity alone does not establish correct dynamics.
visual: Visit all twelve pairs of native thirty-by-thirty saved frames. Show common intensity
  range, original epoch and per-frame flux, centered NCC and range-normalized error.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal reference brightness and reconstruction error

```beat
id: reference
scene: reference
frames: 864
caption: Reveal reference brightness and reconstruction error
narration: The supplied reference stays hidden until this chapter’s midpoint. Then compare the
  synthetic truth, the saved StarWarps frame and absolute pixel error at every epoch. The reference
  sums to two Janskys per frame. Truth and reconstruction share one brightness scale; error has
  its own labeled range. Purple dashed borders identify reference-derived views. Actual end-to-end
  staging copies ground_truth.npz at all three assistance levels, so this reveal changes reading
  order, not evaluator privacy. No reference image is substituted for a solver output.
visual: Keep all reference images and errors absent during the first half. After the explicit
  reveal, traverse all twelve epochs on the native grid with matched time and a separately labeled
  full error range.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Smooth images need not recover the full change

```beat
id: diagnostics
scene: diagnostics
frames: 768
caption: Smooth images need not recover the full change
narration: The left plot follows a descriptive brightness direction in array coordinates; the
  right follows total flux. The reference direction advances ninety degrees. Saved StarWarps advances
  about fifty-eight degrees, while the independent static frames advance about eighty-nine. StarWarps
  nevertheless has lower error in adjacent frame differences because the static sequence also
  contains larger fluctuations. These are different properties. Brightness direction is not a
  fitted warp parameter or an astrophysical position angle. Neither method preserves the reference’s
  two-Jansky flux exactly.
visual: Show all twelve measured brightness moments and flux values with separate StarWarps, static
  and dashed-reference legends. Sweep a native-epoch cursor. State the supplemental temporal-difference
  denominator and no sky-motion inference.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## An oracle with no motion can score very highly

```beat
id: scoring
scene: scoring
frames: 768
caption: An oracle with no motion can score very highly
narration: Now inspect answer-based controls. Repeating the reference’s time-average image produces
  no motion but scores higher than either saved reconstruction. Reversing the reference video
  also retains high similarity while reversing its temporal progression. These oracle rows use
  the answer and are not legitimate blind reconstruction baselines. The native report averages
  framewise centered correlation and normalized error. A historical recipe flattens the video;
  the live local scorer uses cosine correlation instead. Keep those definitions separate. No current
  pass thresholds are published.
visual: Select saved StarWarps, repeated oracle time mean, reversed truth and repeated first truth
  frame. Show first and last images, all-frame native scores and descriptive direction changes.
  Preserve oracle labels and distinct metric definitions.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Retain the source and evaluation limits

```beat
id: limits
scene: limits
frames: 672
caption: Retain the source and evaluation limits
narration: The pinned main script contains a syntax error, so the saved arrays do not prove fresh
  source reproducibility. The measurement helper also uses twice the generator’s nominal real-component
  noise variance. All assistance levels expose the reference, and an older runner fallback requires
  a two-dimensional output instead of a video. This review verifies source identities, small arithmetic
  fixtures and retained arrays. It does not establish a blind agent pass, general superiority,
  calibrated motion or a real black-hole observation. No simulation or new solver run was performed.
visual: 'Highlight four source-limit cards in turn: reproducibility, reference access, noise and
  warp conventions, and scientific scope. End with the complete bounded conclusion.'
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```
