---
schema: 2
id: imaging101-photoacoustic-tomography
title: Trace acoustic arrivals without inventing a pressure image
locale: en
purpose: "Explain native signed signals, time of flight and backprojection source rules."
scope: "Synthetic acoustic input only; no tissue or participant reconstruction."
recipe: imaging101-photoacoustic-tomography-v1
asset_pack: retained-imaging101-photoacoustic-tomography-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-photoacoustic-tomography.md
- presentation/external-tasks/sources/imaging101-photoacoustic-tomography-resolution.json
- scripts/build_imaging_photoacoustic_assets.py
---
# synthetic-pressure-and-source-gap

```beat
id: synthetic-pressure-and-source-gap
scene: input
frames: 168
caption: "Synthetic acoustics; no reconstruction · Official Imaging101 acquisition"
narration: "Native synthetic pressure signals are present, but no tissue scan or participant reconstruction."
visual: "Native synthetic pressure signals; authored geometric rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# pressure-time-detector-contract

```beat
id: pressure-time-detector-contract
scene: operation
frames: 168
caption: "Keep pressure, time and geometry units distinct"
narration: "Signed relative pressure and time of flight are not photon counts or calibrated optical absorption."
visual: "Native synthetic pressure signals; authored geometric rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# native-detector-trace-selection

```beat
id: native-detector-trace-selection
scene: operation
frames: 168
caption: "Inspect exact native detector traces"
narration: "Three full detector time traces show native bipolar signals; no filtering or reconstruction."
visual: "Native synthetic pressure signals; authored geometric rules; actual output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# signed-filter-and-backprojection-rule

```beat
id: signed-filter-and-backprojection-rule
scene: operation
frames: 168
caption: "Trace signed filtering and geometric weighting"
narration: "Signed derivative and nearest arrival samples feed solid-angle weighting; normalization removes absolute amplitude."
visual: "Native synthetic pressure signals; authored geometric rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# participant-output-empty

```beat
id: participant-output-empty
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Native synthetic pressure signals; authored geometric rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# reader-support-and-crop-metrics

```beat
id: reader-support-and-crop-metrics
scene: reference
frames: 168
caption: "Reveal binary-support and crop-scoring rules"
narration: "Binary support truth is solver-visible; source crop and generic full-image denominators differ."
visual: "Native synthetic pressure signals; authored geometric rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# reopen-calibration-and-reference-lineage

```beat
id: reopen-calibration-and-reference-lineage
scene: limits
frames: 168
caption: "Resolve calibration, normalization and scorer lineage"
narration: "No tissue image, calibrated pressure, optical absorption or numerical outcome."
visual: "Native synthetic pressure signals; authored geometric rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
