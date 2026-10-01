---
schema: 2
id: imaging101-usct-fwi
title: Trace USCT signals without inventing a speed map
locale: en
purpose: "Explain native complex observations, acoustic fitting and reconstruction-reference boundaries."
scope: "Numerical phantom signals only; true speed and participant output absent."
recipe: imaging101-usct-fwi-v1
asset_pack: retained-imaging101-usct-fwi-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-usct-fwi.md
- presentation/external-tasks/sources/imaging101-usct-fwi-resolution.json
- scripts/build_imaging_usct_fwi_assets.py
---
# native-observations-and-source-gap

```beat
id: native-observations-and-source-gap
scene: input
frames: 168
caption: "Phantom signals; true speed / output missing · Official Imaging101 acquisition"
narration: "Numerical phantom observations retained; independent true speed, calibrated pressure and participant output absent."
visual: "Native real-component cells; authored fitting rules; reference selection late, output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# frequency-geometry-and-operator-contract

```beat
id: frequency-geometry-and-operator-contract
scene: operation
frames: 168
caption: "Keep grid units, time absence and muting explicit"
narration: "Frequency-domain complex cells have no time sampling or calibrated pressure. Metadata geometry conflicts with grid spacing."
visual: "Native real-component cells; authored fitting rules; reference selection late, output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# native-frequency-cell-selection

```beat
id: native-frequency-cell-selection
scene: operation
frames: 168
caption: "Inspect three exact native frequency displays"
narration: "Signed real components at three source frequencies retain native receiver/source indices and distinct display scales."
visual: "Native real-component cells; authored fitting rules; reference selection late, output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# source-fit-gradient-and-line-search

```beat
id: source-fit-gradient-and-line-search
scene: operation
frames: 168
caption: "Fit source amplitude before bounded slowness updates"
narration: "Authored scalar amplitude fit teaches the formula; no native forward field, gradient, NCG update or convergence computed."
visual: "Native real-component cells; authored fitting rules; reference selection late, output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# participant-map-empty

```beat
id: participant-map-empty
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Native real-component cells; authored fitting rules; reference selection late, output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# reader-reference-and-backend-rules

```beat
id: reader-reference-and-backend-rules
scene: reference
frames: 168
caption: "Reveal source versus generic reconstruction references"
narration: "Two saved reconstructions are not true speed; first generic reference differs from source baseline despite the same range-normalized error formula."
visual: "Native real-component cells; authored fitting rules; reference selection late, output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# reopen-calibration-truth-and-runtime

```beat
id: reopen-calibration-truth-and-runtime
scene: limits
frames: 168
caption: "Resolve geometry, pressure units, runtime and true reference"
narration: "No current acoustic simulation, reconstructed speed, phantom truth, clinical property or metric."
visual: "Native real-component cells; authored fitting rules; reference selection late, output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
