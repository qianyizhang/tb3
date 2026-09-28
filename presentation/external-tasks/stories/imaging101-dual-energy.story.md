---
schema: 2
id: imaging101-dual-energy
title: Separate two materials with dual-energy CT
locale: en
purpose: Explain paired spectral measurements, saved material reconstruction and the
  two-material scoring boundary.
scope: One synthetic parallel-beam case, saved result and forward/scoring diagnostics;
  no fresh material optimization or agent.
recipe: imaging101-dual-energy-v1
asset_pack: retained-imaging101-dual-energy-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-ct-dual-energy.md
- presentation/external-tasks/sources/imaging101-dual-energy-audit.json
- scripts/audit_imaging101_dual_energy.py
- scripts/build_imaging101_dual_energy_assets.py
---

# Canonical dual-energy CT explanation

## Two spectra measure the same synthetic phantom

```beat
id: inputs
scene: inputs
frames: 480
caption: Two spectra measure the same synthetic phantom
narration: The source provides paired low and high energy count sinograms for one
  synthetic phantom. Each has one hundred twenty-eight detector bins and one hundred
  eighty projection angles. The same selected ray is marked in both images, on a shared
  count scale. The two observations differ because their incident spectra differ.
  These are simulated photon counts, not patient images or Hounsfield units.
visual: Show both native count sinograms with calibrated detector and angle axes;
  visit three actual rays.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## Keep spectra and material attenuation separate

```beat
id: calibration
scene: calibration
frames: 576
caption: Keep spectra and material attenuation separate
narration: 'The supplied spectra describe incident photons in each one-keV energy
  bin. Separate material curves describe mass attenuation in square centimeters per
  gram. The green and orange legends identify each curve explicitly. Tissue and bone
  affect both spectra, but with different energy dependence. These released attenuation
  tables are approximations: the values at twenty keV differ from the official NIST
  tables. The audit keeps the released calibration unchanged.'
visual: Plot all 131 supplied spectral and attenuation samples; highlight three energy
  bins without changing calibration.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Predict counts from a saved pair of material integrals

```beat
id: forward
scene: forward
frames: 624
caption: Predict counts from a saved pair of material integrals
narration: For each energy, multiply tissue and bone line integrals by their respective
  mass attenuation coefficients. Add the two contributions and exponentiate their
  negative sum to get transmission. Weight this by each incident spectrum, then sum
  over energy to predict two photon counts. These examples use three material-integral
  pairs from the saved reconstruction. The source inverse adjusts both nonnegative
  integrals jointly. This view is a forward diagnostic, not an optimization trace
  or a newly recovered answer.
visual: Traverse three saved rays with exact integrals, energy contributions and predicted
  versus observed counts.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Backproject each saved material sinogram

```beat
id: output
scene: output
frames: 528
caption: Backproject each saved material sinogram
narration: The saved material sinograms contain line integrals in grams per square
  centimeter. Divide each by the source pixel width of zero point one centimeter before
  ramp-filtered backprojection. Clip negative reconstructed values to zero. This converts
  the stored tissue and bone sinograms into density maps in grams per cubic centimeter.
  Both maps reproduce exactly with the audited source wrapper. That saved-intermediate
  replay does not repeat the material-decomposition solver.
visual: Switch from the two native saved material sinograms to their two density maps;
  preserve units and common within-domain scales.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal both synthetic truth maps on matched scales

```beat
id: reference
scene: reference
frames: 576
caption: Reveal both synthetic truth maps on matched scales
narration: 'Now reveal tissue truth beside its saved map, then switch both panels to bone.
  Both comparisons use the same density scale, and dashed purple frames identify synthetic
  truth. Native scores compare both materials inside a truth-derived body mask containing
  eight thousand seven hundred ninety-seven pixels. The tissue and bone errors remain
  separate. These geometric regions are not patient annotations. The reader reveal
  does not imply private evaluation: the released solver packet already includes both
  truth maps.'
visual: Reveal tissue truth halfway through the chapter, then switch to bone; preserve
  matched scales and native pixel geometry.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Every assistance level receives the truth archive

```beat
id: staging
scene: staging
frames: 480
caption: Every assistance level receives the truth archive
narration: At all three assistance levels the local runner copies the entire data
  directory, including the ground truth archive. It contains both material maps and
  both material sinograms. Level two adds an approach; level three adds the software
  design. The audit reproduced these actual file copies while intercepting every installation
  command. Source and evaluation directories are not seeded. These released packets
  therefore do not establish a hidden-reference experiment.
visual: Highlight each assistance packet and explicitly label the copied truth archive.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Array shape changes what the generic scorer evaluates

```beat
id: scoring
scene: scoring
frames: 720
caption: Array shape changes what the generic scorer evaluates
narration: 'The generic scorer chooses a single reference by output shape and key
  ranking. A square map selects tissue truth. A sinogram-shaped output selects the
  bone sinogram. Stacked tissue and bone maps have no matching reference array. Tissue
  truth alone and bone-sinogram truth alone both receive correlation one and mean
  squared error zero, although neither is the requested pair of density maps. Native
  metrics have different limits: cosine correlation misses density scaling, and the
  body mask excludes outside-body changes. No pass thresholds are shipped.'
visual: Compare actual shape-selection controls and three native metric controls;
  distinguish filenames, denominators and missing thresholds.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## A saved two-material result with explicit limits

```beat
id: limits
scene: limits
frames: 528
caption: A saved two-material result with explicit limits
narration: This walkthrough establishes the exact source measurements, released calibration,
  saved two-material result, forward operators and evaluator behavior. It does not
  establish a fresh decomposition, agent capability, private-reference validity, benchmark
  pass or patient accuracy. The small inverse fixture remained unavailable after bounded
  download attempts, and no material optimizer ran. Original arrays are preserved.
  Benchmark and upstream MIT notices retain their separate copyright holders; the
  cited fan-beam simulator is different from this parallel-beam adaptation.
visual: End with verified saved-state facts and unestablished claims, retaining the
  unavailable fixture and original attribution.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```
