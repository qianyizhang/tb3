---
schema: 2
id: imaging101-ct-poisson-lowdose
title: Count photons without substituting another dose outcome
locale: en
purpose: "Explain the exact 300-photon contract and release mismatch."
scope: "Missing matched 300-photon noisy input/truth; no reconstruction or outcome."
recipe: imaging101-poisson-v1
asset_pack: retained-imaging101-poisson-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-ct-poisson-lowdose.md
- presentation/external-tasks/sources/imaging101-ct-poisson-lowdose-resolution.json
- scripts/build_imaging_poisson_assets.py
---
# chapter-0

```beat
id: chapter-0
scene: input
frames: 168
caption: "300 input/truth unmatched · Official Imaging101 acquisition"
narration: "Symbolic rays, no noisy input or reconstruction."
visual: "Symbolic count/log controls, actual output empty, late fixture expected counts."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# chapter-1

```beat
id: chapter-1
scene: operation
frames: 168
caption: "Expectation differs from a Poisson realization"
narration: "Expected photon count depends on line integral; units conflict remains."
visual: "Symbolic count/log controls, actual output empty, late fixture expected counts."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# chapter-2

```beat
id: chapter-2
scene: operation
frames: 168
caption: "Floor illustrative counts before log and weights"
narration: "Canonical count controls teach source formula; no random generation."
visual: "Symbolic count/log controls, actual output empty, late fixture expected counts."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# chapter-3

```beat
id: chapter-3
scene: operation
frames: 168
caption: "Weighted reconstruction is a contract, no recovered output"
narration: "Source TV and advertised plan differ; no solver executed."
visual: "Symbolic count/log controls, actual output empty, late fixture expected counts."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# chapter-4

```beat
id: chapter-4
scene: output
frames: 168
caption: "Actual reconstruction and score remain empty"
narration: "No 300-photon outcome inferred from 1000-photon source arrays."
visual: "Symbolic count/log controls, actual output empty, late fixture expected counts."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# chapter-5

```beat
id: chapter-5
scene: reference
frames: 168
caption: "Reveal expected-count fixture, not noisy input or GT"
narration: "Reader-only 300-photon source physics fixture, native-bin subset and scorer limits."
visual: "Symbolic count/log controls, actual output empty, late fixture expected counts."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# chapter-6

```beat
id: chapter-6
scene: limits
frames: 168
caption: "Recover matching 300 data and resolve units"
narration: "Keep release gap and distinct evaluator reference boundaries."
visual: "Symbolic count/log controls, actual output empty, late fixture expected counts."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
