---
schema: 2
id: imaging101-mri-t2-mapping
title: Trace echo decay without inventing a fitted T2 map
locale: en
purpose: "Explain actual magnitude echoes, units and log/nonlinear fit contracts."
scope: "Synthetic source; M0/T2 generic reference ambiguity; no participant fit."
recipe: imaging101-t2-mapping-v1
asset_pack: retained-imaging101-t2-mapping-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-mri-t2-mapping.md
- presentation/external-tasks/sources/imaging101-mri-t2-mapping-resolution.json
- scripts/build_imaging_t2_mapping_assets.py
---
# synthetic-echo-target-gap

```beat
id: synthetic-echo-target-gap
scene: input
frames: 168
caption: "Synthetic echoes; target gap · Official Imaging101 acquisition"
narration: "Actual synthetic echo inputs present; no participant T2 fit and generic target ambiguous."
visual: "Actual synthetic echo magnitudes; symbolic fitting rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# signal-noise-units

```beat
id: signal-noise-units
scene: operation
frames: 168
caption: "Keep milliseconds and magnitude signal units distinct"
narration: "Expected exponential signal and per-channel noise are separate from magnitude realization."
visual: "Actual synthetic echo magnitudes; symbolic fitting rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# native-echo-display

```beat
id: native-echo-display
scene: operation
frames: 168
caption: "Inspect native echoes with one display scale"
narration: "TE 10/50/100 ms native previews; no per-echo normalization or fitting."
visual: "Actual synthetic echo magnitudes; symbolic fitting rules; actual output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# log-nonlinear-rules

```beat
id: log-nonlinear-rules
scene: operation
frames: 168
caption: "Separate log-domain and signal-domain fit rules"
narration: "Unweighted log OLS and LM fallback; no statistical or native fit claim."
visual: "Actual synthetic echo magnitudes; symbolic fitting rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# absent-participant-map

```beat
id: absent-participant-map
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Actual synthetic echo magnitudes; symbolic fitting rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# late-target-mask-rules

```beat
id: late-target-mask-rules
scene: reference
frames: 168
caption: "Reveal source-truth and magnitude-scoring rules"
narration: "T2/M0/tissue mask solver-visible; generic target and masked/full denominators need reconciliation."
visual: "Actual synthetic echo magnitudes; symbolic fitting rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# unresolved-target-units

```beat
id: unresolved-target-units
scene: limits
frames: 168
caption: "Reconcile T2/M0 target, units and mask"
narration: "No matched live reference/threshold lineage, participant map or clinical result."
visual: "Actual synthetic echo magnitudes; symbolic fitting rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
