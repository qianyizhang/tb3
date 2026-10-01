---
schema: 2
id: imaging101-plane-wave-ultrasound
title: Trace RF phase without inventing a focused image
locale: en
purpose: "Explain native ADC channels, steering and coherent compounding rules."
scope: "Physical phantom RF only; no participant B-mode or score."
recipe: imaging101-plane-wave-ultrasound-v1
asset_pack: retained-imaging101-plane-wave-ultrasound-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-plane-wave-ultrasound.md
- presentation/external-tasks/sources/imaging101-plane-wave-ultrasound-resolution.json
- scripts/build_imaging_plane_wave_assets.py
---
# phantom-rf-source-gap

```beat
id: phantom-rf-source-gap
scene: input
frames: 168
caption: "Phantom RF; B-mode missing · Official Imaging101 acquisition"
narration: "Actual phantom RF is present; participant B-mode and matched generic binding are unresolved."
visual: "Actual phantom ADC inputs; authored phase mechanics; B-mode output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# rf-steering-units

```beat
id: rf-steering-units
scene: operation
frames: 168
caption: "Keep RF, steering and time origins distinct"
narration: "Real ADC codes are not IQ or B-mode; the two phantoms have different acquisition starts."
visual: "Actual phantom ADC inputs; authored phase mechanics; B-mode output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# native-rf-traces

```beat
id: native-rf-traces
scene: operation
frames: 168
caption: "Inspect exact native RF traces"
narration: "Three full raw ADC traces keep phantom, angle and time origin visible; no filtering or focusing."
visual: "Actual phantom ADC inputs; authored phase mechanics; B-mode output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# coherent-envelope-rules

```beat
id: coherent-envelope-rules
scene: operation
frames: 168
caption: "Compound phase before envelope detection"
narration: "Complex angle images are averaged before Hilbert-envelope power compression; no method executed."
visual: "Actual phantom ADC inputs; authored phase mechanics; B-mode output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# absent-bmode-output

```beat
id: absent-bmode-output
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Actual phantom ADC inputs; authored phase mechanics; B-mode output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# late-baseline-scorer-rules

```beat
id: late-baseline-scorer-rules
scene: reference
frames: 168
caption: "Reveal source baseline and scorer binding rules"
narration: "B-mode baselines are solver-visible, differ from saved outputs and use incompatible generic threshold names."
visual: "Actual phantom ADC inputs; authored phase mechanics; B-mode output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# unresolved-lineage-rights

```beat
id: unresolved-lineage-rights
scene: limits
frames: 168
caption: "Resolve selected phantom, baseline and rights"
narration: "No participant B-mode, image-quality measurement, clinical interpretation or numerical outcome."
visual: "Actual phantom ADC inputs; authored phase mechanics; B-mode output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
