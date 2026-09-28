---
schema: 2
id: imaging101-eht-uq
title: Read uncertainty in a radio-interferometric image
locale: en
purpose: Explain closure measurements, source assumptions, saved sample spread and evaluator limits.
scope: Retained DPI arrays and arithmetic controls. Observation provenance and calibration remain unverified.
recipe: imaging101-eht-uq-v1
asset_pack: retained-imaging101-eht-uq-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-eht-black-hole-uq.md
- presentation/external-tasks/sources/imaging101-eht-uq-audit.json
- scripts/audit_imaging101_eht_uq.py
- scripts/build_imaging101_eht_uq_assets.py
---

# Canonical EHT uncertainty explanation

## A telescope pair measures a spatial frequency

```beat
id: inputs
scene: inputs
frames: 672
caption: A telescope pair measures a spatial frequency
narration: The bundled DPI example contains nine hundred thirty-eight complex visibilities,
  measured at the displayed spatial frequencies. Nine station names and one hundred timestamps
  are retained. The animation highlights stored timestamp groups; it does not simulate telescope
  motion. Orange points are derived conjugates, not additional measurements. The source also
  provides four hundred sixty-five closure phases and four hundred eighty-five log closure
  amplitudes with noise estimates. Sparse Fourier coverage leaves ambiguity in the image.
visual: Display all native u-v points with equal axes and explicit derived-conjugate labels.
  Visit the one hundred source timestamp groups beside the complete phase and log-amplitude arrays.
channels:
  view: [0, 1]
  reference: [0, 0]
```

## Station gains change edges but cancel in closure combinations

```beat
id: closures
scene: closures
frames: 768
caption: Station gains change edges but cancel in closure combinations
narration: Follow the first stored triangle and quadrangle. Their station positions are schematic,
  not geographic. We apply fixed multiplicative station gains to the existing complex visibilities.
  Individual edge phases and amplitudes change, but each station phase cancels around a triangle.
  Gain amplitudes cancel in the quadrangle ratio. The displayed closure values therefore stay
  fixed. The denominator follows the verified source indices, which differ from the README's
  written pairing. This arithmetic identity does not remove thermal noise or make closure rows independent.
visual: Continuously vary the documented station-gain control from zero to full strength.
  Keep edge directions, negative log-amplitude weights, native closure-row values and dynamic
  edge measurements visible together. No learned model or Fourier forward runtime executes.
channels:
  view: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## The image prior supplies assumptions beyond closure data

```beat
id: prior
scene: prior
frames: 672
caption: The image prior supplies assumptions beyond closure data
narration: Closure measurements do not determine absolute flux or image position. The source adds
  flux, centering, smoothness, sparsity and maximum-entropy penalties. Its Gaussian helper has
  fifty microarcseconds full width at half maximum. But two retained versions disagree. The
  saved fixture uses about two point zero four four Janskys from the APEX-ALMA baseline. Current
  preprocessing takes the median over all visibilities, about zero point two seven four Janskys.
  These are different inference conditions, displayed on one brightness scale.
visual: Show the retained Gaussian prior and independently evaluated current-source formula
  on the full 32 by 32 grid. Highlight each condition in turn without morphing one into the other.
channels:
  view: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Read stored samples from an approximate image posterior

```beat
id: samples
scene: samples
frames: 768
caption: Read stored samples from an approximate image posterior
narration: The source procedure maps Gaussian latent vectors through a Real-NVP flow, then applies
  a positive activation and learned intensity scale. Training balances closure agreement and image
  priors against an entropy term that discourages collapse to one image. The diagram explains
  that procedure; it does not replay latent values. Here we inspect the first eight images already
  stored in posterior_samples.npy, in their original order. They are not a time sequence, ranked
  solutions or newly generated images. Diversity alone does not validate posterior probabilities.
visual: Step through saved rows zero to seven at equal intervals. Keep all eight thumbnails,
  selected-row marker, common brightness scale and a schematic source-procedure diagram visible.
channels:
  view: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## The average image and sample spread answer different questions

```beat
id: output
scene: output
frames: 672
caption: The average image and sample spread answer different questions
narration: All one thousand twenty-four stored images produce the saved mean and population
  standard deviation exactly. The mean summarizes average brightness; the standard deviation
  measures variation within this fitted sample set. Both retain the native thirty-two by thirty-two
  grid, with five microarcseconds per pixel. The marked fixed pixel has a trace of all stored
  values, its mean and a one-standard-deviation band. This is not an error map or evidence that
  pixel values follow a Gaussian distribution. The horizontal axis is sample index, not time.
visual: Display mean, standard deviation and the complete fixed-pixel trace. Mark native row
  fifteen, column twenty on both images and sweep a marker across the stored sample indices.
channels:
  view: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Reveal the supplied reference and compare error with spread

```beat
id: reference
scene: reference
frames: 864
caption: Reveal the supplied reference and compare error with spread
narration: The reference remains hidden until this chapter's midpoint. After the reveal, compare
  the supplied reference with the saved mean and absolute pixel error, then inspect containment
  within mean plus or minus one standard deviation. Exactly one hundred eighty of one thousand
  twenty-four reference pixels satisfy that test. This is a descriptive fraction for one image,
  not repeated-data calibration or a universal Gaussian target. Purple dashed borders identify
  reference-derived views. Actual solver staging exposes both truth files at every assistance
  level, so this reveal changes reading order, not evaluator privacy.
visual: Keep reference image, error, containment and reference-specific values absent before
  the midpoint. Then show common-scale truth and mean with separately scaled full-range error,
  followed by the binary containment map and explicit numerator and denominator.
channels:
  view: [0, 1]
  reference: [0, 1]
cut: intentional-cut
```

## The live image scorer ignores uncertainty

```beat
id: scoring
scene: scoring
frames: 672
caption: The live image scorer ignores uncertainty
narration: The task-native helper peak-normalizes the images and uses centered correlation.
  The local generic scorer uses absolute intensity and cosine similarity, so its numbers differ.
  Both assess an image rather than the uncertainty distribution. Supplying a zero standard-deviation
  map or a one-Jansky-per-pixel map alongside the same mean leaves the generic score unchanged. A stack
  of samples is rejected. Copying the exposed reference gives a perfect image score without
  estimating uncertainty. Current pass thresholds are absent. These are saved-array controls,
  not agent results or a benchmark pass.
visual: Visit native mean, generic mean, zero-std, exaggerated-std and reference-copy controls.
  Keep metric definitions, uncertainty omission and missing current thresholds explicit.
channels:
  view: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Preserve version, access and provenance limits

```beat
id: limits
scene: limits
frames: 672
caption: Preserve version, access and provenance limits
narration: The pinned entry script has a syntax error, and its solver expects an older observation
  object absent from current preprocessing. Saved outputs therefore do not prove this source can
  regenerate them. The file named posterior_samples_1024.npy contains a different sample set and
  must not replace the verified one. Both FITS files match the original DPI example, but their
  headers do not establish the README's real-observation claim. This explanation covers retained
  arrays and bounded arithmetic. No new training, sampling, installation, astrophysical validation
  or agent trial was performed.
visual: Visit staging, source reproducibility, alternate-sample identity and unresolved observation
  provenance records. End with the bounded retained-evidence scope and no new model-execution claim.
channels:
  view: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
