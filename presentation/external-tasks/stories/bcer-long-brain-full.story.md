---
schema: 2
id: bcer-long-brain-full
title: "Build the BCER brain tumor artifact and report chain"
locale: en
purpose: "Trace the five required BCER stages, conditional registration, fallback and report limits without inventing a case."
scope: "Source-code-derived symbolic workflow; no matching MRI, output, expert mask, true grade or score."
recipe: bcer-brain-full-v1
asset_pack: retained-bcer-long-brain-full-workflow-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/bcer-long-brain-full.md
- presentation/external-tasks/sources/bcer-long-brain-full-resolution.json
- scripts/build_brain_full_refined_assets.py
---

# Input

```beat
id: input
scene: input
frames: 264
caption: "Four matched modalities, unavailable here"
narration: "All four brain MRI sequences are required. No patient pixels or case-matched annotation are shown."
visual: "Task-specific schema/operation; no patient or output invented."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Route

```beat
id: route
scene: route
frames: 264
caption: "Register only when geometry requires it"
narration: "Registration of T2 and FLAIR to T1c is conditional. The runner-loaded registry requires five other stages and does not count registration when co-registered input makes it unnecessary."
visual: "Task-specific schema/operation; no patient or output invented."
channels:
  progress: [0, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 360
caption: "Inspect each source-contract boundary"
narration: "The segmentation and WT mask feed ROI features and a rule-based grade. With missing dependencies, segmentation can fall back to a heuristic mask. The report reads run state, sequence mapping and feature evidence; its brain JSON does not directly carry the grade classifier output."
visual: "Task-specific schema/operation; no patient or output invented."
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
frames: 264
caption: "Five empty artifact paths"
narration: "Five artifact paths and five stage successes form the ten-check completion ratio. The seven invariants and separate five-tool success rule remain distinct. Every case value here is unset."
visual: "Task-specific schema/operation; no patient or output invented."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 264
caption: "Structural checks leave clinical truth untested"
narration: "A nonempty, affine-matched mask may still be heuristic. No mask or grade is compared with truth, no report confirms clinical accuracy, and no patient case was run."
visual: "Task-specific schema/operation; no patient or output invented."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
