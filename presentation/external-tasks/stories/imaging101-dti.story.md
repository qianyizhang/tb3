---
schema: 2
id: imaging101-dti
title: Fit diffusion tensors from directional MRI signals
locale: en
purpose: Explain signal attenuation, fixed pixel fitting, saved tensor maps and evaluator limits.
scope: One synthetic phantom and saved fits. Fixed pixel controls explain the math; source and
  scoring limits remain explicit.
recipe: imaging101-dti-v1
asset_pack: retained-imaging101-dti-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-diffusion-mri-dti.md
- presentation/external-tasks/sources/imaging101-dti-audit.json
- scripts/audit_imaging101_dti.py
- scripts/build_imaging101_dti_assets.py
---

# Canonical diffusion tensor explanation

## One phantom produces 31 differently weighted signal volumes

```beat
id: inputs
scene: inputs
frames: 576
caption: One phantom produces 31 differently weighted signal volumes
narration: This is a retained synthetic phantom, not a patient scan. Each of its one hundred
  twenty-eight by one hundred twenty-eight pixels has thirty-one measurements. One volume has
  no diffusion weighting; thirty use b equal to one thousand seconds per square millimeter.
  The four displayed volumes share one intensity scale. Changing the gradient changes the signal.
  The tissue mask is supplied truth, available to every assistance level, and the source baseline
  fits only inside it.
visual: Select b0 and the three available gradients nearest the source x, y and z axes. Preserve
  the native image grid, common intensity scale and separately labeled supplied mask.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## Each gradient supplies one row of a seven-parameter system

```beat
id: gradients
scene: gradients
frames: 672
caption: Each gradient supplies one row of a seven-parameter system
narration: 'The source equation predicts signal from baseline intensity and directional diffusion.
  Taking its logarithm gives one linear equation per measurement. The design matrix has thirty-one
  rows and seven columns: baseline log intensity and six independent entries of a symmetric
  tensor. Cross terms contain a factor of two. The retained gradient table gives rank seven.
  The view shows source x, y and z coordinates; these are not anatomical directions. Opposite
  gradient vectors give the same quadratic form.'
visual: Visit all thirty-one source gradient rows. Highlight the selected vector and display
  its exact rounded direction, b-value and seven matrix coefficients alongside the signal equation.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Compare the fixed OLS and WLS fit at one selected pixel

```beat
id: fit
scene: fit
frames: 840
caption: Compare the fixed OLS and WLS fit at one selected pixel
narration: Five fixed pixels were selected after reference inspection to explain different tensor
  types. The dots are their retained measurements. The lines come from the audited ordinary
  and weighted least-squares pixel controls, which closely match saved tensor values. Ordinary
  least squares fits log signals. Weighted least squares re-solves using squared signals predicted
  by the ordinary fit, so observations have different influence. These are fixed controls, not
  a new full-image reconstruction or an optimization trajectory.
visual: Select each of five native pixels, keeping its image marker, thirty-one observations,
  OLS/WLS predicted signals and actual WLS weights synchronized. Label the post-hoc selection
  and fixed-control origin.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Six saved values define a symmetric three-dimensional tensor

```beat
id: tensor
scene: tensor
frames: 840
caption: Six saved values define a symmetric three-dimensional tensor
narration: The saved weighted fit contains six independent tensor components in square millimeters
  per second. Eigendecomposition gives three diffusion magnitudes and corresponding axes. Fractional
  anisotropy describes differences between those magnitudes; mean diffusivity is their average.
  The three glyph views are orthographic projections with equal scales and axis lengths proportional
  to eigenvalues. They are not tissue surfaces or fiber tracks. Switching pixels inspects existing
  tensors. Their source coordinates do not establish a patient orientation.
visual: Visit the five saved WLS tensors. Show the symmetric matrix, descending eigenvalues,
  FA/MD and three coordinate projections of the same eigenvalue-scaled glyph, with equal axes
  and explicit units.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect retained scalar maps on common scales

```beat
id: output
scene: output
frames: 672
caption: Inspect retained scalar maps on common scales
narration: 'The source retains ordinary and weighted least-squares maps. First compare their
  fractional anisotropy, then their mean diffusivity. The two methods use identical display
  ranges. Excluded pixels are the supplied truth-mask background, not missing data. These are
  saved outputs, and switching views does not execute either solver. Scalar maps summarize the
  tensor: a similar FA map alone does not guarantee correct diffusion magnitude or direction.'
visual: Show OLS and WLS side by side, switching from FA to MD with a shared scale for each
  quantity and unchanged native coordinates.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal truth and the complete range of saved-map error

```beat
id: reference
scene: reference
frames: 768
caption: Reveal truth and the complete range of saved-map error
narration: The reader reference opens halfway through this chapter. The source truth and weighted-fit
  map use the same scale; the adjacent absolute error map uses its full retained range. The
  comparison includes seven thousand one hundred eighty-six supplied tissue pixels. First inspect
  fractional anisotropy, then mean diffusivity. These arrays are simulated reference values,
  already visible to the solver at all assistance levels. This reveal separates reading stages
  and does not establish a private evaluation condition.
visual: Keep reference maps and values absent before the midpoint. Then mount truth, saved WLS
  and full-range absolute error for FA and MD, with purple reference borders, matched image
  scales and an explicit solver-visible label.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Check what each score actually compares

```beat
id: scoring
scene: scoring
frames: 720
caption: Check what each score actually compares
narration: The task-specific helper checks only masked fractional anisotropy. Correct FA with
  zero mean diffusivity and tensor fields still scores perfectly. If both native files are present,
  this helper selects the ordinary fit first. The local generic scorer includes background and
  chooses a reference by output shape and key order. A mean-diffusivity oracle therefore gets
  compared with FA, while a six-component output selects tensor truth. The published thresholds
  file is absent. These controls diagnose scoring scope, not model capability.
visual: 'Highlight six retained score controls in turn: masked OLS, masked WLS, generic WLS
  FA, FA with zero MD/tensor, MD oracle against the wrong reference, and the tensor oracle.
  Keep denominators and missing thresholds beside the values.'
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Preserve source coordinates, access boundaries and missing contracts

```beat
id: limits
scene: limits
frames: 672
caption: Preserve source coordinates, access boundaries and missing contracts
narration: Every assistance level seeds the entire data directory, including truth and the mask.
  The source rotation attaches the largest eigenvalue to a different axis from its declared
  direction, and two notebook probe labels disagree with the stored arrays. This explanation
  follows the actual tensor values. The fallback scorer without a local workspace requires a
  missing NPY truth file. No container was launched to test that branch. One synthetic phantom
  and fixed numerical controls do not establish clinical accuracy, blind task difficulty or
  an agent result.
visual: 'Visit four source records: actual L1-L3 staging, declared versus stored tensor axis,
  notebook probe-label controls, and the no-workspace scorer error. Preserve the original evidence
  and explicit study limits.'
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```
