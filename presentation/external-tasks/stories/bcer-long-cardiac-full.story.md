---
schema: 2
id: bcer-long-cardiac-full
title: "Turn cardiac cine MRI into BCER artifacts and a report"
locale: en
purpose: "Explain conditional reconstruction, phase handling, segmentation-derived group rules, and structural checks without a patient outcome."
scope: "Source-code-derived symbolic workflow; no matched cine, output, reference or task run."
recipe: bcer-cardiac-full-v1
asset_pack: retained-bcer-long-cardiac-full-workflow-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/bcer-long-cardiac-full.md
- presentation/external-tasks/sources/bcer-long-cardiac-full-resolution.json
- scripts/build_cardiac_full_refined_assets.py
---

# Identify the cine input

```beat
id: input
scene: input
frames: 264
caption: "One cine case, absent here"
narration: "BCER accepts one case-matched cine NIfTI or raw cine H5. The source slot is empty; neither patient frames nor a disease-group answer is available in this pack."
visual: "Empty cine input slot and common-header official acquisition notice."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Choose the conditional route

```beat
id: route
scene: route
frames: 288
caption: "Reconstruct only raw H5"
narration: "Raw cine H5 takes a conditional reconstruction route to NIfTI before segmentation. Cine NIfTI enters directly. Reconstruction is in the goal template but not one of the five required stage-success keys. The branch is schematic, not an observed conversion."
visual: "Accessible H5 versus NIfTI route switch with no case dimensions or rendered frames."
channels:
  progress: [0, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Inspect phase and artifact operations

```beat
id: operation
scene: operation
frames: 360
caption: "Phase choice changes what can be measured"
narration: "A 4D cine can be split into 3D frames; valid one-based ED and ES metadata select phases, while absent valid metadata leaves all frames for segmentation. One 3D phase is not a temporal curve. The classifier derives volume and ejection-fraction quantities from segmentation frames. The feature CSV is a parallel required artifact, not its numeric input. No measured values or group are shown."
visual: "Static three-state phase provenance selector, source-label legend, and parallel feature/classifier artifact paths."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Show the required empty outputs

```beat
id: output
scene: output
frames: 288
caption: "Four artifact paths remain empty"
narration: "The task requires segmentation NIfTI, feature CSV, classification JSON with predicted_group, and report JSON. The report is generated from run state and artifacts, not an independent clinical reference. No artifact, phase volume, group or finding was produced for this explainer."
visual: "Four empty output sockets and a nine-item structural tally definition, without completion marks."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Keep reference and scoring boundaries

```beat
id: limits
scene: limits
frames: 288
caption: "Structural checks do not prove correctness"
narration: "Five stage successes plus four artifact paths form the completion ratio, with separate success and nonempty-file checks. A nonempty UNCLASSIFIED group can pass a field check. The source classifier can read Group from Info.cfg and echo it, so this code does not prove answer isolation. No expert mask, independent disease group or clinical accuracy evaluation is present."
visual: "No-reference boundary, official source route, and unobserved score state."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
