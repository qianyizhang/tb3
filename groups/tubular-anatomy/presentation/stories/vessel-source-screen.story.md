---
schema: 2
id: vessel-source-screen
title: Curate source evidence for local vessel repair
locale: en
purpose: Inspect actual TopCoW source images and annotation configurations before admitting a local
  connection-repair task.
scope: 'BR-025 author source curation: twelve edge files, four public MRA candidates, no admitted
  defect fixture or model trial. Reference geometry is mask-derived; no clinical adjudication.'
recipe: vessel-source-v1
asset_pack: retained-vessel-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/tubular-anatomy/presentation/briefs/tb3-vessel-source-screen.md
- groups/tubular-anatomy/experiments/br025/protocol.md
- docs/research-rounds/BR-025-vessel-connectivity.md
- docs/evidence/br025-curation.json
- groups/tubular-anatomy/presentation/sources/vessel-source-audit.json
- presentation/task-explorer/vessel-source/manifest.json
- scripts/build_vessel_source_assets.py
- scripts/build_resect_assets.py
- scripts/build_respiratory_assets.py
---

# Source curation before local vessel repair

## sources

```beat
id: sources
frames: 240
scene: sources
caption: Start with four actual MRA sources, before a repair task exists.
narration: The author screened the first twelve MRA edge-label files and selected four public training
  subjects. These projections show the provided Circle of Willis boxes, each fitted independently.
  Complete native images, masks, edge labels and mask-derived graphs are author curation inputs.
  Paired CTA labels were checked, but CTA images were not reviewed.
visual: Four actual MRA projections without reference overlays or candidate annotation states.
channels:
  scan:
  - 0
  - 0
  reference:
  - 0
  - 0
  output:
  - 0
  - 0
```

## states

```beat
id: states
frames: 264
scene: states
caption: Reveal annotation configurations and possible control roles.
narration: Reveal the source labels for the posterior communicating arteries, or Pcoms. The panel
  includes bilateral, absent and asymmetric configurations. They motivate possible broken-connection,
  false-bridge and unchanged controls. A source annotation marked absent does not establish congenital
  absence, and no defective prediction has been admitted.
visual: Reveal orange right, teal left and blue other labels; plus/minus denote annotation present/absent.
channels:
  scan:
  - 0
  - 0
  reference:
  - 0
  - 1
  output:
  - 0
  - 0
cut: intentional-cut
```

## inspect

```beat
id: inspect
frames: 288
scene: inspect
caption: Move through native sections; a projection hides depth.
narration: Case 007 has fourteen retained native sections spanning both annotated Pcoms with a one-slice
  halo. The paired panels share crop, scale and a fixed intensity window. Only the viewed slice
  changes. This author view was chosen from annotation extent; it is not a frozen solver crop. Native
  axes are oblique, and no resampling is applied.
visual: Sweep slices 104 through 117 with image-only and corresponding reference overlay side by
  side.
channels:
  scan:
  - 0
  - 1
  reference:
  - 1
  - 1
  output:
  - 0
  - 0
cut: intentional-cut
```

## contacts

```beat
id: contacts
frames: 264
scene: contacts
caption: Check local contacts on the three-dimensional source mask.
narration: Each present Pcom label is one twenty-six-connected component and touches the expected
  internal carotid and posterior cerebral labels. Corner contact counts under this rule. These checks
  are computed on the mask, not inferred from a projection. They do not independently adjudicate
  anatomy. A class-label mistake that disappears when labels merge is not a binary connectivity
  defect.
visual: Source MIP with separately identified measured label contacts and voxel/component counts.
channels:
  scan:
  - 1
  - 1
  reference:
  - 1
  - 1
  output:
  - 0
  - 0
cut: intentional-cut
```

## nodes

```beat
id: nodes
frames: 240
scene: nodes
caption: Use stored physical coordinates to check technical alignment.
narration: Project the mask-derived graph nodes using the same native affine and region. Distances
  to foreground voxel centres reproduce the retained source screen. Shared boundary nodes recur
  under different vessel labels, so entry counts are not independent observations. The rendered
  circles deduplicate identifiers. This corroborates coordinates, not every graph edge or independent
  anatomical truth.
visual: Source 007 node projections and exact entry count with maximum nearest-foreground distance.
channels:
  scan:
  - 1
  - 1
  reference:
  - 1
  - 1
  output:
  - 0
  - 0
cut: intentional-cut
```

## contract

```beat
id: contract
frames: 264
scene: contract
caption: Define a future task that permits reconnect, disconnect and unchanged.
narration: The proposed solver receives one MRA region, a proposed binary mask and a broad editable
  region. It returns a corrected mask on the same grid while preserving the outside. Exact defect
  coordinates, answer labels, reference graphs and ground-truth-shaped corridors stay out of the
  solver packet. Local attachment, geometry and collateral edits need separate checks.
visual: Explicit proposed input-to-output contract; do not invent a faulty mask or depict an executed
  correction.
channels:
  scan:
  - 1
  - 1
  reference:
  - 0
  - 0
  output:
  - 0
  - 0
cut: intentional-cut
```

## admission

```beat
id: admission
frames: 264
scene: admission
caption: Reveal the actual curation outcome and its admission gap.
narration: The output records are source candidates only. No natural faulty prediction was obtained,
  no defect fixture was admitted, and no model trial was run. Numeric verifier thresholds were not
  frozen. Admission still requires reproducible prediction provenance, native-image review, adjudication
  and oracle, unchanged and wrong-bridge controls. Later synthetic feasibility belongs to a separate
  study.
visual: Reveal the four retained candidate status records and zero trial/defect counts.
channels:
  scan:
  - 1
  - 1
  reference:
  - 0
  - 0
  output:
  - 0
  - 1
cut: intentional-cut
```

## limits

```beat
id: limits
frames: 240
scene: limits
caption: Preserve source provenance without claiming task difficulty.
narration: The audit verifies selected file sizes, hashes and retained ZIP checksums, source grids,
  label contacts and node alignment. Public-source exposure, annotation ambiguity and a natural
  prediction-error collection remain unresolved. TopCoW commercial use requires permission; the
  graph source declares noncommercial terms without a version. This local explanation neither promotes
  a task nor runs a medical trial.
visual: Show verified source checks, limits, terms and the still-open task-admission boundary.
channels:
  scan:
  - 1
  - 1
  reference:
  - 0
  - 0
  output:
  - 1
  - 1
cut: intentional-cut
```
