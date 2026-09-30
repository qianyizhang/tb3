---
schema: 2
id: abra-birads
title: "Structure an ABRA breast MRI report"
locale: en
purpose: "Explain image-reading versus answer-bearing oracle assistance and a report schema without a patient finding."
scope: "Source series metadata; matched MRI, generated report and answer absent. General code rules require reader reveal."
recipe: abra-birads-v1
asset_pack: retained-abra-birads-contract-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/abra-birads.md
- presentation/external-tasks/sources/abra-birads-resolution.json
- scripts/build_abra_birads_assets.py
---

# Inspect source metadata

```beat
id: input
scene: input
frames: 288
caption: "MRI absent · cancerimagingarchive.net/collection/duke-breast-cancer-mri/"
narration: "Public ABRA metadata identifies six MR series and one SEG series for Breast_MRI_008. No matching patient MRI pixels or verified generated task is retained here. The series list preserves manifest order, which is not contrast-phase acquisition order. Obtain matching images and clinical data through the linked official TCIA collection."
visual: "Unordered source series list and labeled empty MRI sockets; no invented patient image."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Contrast the assistance conditions

```beat
id: operation
scene: operation
frames: 336
caption: "Inspect images or relay oracle fields"
narration: "Visual assessment enables vision, uses the breast MRI display preprocessor and allows twenty turns. The oracle condition disables vision and allows ten turns. Its query checks the series UID and returns prepared task fields, rather than running a CAD model. Select a condition to inspect what is supplied and what work remains. No viewer or oracle call occurs here."
visual: "Condition selector with source-defined tool paths, empty image or oracle-response socket."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Inspect the unsubmitted report

```beat
id: output
scene: output
frames: 264
caption: "Required fields remain unset"
narration: "The terminal report call requires laterality, lesion count, category and enhancement status. Optional quadrant belongs inside the first finding's location_quadrant field. No patient value, oracle response, submission or score is shown."
visual: "Four null-value schema sockets and optional nested quadrant path; no completed checkmarks."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Reveal general construction policy

```beat
id: reference
scene: reference
frames: 336
caption: "Reveal code rules, not a patient reference"
narration: "This reveal shows general ABRA target construction only. The clinical script assigns category five and enhancement true by code, and maps multifocality to count two or one. These are not independently recorded MRI findings. Laterality and quadrant are derived from clinical fields; DCE UID selection uses keyword priority with an any-MR fallback. No patient target JSON is available."
visual: "Covered derivation, followed by explicit reveal of labeled general code rules; no patient answer."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 1]
cut: intentional-cut
```

# Inspect weighted agreement and settle

```beat
id: limits
scene: limits
frames: 288
caption: "Agreement with constructed fields"
narration: "Weights are point two five for side, point three for category, point two for count and point one five for enhancement. A reference quadrant adds point one, changing the total from point nine to one. Category and count have partial-credit branches. No weighted result or independent diagnostic accuracy is measured. The report remains unsubmitted."
visual: "Scorer field weights and optional-quadrant denominator selector beside unset report output."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
