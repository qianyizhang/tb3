---
schema: 2
id: automedbench-full-mimic-cxr-report-task
title: "Generate MIMIC findings from supplied views"
locale: en
purpose: "Explain multi-view findings output and whole-submission scoring without patient findings."
scope: "Symbolic contract; exact staged image, reference report, case/patient join and model output absent."
recipe: automed-mimic-report-v1
asset_pack: symbolic-automed-mimic-report-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-mimic-cxr-report-task.md
- presentation/external-tasks/sources/automedbench-full-mimic-cxr-report-task-resolution.json
- scripts/build_automed_mimic_report_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Images absent \u00b7 physionet.org/content/mimic-cxr/2.1.0/"
narration: "Inspect the required one or more JPEG views study input. Full staged case IDs and patient mapping are absent. Original MIMIC DICOM and JPG derivative differ. Exact staged view count and subject-study-image join are absent; no patient finding or quantitative intensity inferred."
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
caption: "Public schema differs from original 14 labels"
narration: "The public scoring schema contains twelve binary text regex concepts. These are not independent image findings. No patient narrative or label is shown. Lite compares suitable report pipelines; Standard compares at least 3. No fixed Lite checkpoint or measured performance."
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
caption: "Generate findings from all supplied views"
narration: "Verify listed views, grouping and case identity, provision the chosen method and preprocessing, generate constrained text and submit every discovered case. This operation is symbolic and does not run a model or reveal private reports."
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
