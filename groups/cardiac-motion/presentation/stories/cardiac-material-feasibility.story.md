---
schema: 2
id: cardiac-material-feasibility
title: 'Four ultrasound planes to material deformation'
locale: en
purpose: Explain how retained BR-029 author methods turn four synthetic ultrasound planes and a supplied initial material mesh into motion and strain fields, then compare against private simulator trajectories.
scope: One STRAUS simulation and saved author results; local noncommercial teaching, no model trial or clinical strain claim.
recipe: cardiac-material-v1
asset_pack: retained-cardiac-material-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/cardiac-motion/presentation/briefs/tb3-cardiac-material-feasibility.md
- groups/cardiac-motion/presentation/sources/cardiac-material-audit.json
- groups/cardiac-motion/presentation/sources/cardiac-material-resolution.json
- docs/evidence/br029-dynamic-heart-results.json
- docs/evidence/br029-dynamic-heart-tissue-results.json
- presentation/task-explorer/cardiac-material/manifest.json
---

# Four views do not determine every material trajectory

## Observe the four fixed planes

```beat
id: inputs
scene: inputs
frames: 168
caption: Four synthetic ultrasound views, 30 frames each
narration: The author receives three long-axis views and one short-axis view, sampled on fixed planes from one healthy simulator. Each grayscale image is one hundred ninety-two by one hundred ninety-two pixels at zero point seven five millimetres per pixel. Later source meshes and strain fields are not inputs.
visual: Show the four actual source-derived input cines with plane names and calibrated frame index. Keep every saved trajectory and private reference unmounted.
channels:
  phase: [0, 1]
  helper: [0, 0]
  output: [0, 0]
  reference: [0, 0]
```

## Start from supplied material anatomy

```beat
id: initial
scene: initial
frames: 144
caption: Initial points and tetrahedra are already given
narration: The public task also supplies eleven thousand three hundred seventy initial material points and forty-seven thousand one hundred eighty-six tetrahedra. Their IDs and AHA labels are fixed. The task is to place those same points at later frames, not to infer the first mesh.
visual: Show the native plane-one first image alongside a fixed-ID sample of the actual initial source mesh and one selected AHA-seven tetrahedron. No later mesh appears.
channels:
  phase: [0, 0]
  helper: [1, 1]
  output: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Track near-plane evidence into a saved affine motion

```beat
id: tracking
scene: tracking
frames: 192
caption: Sparse image observations constrain a global map
narration: Material seeds initially within one point five millimetres of each plane are followed in two dimensions by the retained author video method. The saved video-affine baseline fits one global twelve-parameter map and moves every material ID. Displayed blue seed locations are projections of that saved result, not measured ground truth.
visual: Animate the actual long-axis sixty-degree cine with a deterministic subset of saved projected seed positions. A fixed-camera sampled mesh moves beside it. Keep private simulator motion hidden.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [1, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Deform a tetrahedron with fixed IDs

```beat
id: tetra
scene: tetra
frames: 168
caption: Four corresponding vertices define the deformation
narration: The later tissue fit keeps the initial tetrahedral connectivity. For one pinned AHA-seven cell, the three reference edge columns form D m and the saved current edges form D s. Their product D s times inverse D m gives F. The magnified edges align vertex zero to remove translation and share a fixed millimetre scale.
visual: Draw the same four retained vertices and six cell edges at reference and current frames, with source-derived sampled body points for context. Show the saved tissue-fit state only after the output gate.
channels:
  phase: [0, 0.5517241379310345]
  helper: [1, 1]
  output: [1, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Separate tensor arithmetic from recovered motion

```beat
id: strain
scene: strain
frames: 192
caption: F, E, J and directional strain answer different questions
narration: The saved tissue export provides full F and Green–Lagrange E tensors. J is determinant F. Directional engineering strain is the length change of a source anatomical axis, not a component of E. Three positive-AHA tetrahedra have no usable axes; they retain geometry and J, but their direction values stay unavailable.
visual: Show numeric saved fields for the pinned valid tetrahedron and an explicit unavailable-direction card for a separate positive-AHA cell. Keep the fixed millimetre projection and no reference overlay.
channels:
  phase: [0.5517241379310345, 0.5517241379310345]
  helper: [1, 1]
  output: [1, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Reveal the simulator material reference

```beat
id: comparison
scene: comparison
frames: 192
caption: Two valid fits, different motion errors
narration: Reveal the withheld healthy simulator point trajectories only for the reader. Video affine has three point seven six millimetres material RMSE and sixteen point six seven percentage points radial strain error. The development-informed tissue fit changes these to four point zero three millimetres and six point seven nine percentage points. The comparison is endpoint-only, not a controlled image ablation.
visual: Overlay fixed-ID sampled simulator points in solid gold and synchronize the thirty-frame radial engineering-strain curves and retained full-body metrics. Mount reference DOM only after reader reveal.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [1, 1]
  reference: [0, 1]
cut: intentional-cut
```

## Volume can agree while trajectories fail

```beat
id: controls
scene: controls
frames: 144
caption: Static geometry is a counterexample
narration: A static initial body has just one point eight seven percent mean tissue-volume error, yet six point one nine millimetres material motion error. The tissue fit has one point three five percent volume error but still four point zero three millimetres motion error. Positive Jacobians and a plausible volume curve do not establish recovered tissue motion.
visual: Hold one native frame, fixed-camera body and retained tissue-volume value and separate comparison table. Place static and both video-method metrics in distinct rows; label the source reference as privileged.
channels:
  phase: [0.3103448275862069, 0.3103448275862069]
  helper: [1, 1]
  output: [1, 1]
  reference: [1, 1]
cut: intentional-cut
```

## End at the study boundary

```beat
id: limits
scene: limits
frames: 168
caption: One simulation, no clinical strain claim
narration: This author feasibility study has one healthy simulation and thirty correlated frames, not thirty patients. Directional statistics use thirty-one thousand two hundred forty-one of thirty-one thousand two hundred forty-four positive-AHA cells. The source frame duration, patient strain, strain rate, force balance, blood flow, cavity ejection fraction and diagnosis are unestablished. No method passes all provisional targets.
visual: Keep the supplied initial body, saved tissue mesh, reader-revealed simulator and limits together at a fixed source frame, including the missing-axis count.
channels:
  phase: [0.5517241379310345, 0.5517241379310345]
  helper: [1, 1]
  output: [1, 1]
  reference: [1, 1]
cut: intentional-cut
```
