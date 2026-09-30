---
schema: 2
id: imaging101-eht-original
title: Recover structure through gain-canceling closures
locale: en
purpose: Explain static Fourier imaging, station-gain cancellation and retained comparison
  limits.
scope: One pinned synthetic M87-like source, fixed algebra controls and saved outputs.
  No observation generation, optimization or agent trial.
recipe: imaging101-eht-original-v1
asset_pack: retained-imaging101-eht-original-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-eht-black-hole-original.md
- presentation/external-tasks/sources/imaging101-eht-original-audit.json
- scripts/audit_imaging101_eht_original.py
- scripts/build_imaging101_eht_original_assets.py
---

# Canonical static closure-imaging explanation

## Inspect both supplied observation conditions

```beat
id: inputs
scene: inputs
frames: 576
caption: Inspect both supplied observation conditions
narration: Seven stations provide four hundred twenty-one complex visibility samples across twenty-one
  station pairs. The left panel shows measured Fourier coordinates, highlighting each pair in
  turn. The right compares amplitudes from the supplied calibrated and corrupted observations.
  Both arrays are available to the solver. No conjugate measurements are added. This is one static
  synthetic ring inspired by M87, not an observed black-hole image. Sparse coverage leaves much
  of the spatial-frequency plane unmeasured.
visual: Show all421 native samples, selected station pair and both amplitude conditions on complete
  fixed axes. Preserve21 physical pairs; no simulated UV points or invented time sequence.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## Cancel station factors using matched simultaneous baselines

```beat
id: closures
scene: closures
frames: 768
caption: Cancel station factors using matched simultaneous baselines
narration: A station gain changes every visibility involving that station. Around a triangle,
  the phase factors cancel in the product. Across four stations, adding two log amplitudes and
  subtracting two others also cancels the gain amplitudes. These six controls use exact baseline
  rows matched to the supplied per-scan Fourier coordinates. Fixed gains change the individual
  terms, while the combined value remains unchanged. Station positions in this diagram are schematic.
  This is a deterministic algebra check on existing data, with no new noise or observation simulation.
visual: Cycle all six UV-matched phase/log-amplitude controls. Draw directed baseline terms, matching
  plus/minus signs, green solid additions and orange dashed subtractions. Show fixed before/after
  numeric terms and invariant sum; never use the first-occurrence helper.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Distinguish gain cancellation from noise immunity

```beat
id: observables
scene: observables
frames: 576
caption: Distinguish gain cancellation from noise immunity
narration: The task already supplies two hundred sixty-nine closure phases and two hundred thirty-three
  log amplitude ratios. These plots retain every calibrated and corrupted pair, including outliers.
  The dashed diagonal marks equality. The stored arrays differ because their source observation
  calls include noise; they are not a pure gain-only transformation. Exact cancellation of station
  factors does not cancel measurement noise or make reused combinations independent. The solver
  can use the supplied per-scan closure values and uncertainties without reconstructing their
  grouping from scratch.
visual: Show full phase and log-amplitude scatterplots with common axes that contain every source
  value. Highlight each observable in turn. Keep the large negative log-amplitude outlier, and
  label equality as orange dashed.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Constrain an underdetermined image with a prior

```beat
id: imaging
scene: imaging
frames: 672
caption: Constrain an underdetermined image with a prior
narration: Image fitting starts from a positive brightness distribution. The released Fourier
  operator predicts complex visibilities, using its stated sign convention and pixel response.
  Predicted closures are compared with the supplied measurements, and entropy penalties constrain
  the missing information. The image shown here is the retained Gaussian workflow prior. It is
  not an image file seeded into the assistance levels. The highlighted boxes explain the computational
  sequence; they are not optimizer iterations. No image is reconstructed inside this player.
visual: Step through four conceptual fitting stages beside the retained workflow prior. Preserve
  its original0.6 pixel sum and label unit-flux/log display. No fabricated intermediate reconstruction
  or optimization trajectory.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect the retained calibrated and corrupted method pairs

```beat
id: outputs
scene: outputs
frames: 768
caption: Inspect the retained calibrated and corrupted method pairs
narration: 'The release contains three imaging comparisons: visibility fitting, amplitude plus
  closure phase, and closure-only fitting. Each has a saved calibrated and corrupted output. Every
  image is rescaled to unit flux here so its morphology can be inspected, while its original pixel
  sum remains visible. All panels use the same logarithmic color scale and the complete sixty-four
  by sixty-four grid. The corrupted visibility output has displaced arcs; closure-only retains
  a central ring with artifacts. These are retained examples from one synthetic source, not new
  runs or a general method ranking.'
visual: Cycle all three method pairs with both saved conditions always visible. Use full native
  arrays, common log range1e-6..0.34 and original pixel sums. Do not reveal truth or reference-derived
  scores yet.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the supplied truth and its actual access boundary

```beat
id: reference
scene: reference
frames: 864
caption: Reveal the supplied truth and its actual access boundary
narration: 'The reference stays hidden until this chapter’s midpoint. Then compare all three saved
  method pairs against the same synthetic truth. The dashed border identifies that reference.
  Display normalization remains explicit: the reference sums to one, while its physical counterpart
  sums to point six Janskys. The released solver workspace includes the ground-truth archive at
  every assistance level. This reveal changes reading order, not solver access. A convincing comparison
  image therefore does not establish blind inference ability or performance on actual sky observations.'
visual: Keep reference image absent in the first half, then visit all three native reference/calibrated/corrupted
  triplets. Shared image scale and dashed truth border; explicit unit-sum reference, original
  sums, unchanged full-grid orientation.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Keep the scoring conventions separate

```beat
id: scoring
scene: scoring
frames: 864
caption: Keep the scoring conventions separate
narration: Published metrics normalize each estimate’s total flux to the reference before computing
  range-normalized error. The live filesystem scorer uses that range denominator without flux
  normalization. The older fallback uses reference RMS instead, so its numbers are different again.
  The table preserves all six stored conditions and their cosine correlations. A physical truth
  image at point six Janskys has perfect correlation but nonzero live error because the scorer
  expects unit sum. A zero-image control also exposes the limits of error alone. No pass thresholds
  are supplied.
visual: Highlight each method pair, then fixed physical-truth and zero-image controls. Keep published
  flux-matched range error, live unscaled range error and fallback RMS denominator distinct. Oracle
  controls are answer-based diagnostics, not agent results.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Preserve the source limits and original evidence

```beat
id: limits
scene: limits
frames: 672
caption: Preserve the source limits and original evidence
narration: 'All assistance levels provide calibrated observations, precomputed closures and ground
  truth. Some small source helpers and fixtures disagree: a first-match closure helper loses scan
  identity, a Fourier fixture has inconsistent lengths, and two visibility losses differ by a
  factor of two. A fixed derivative check also finds a TV-gradient sign error. The main saved
  comparisons use entropy penalties, so that defect alone does not explain their outcomes. This
  audit preserves those distinctions and original arrays. It establishes fixed arithmetic and
  saved-output behavior, not a fresh agent pass or recovered optimizer.'
visual: Highlight four evidence-limit cards and end on the single64x64 output contract. Keep the
  TV-versus-main-comparison qualification and no-new-optimization scope visible.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```
