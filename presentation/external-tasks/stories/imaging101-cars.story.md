---
schema: 2
id: imaging101-cars
title: Infer temperature from a CARS spectrum
locale: en
purpose: Explain temperature inversion and the actual released staging and scoring
  contracts.
scope: One published synthetic spectrum, saved fit and bounded contract diagnostics;
  no agent or inverse solve.
recipe: imaging101-cars-v1
asset_pack: retained-imaging101-cars-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-cars-spectroscopy.md
- presentation/external-tasks/sources/imaging101-cars-audit.json
- scripts/audit_imaging101_cars.py
- scripts/build_imaging101_cars_assets.py
---

# Canonical CARS task explanation

## Start with 200 spectral measurements

```beat
id: inputs
scene: inputs
frames: 336
caption: Start with 200 spectral measurements
narration: 'One published synthetic nitrogen spectrum contains two hundred paired
  wavenumbers and intensities. The arrays have shape one by two hundred: the first
  dimension is a one-case batch. The axis spans twenty-two eighty to twenty-three
  thirty inverse centimeters. Metadata supplies pressure, pump linewidth, slit width
  and molecular constants. These are synthetic gas data, not an experimental measurement.'
visual: Plot every native measurement with units; separate physical metadata.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## The released staging exposes the reference

```beat
id: staging
scene: staging
frames: 528
caption: The released staging exposes the reference
narration: The scientific reference and the released solver boundary differ. All three
  end-to-end levels copy the complete data directory, including ground truth. We reproduced
  file seeding while intercepting every installation command. Level two adds an approach
  that also states the true temperature; level three adds software design. The player
  can hide a curve for teaching, but that display choice does not make the released
  reference private.
visual: Advance L1, L2 and L3 cards; show exact copied reference path.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Change temperature, then predict a spectrum

```beat
id: forward
scene: forward
frames: 576
caption: Change temperature, then predict a spectrum
narration: Temperature changes molecular populations and the relaxation matrix. The
  implementation combines Q, O and S branch contributions, adds a coherent nonresonant
  background, applies pump and slit operations, then downsamples and normalizes. Two
  fixed proposals, two thousand and twenty-eight hundred kelvin, show the resulting
  shape change. Other parameters stay fixed. These are bounded forward diagnostics,
  not fitting steps or an observed optimizer trajectory.
visual: Compare two source-forward curves with all two hundred measured samples.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect the published fit and its residual

```beat
id: fit
scene: fit
frames: 528
caption: Inspect the published fit and its residual
narration: The source release includes a saved fitted spectrum and a temperature of
  twenty-three ninety-one point five six kelvin. Inspect three exact sample indices.
  The vertical segment and arithmetic show fitted intensity minus measured intensity
  at the same wavenumber. The source optimizer fits four parameters with bounded least
  squares. This tour replays retained output; it does not run a fresh inversion.
visual: Advance exact indices 50, 113 and 182; numeric and plotted residuals agree.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the clean source spectrum

```beat
id: reference
scene: reference
frames: 480
caption: Reveal the clean source spectrum
narration: 'The clean spectrum appears halfway through this chapter, as a dashed purple
  curve. Its true source temperature is twenty-four hundred kelvin. The saved estimate
  differs by eight point four four kelvin. Noise and preprocessing explain why measured
  points differ from the clean curve. This is a reader reference reveal: the released
  task staging already copied the reference file.'
visual: Initially show measured points and saved fit only; explicitly reveal clean
  curve and true parameter.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Two scorer paths ask different questions

```beat
id: scoring
scene: scoring
frames: 672
caption: Two scorer paths ask different questions
narration: The active local generic scorer compares the saved spectral array to the
  clean spectrum. Its normalized error is zero point zero zero two four zero three,
  and it emits no temperature error. The separate CARS adapter compares to noisy measurements
  and also reports Kelvin error. A raw-data no-op is a control, not a fitted result.
  Substituting three hundred kelvin with the same curve leaves correlation unchanged
  but produces twenty-one hundred kelvin error in the native adapter. Missing thresholds
  prevent a pass claim.
visual: Highlight three scored conditions, retain distinct references and expose missing
  pass thresholds.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Preserve the batch axis in the output

```beat
id: shape
scene: shape
frames: 528
caption: Preserve the batch axis in the output
narration: The active local contract asks for output slash reconstruction dot n p
  y. Shape one by two hundred matches the clean spectral array. Flattening to two
  hundred fails the pinned reference lookup. A one-element temperature array selects
  a scalar reference, whose zero dynamic range makes normalized error infinite. This
  is not a Kelvin-error calculation. The separate native adapter uses a different
  archive and two named keys.
visual: Advance three exact tested shapes and show the two distinct output contracts.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## A saved fit is useful; a benchmark pass is unresolved

```beat
id: limits
scene: limits
frames: 576
caption: A saved fit is useful; a benchmark pass is unresolved
narration: 'The inspected source establishes exact samples, a saved fit, reference
  visibility and scorer behavior. It does not establish a fresh agent result, hidden-reference
  validity or general performance. The pinned forward model also normalizes away the
  mole-fraction amplitude: changing it from zero point seven nine to zero point two
  produces the same normalized curve within floating-point precision. Numerical warnings
  were retained and all output samples were finite. Preserve these limits alongside
  the useful worked example.'
visual: Pair established evidence with unresolved claims; show the normalization diagnostic
  and no fresh-run boundary.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```
