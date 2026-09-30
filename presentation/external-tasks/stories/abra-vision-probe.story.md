---
schema: 2
id: abra-vision-probe
title: Identify an ABRA image modality or display treatment
locale: en
purpose: "Explain modality/display classification with matched-source CT windows and symbolic unavailable conditions."
scope: "Source CT derivatives; original task PNG and results absent. Named Gaussian control actually uses uniform replacement."
recipe: abra-vision-probe-v1
asset_pack: retained-abra-vision-probe-source-example-v3
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/abra-vision-probe.md
- presentation/external-tasks/sources/abra-vision-probe-resolution.json
- scripts/build_abra_vision_probe_assets.py
---

# input

```beat
id: input
scene: input
frames: 168
caption: "Task PNG absent · source CT · github.com/Luab/ABRA"
narration: "Exact selected PNG is absent; recover through official ABRA setup. Source CT previews are independent derivatives; other missing modalities and toy cells remain explicitly labeled."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# condition-1

```beat
id: condition-1
scene: operation
frames: 168
caption: "Default modality PNG absent; CT window examples only"
narration: "Condition and five selected index sockets follow canonical channels. Source CT previews are not recovered task PNGs; participant result remains absent."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [0.0, 0.0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# condition-2

```beat
id: condition-2
scene: operation
frames: 168
caption: "Replacement ignores original pixel values"
narration: "Condition and five selected index sockets follow canonical channels. Source CT previews are not recovered task PNGs; participant result remains absent."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [0.2, 0.2]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# condition-3

```beat
id: condition-3
scene: operation
frames: 168
caption: "CT lung window: C=-600 / W=1500 HU"
narration: "Condition and five selected index sockets follow canonical channels. Source CT previews are not recovered task PNGs; participant result remains absent."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [0.4, 0.4]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# condition-4

```beat
id: condition-4
scene: operation
frames: 168
caption: "CT soft tissue: C=40 / W=400 HU"
narration: "Condition and five selected index sockets follow canonical channels. Source CT previews are not recovered task PNGs; participant result remains absent."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [0.6, 0.6]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# condition-5

```beat
id: condition-5
scene: operation
frames: 168
caption: "MRI signal: p01 to p99, not HU"
narration: "Condition and five selected index sockets follow canonical channels. Source CT previews are not recovered task PNGs; participant result remains absent."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [0.8, 0.8]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# condition-6

```beat
id: condition-6
scene: operation
frames: 168
caption: "Uniform uint8 replacement, despite noise_gaussian name"
narration: "Condition and five selected index sockets follow canonical channels. Source CT previews are not recovered task PNGs; participant result remains absent."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [1.0, 1.0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# output

```beat
id: output
scene: output
frames: 168
caption: "Submit one A/B/C/D letter · actual answer absent"
narration: "The formatting illustration is not a generated case answer or model response."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [0.4, 0.4]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# reference

```beat
id: reference
scene: reference
frames: 168
caption: "Reveal generator label rules, no case answer"
narration: "Expected letters derive from modality or pipeline metadata. Replacement noise maps to D, N/A; no clinical reference is supplied."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [0.4, 0.4]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# limits

```beat
id: limits
scene: limits
frames: 168
caption: "Initial viewport context limits image-only claims"
narration: "System window and level may provide context. Only submit_answer is callable, with three turns and no oracle."
visual: "Symbolic nonclinical transfer with linked actual PNG gap warning."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
