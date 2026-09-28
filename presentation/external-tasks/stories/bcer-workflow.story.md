---
schema: 2
id: bcer-workflow
title: Complete a prostate MRI workflow
locale: en
purpose: Trace native sequence geometry and public artifact dependencies, then separate
  stage success, completion and invariant checks.
scope: Native PI-CAI inputs and public BCER checks. Nonclinical fixtures; no pipeline or model run.
recipe: bcer-workflow-v1
asset_pack: retained-bcer-workflow-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/bcer.md
- presentation/external-tasks/sources/bcer-workflow-audit.json
- scripts/audit_bcer_workflow.py
- scripts/build_bcer_workflow_assets.py
---

# Canonical BCER workflow explanation

## Three contrasts enter one workflow

```beat
id: inputs
scene: inputs
frames: 240
caption: Three contrasts enter one workflow
narration: 'The full prostate task requires T2-weighted MRI and at least one diffusion
  input: ADC or high-b diffusion. This retained PI-CAI example contains all three.
  Native planes differ in contrast, resolution and field of view. It is a representative
  input preparation, not an official BCER split or completed pipeline.'
visual: Three actual native MRI planes, with sequence selection and explicit acquisition
  grids.
channels:
  view:
  - 0
  - 1
```

## Modality names are part of the contract

```beat
id: manifest
scene: manifest
frames: 336
caption: Modality names are part of the contract
narration: The earlier local sample manifest uses lowercase modality names. The pinned
  builder and contract use T2w, ADC and DWI_highb, and their lookup is case-sensitive.
  A fresh derived manifest satisfies the exact selected rule while the original bytes
  remain unchanged. Filename-based modality flags do not prove scan quality or inspect
  the underlying DICOM metadata.
visual: Preserved original fields beside canonical derived fields and the explicit
  AND/OR rule.
channels:
  view:
  - 0
  - 0
cut: intentional-cut
```

## Follow physical coordinates across native grids

```beat
id: geometry
scene: geometry
frames: 384
caption: Follow physical coordinates across native grids
narration: White crosses follow three author ruler points through each image header.
  They are not lesion locations. T2 uses point-three-millimeter in-plane spacing;
  diffusion uses two millimeters. Native indices therefore differ at the same LPS
  physical point. These panels have different fields of view and are not shown at
  a common physical scale. Header mapping is not an anatomical registration result.
visual: Three discrete physical points mapped into native pixel centers; no image
  warp or mask.
channels:
  view:
  - 0
  - 1
cut: intentional-cut
```

## Resolve the source plan’s artifact dependencies

```beat
id: dependencies
scene: dependencies
frames: 528
caption: "Resolve the source plan\u2019s artifact dependencies"
narration: The source planning template has eight nodes. Follow a dependency to find
  the producing tool and its returned path. Lesion detection uses the ADC registration
  result and the prostate mask. DWI registration and feature extraction are optional
  in this template, but the benchmark contract requires successful feature extraction.
  The template and benchmark have different roles. Highlighted nodes illustrate the
  static plan, not an agent execution trace.
visual: Exact eight-node template dependencies with selected tool and typed output-path
  example.
channels:
  view:
  - 0
  - 1
cut: intentional-cut
```

## Return four typed artifact paths

```beat
id: artifacts
scene: artifacts
frames: 384
caption: Return four typed artifact paths
narration: The contract requires paths to a prostate mask, lesion-candidate JSON,
  feature CSV and report JSON. Path existence contributes to completion. Separate
  invariants check nonempty mask data, matching geometry, basic candidate fields,
  a CSV data row and a truthy JSON value. These checks do not independently establish
  a correct gland boundary, valid lesion localization or diagnostic accuracy.
visual: Four named output fields and the selected invariant; no invented patient output.
channels:
  view:
  - 0
  - 1
cut: intentional-cut
```

## Three check results answer different questions

```beat
id: metrics
scene: metrics
frames: 672
caption: Three check results answer different questions
narration: Five nonclinical fixtures replay selected pure checks. Six successful stage
  records can pass the base success rule with missing files and completion of six
  out of ten. Empty existing files reach ten out of ten while all five invariants
  fail. A one-voxel synthetic grid and trivial tables pass structural checks. Shifting
  its origin breaks geometry. Failing the report stage breaks base success despite
  valid files. No controller, fault harness or medical model was run.
visual: Five reproducible fixture outcomes, moving selected row and a separate nonclinical
  grid witness.
channels:
  view:
  - 0
  - 1
cut: intentional-cut
```

## Keep output provenance beside its status

```beat
id: provenance
scene: provenance
frames: 432
caption: Keep output provenance beside its status
narration: "The pinned segmentation source has a degraded geometric fallback when\
  \ its MONAI dependency check raises. It builds an ellipse from array dimensions;\
  \ this explanation does not execute it. Retain degraded-mode flags and warnings\
  \ with artifacts. Metrics documentation describes success as requiring full completion,\
  \ but this contract\u2019s implementation computes stage success, completion and\
  \ invariants separately. The pinned code and bounded replay support the distinction\
  \ shown here."
visual: Public source provenance and documented-versus-implemented metric boundary,
  without medical fallback execution.
channels:
  view:
  - 0
  - 0
cut: intentional-cut
```

## A workflow contract needs several kinds of evidence

```beat
id: limits
scene: limits
frames: 288
caption: A workflow contract needs several kinds of evidence
narration: We have native MRI inputs, matching prepared arrays, a pinned workflow
  contract and five nonclinical validator examples. We do not have a retained BCER
  prostate mask, candidate result, feature table or clinical report. This explains
  how to inspect workflow evidence. It does not measure anatomical accuracy, model
  performance or other BCER task families.
visual: Four scope cards summarizing native data, recovered mechanics and missing
  clinical result evidence.
channels:
  view:
  - 0
  - 0
cut: intentional-cut
```
