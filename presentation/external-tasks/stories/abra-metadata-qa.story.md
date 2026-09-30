---
schema: 2
id: abra-metadata-qa
title: Answer questions about ABRA study metadata
locale: en
purpose: "Select the metadata level and format one terminal answer string."
scope: "Mixed source-manifest teaching and illustrative formatting; generated task and live response absent."
recipe: abra-metadata-qa-v1
asset_pack: retained-abra-metadata-qa-contract-v2
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/abra-metadata-qa.md
- presentation/external-tasks/sources/abra-metadata-qa-resolution.json
- scripts/build_abra_metadata_refined_assets.py
---

# Task/live response absent · github.com/Luab/ABRA

```beat
id: input
scene: input
frames: 144
caption: "Task/live response absent · github.com/Luab/ABRA"
narration: "The original generated task and live metadata response are absent. Obtain them through official ABRA setup. This source-manifest teaching example records one study, twenty-seven series and one hundred sixty-six instances."
visual: "Source-manifest teaching record; canonical family selection and explicit reference boundary. Linked warning remains visible."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# CT instance count: 140

```beat
id: ct-count
scene: operation
frames: 144
caption: "CT instance count: 140"
narration: "Read one hundred forty instances in the first CT series. Do not include twenty-six SEG and SR instances or count only the three tool samples."
visual: "Source-manifest teaching record; canonical family selection and explicit reference boundary. Linked warning remains visible."
channels:
  progress: [0.0, 0.0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# All-series count: 27

```beat
id: series-count
scene: operation
frames: 144
caption: "All-series count: 27"
narration: "Count one CT, thirteen SEG and thirteen SR series. The twenty-seven-series denominator is different from the one hundred sixty-six total-instance denominator."
visual: "Source-manifest teaching record; canonical family selection and explicit reference boundary. Linked warning remains visible."
channels:
  progress: [0.25, 0.25]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Distinct tags → sorted list

```beat
id: modalities
scene: operation
frames: 144
caption: "Distinct tags → sorted list"
narration: "Deduplicate the twenty-seven source modality tags, alphabetically sort CT, SEG and SR, and join with comma plus space. This is legitimate metadata derivation, not a private answer."
visual: "Source-manifest teaching record; canonical family selection and explicit reference boundary. Linked warning remains visible."
channels:
  progress: [0.5, 0.5]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# StudyDate → YYYYMMDD

```beat
id: study-date
scene: operation
frames: 144
caption: "StudyDate → YYYYMMDD"
narration: "Read the source StudyDate and keep eight digits. No acquisition date is inferred from filenames or ZIP order."
visual: "Source-manifest teaching record; canonical family selection and explicit reference boundary. Linked warning remains visible."
channels:
  progress: [0.75, 0.75]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# First CT series → exact UID

```beat
id: ct-uid
scene: operation
frames: 144
caption: "First CT series → exact UID"
narration: "Read the first CT SeriesInstanceUID in source enumeration. Do not substitute the StudyInstanceUID or sort UIDs."
visual: "Source-manifest teaching record; canonical family selection and explicit reference boundary. Linked warning remains visible."
channels:
  progress: [1.0, 1.0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# One answer string · participant field empty

```beat
id: output
scene: output
frames: 144
caption: "One answer string · participant field empty"
narration: "The participant submission is absent. The contract requires one integer, eight-digit date, sorted comma-space list or exact UID string."
visual: "Source-manifest teaching record; canonical family selection and explicit reference boundary. Linked warning remains visible."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Illustrative comparison · no case reference

```beat
id: reference
scene: reference
frames: 144
caption: "Illustrative comparison · no case reference"
narration: "The generated expected answer is absent. Reader reveal shows only authored formatting controls; sorted and unsorted strings illustrate the source rule, not a patient or model result."
visual: "Source-manifest teaching record; canonical family selection and explicit reference boundary. Linked warning remains visible."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# Source counts do not establish an observed task

```beat
id: limits
scene: limits
frames: 144
caption: "Source counts do not establish an observed task"
narration: "The local archive corroborates one hundred forty CT DICOMs. SEG and SR remain manifest records. No tool response, participant answer, score or fresh trial exists."
visual: "Source-manifest teaching record; canonical family selection and explicit reference boundary. Linked warning remains visible."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
