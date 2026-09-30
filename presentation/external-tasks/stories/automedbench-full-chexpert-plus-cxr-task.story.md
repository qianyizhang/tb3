---
schema: 2
id: automedbench-full-chexpert-plus-cxr-task
title: "Generate a CheXpert Plus report"
locale: en
purpose: "Explain single-view report output and whole-submission scoring without patient findings."
scope: "Symbolic contract; exact staged image, reference report, case/patient join and model output absent."
recipe: automed-chexpert-report-v1
asset_pack: symbolic-automed-chexpert-report-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-chexpert-plus-cxr-task.md
- presentation/external-tasks/sources/automedbench-full-chexpert-plus-cxr-task-resolution.json
- scripts/build_automed_chexpert_report_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "JPEG absent \u00b7 aimi.stanford.edu/datasets/chexpert-plus"
narration: "Inspect the required single frontal JPEG study input. Full staged case IDs and patient mapping are absent. Official Stanford DICOM and mirror JPEGs are distinct; no physical geometry or patient finding is inferred."
visual: "Source-specific symbolic input contract; no patient pixels, narrative or results."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 288
caption: "Public schema differs from original14 labels"
narration: "The public scoring schema contains twelve binary text regex concepts. These are not independent image findings. No patient narrative or label is shown. Inspect Lite and Standard method guidance without claiming weights or current availability."
visual: "Source-specific symbolic helper contract; no patient pixels, narrative or results."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 288
caption: "Generate one report from the allowed view"
narration: "Verify view and case identity, provision the chosen method and preprocessing, generate constrained text and submit every discovered case. This operation is symbolic and does not run a model or reveal private reports."
visual: "Source-specific symbolic operation contract; no patient pixels, narrative or results."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 288
caption: "Empty report \u00b7 every case must be valid"
narration: "The singular agent_outputs case report path requires UTF8 decoding and ASCII printable characters, forty to eight thousand characters and at least twenty alphabetic characters. The report stays empty. Any invalid or missing case fails the whole submission gate."
visual: "Source-specific symbolic output contract; no patient pixels, narrative or results."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 288
caption: "Text proxies do not establish clinical accuracy"
narration: "The configured score combines mean observation F1 and mean ROUGE-L with weights point seven and point three across all case IDs. Findings is preferred, otherwise full text. Empty positive sets receive F1 one by convention. Micro diagnostics are separate; no metric, rating or patient outcome is observed."
visual: "Source-specific symbolic limits contract; no patient pixels, narrative or results."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
