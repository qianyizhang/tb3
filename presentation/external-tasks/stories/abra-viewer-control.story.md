---
schema: 2
id: abra-viewer-control
title: "Set an ABRA medical viewer to a requested state"
locale: en
purpose: "Distinguish real source CT bytes, prompt-visible index derivation, symbolic state control, and absent observed OHIF output."
scope: "Matched LIDC-IDRI source CT preview plus symbolic viewer; no performed action, verified viewer ordering, final state or score."
recipe: abra-viewer-control-v1
asset_pack: retained-abra-viewer-control-workflow-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/abra-viewer-control.md
- presentation/external-tasks/sources/abra-viewer-control-resolution.json
- scripts/build_abra_viewer_refined_assets.py
---

# See the source, not a claimed viewport

```beat
id: input
scene: input
frames: 288
caption: "Symbolic OHIF; view missing · cancerimagingarchive.net/collection/lidc-idri/"
narration: "Mixed illustration — matched LIDC-IDRI source CT is retained, but the loaded OHIF viewport, slice-index mapping and observed final state are missing; acquire the study through the official TCIA collection. The retained LIDC-IDRI-0003 archive contains 140 CT DICOM files from the manifest series. This fixed preview is archive member 00000001, whose DICOM InstanceNumber is 80. It is not identified as OHIF sliceIndex 80 or 70. The loaded viewer viewport and its ordering are unavailable."
visual: "Actual fixed source CT preview with member/instance badge and top source notice; no claimed viewer state."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Derive the prompt-visible request

```beat
id: route
scene: route
frames: 288
caption: "The prompt requests index 70"
narration: "Pinned tier-one code uses the CT manifest count 140 and integer division by two. It starts from state index zero and asks for slice index 70. The task description says this explicitly; the expected_outcome field duplicates it for scoring."
visual: "140 instances → floor divide by two → requested state slice_index 70, separated from DICOM InstanceNumber."
channels:
  progress: [0, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Inspect a symbolic state-control action

```beat
id: operation
scene: operation
frames: 336
caption: "Stage a local candidate, not an OHIF call"
narration: "A hypothetical set_viewport_slice call with slice_index 70 would request index 70. The adjustable control here changes only a local schematic candidate index; it never calls OHIF or changes a DICOM image. Archive order, instance number, patient position and viewer index are not interchangeable without the loaded viewer ordering."
visual: "Accessible mock index control 0–139 beside a fixed actual source preview and an empty final-state socket."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Separate requested and observed state

```beat
id: output
scene: output
frames: 288
caption: "Requested sliceIndex 70; observed state absent"
narration: "The requested API field is sliceIndex 70. No final OHIF state, tool trace, or score was retained. A matching mock slider position is not a successful task run."
visual: "Requested-state field next to empty observed-state field; no score."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# State the scorer and geometry limits

```beat
id: limits
scene: limits
frames: 288
caption: "A state score is not image truth"
narration: "The scorer maps slice_index to sliceIndex, compares expected fields with default numeric tolerance 0.01, then gives passed over checked fields. Window tasks use tolerance 1.0. It does not verify anatomy or viewer image ordering, and it was not run here."
visual: "Field mapping and tolerance table, source provenance badge, no observed result."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
