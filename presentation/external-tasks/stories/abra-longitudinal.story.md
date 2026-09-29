---
schema: 2
id: abra-longitudinal
title: Compare two chest CT studies over time
locale: en
purpose: Show how ABRA's four longitudinal tasks use metadata or independent CT browsing, then separate blank agent output from reader-only source references.
scope: Exact NLST pair, 16 native samples per visit; no ABRA answer, registration or verified viewer-to-DICOM reference mapping.
recipe: abra-longitudinal-v1
asset_pack: retained-abra-longitudinal-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/abra-longitudinal.md
- presentation/external-tasks/sources/abra-longitudinal-resolution.json
- scripts/build_abra_longitudinal_assets.py
---

# Two source studies, four ABRA contracts

## Open the exact native inputs

```beat
id: inputs
scene: inputs
frames: 216
caption: Two real NLST CT visits; no saved ABRA answer
narration: 'ABRA supplies paired study identifiers and viewer tools. These grayscale images are actual selected NLST CT slices from the two complete retained series. Sixteen slices per visit were sampled for display. The visits are not registered, and no ABRA answer or lesion change is shown.'
visual: Two labeled source CT inputs with independent study dates, kernel, original InstanceNumber and LPS z; acquisition link and evidence warning above the images.
channels:
  baseline: [0.18, 0.18]
  followup: [0.72, 0.72]
  task: [0, 0]
  reference: [0, 0]
```

## Read the dates

```beat
id: metadata
scene: metadata
frames: 216
caption: Query two dates, then submit an integer interval
narration: 'The interval condition asks for the absolute number of calendar days between two StudyDate fields. Both dates are source metadata available to the solver. The expected integer remains reader-only while the operation is explained.'
visual: Two source StudyDate cards flow to an empty integer-days output socket; no expected answer appears.
channels:
  baseline: [0.18, 0.18]
  followup: [0.72, 0.72]
  task: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Count the native CT images

```beat
id: counts
scene: counts
frames: 216
caption: Follow-up minus baseline is signed
narration: 'The slice-count condition queries each CT series and subtracts the baseline count from the follow-up count. These are complete native instance counts, not the sixteen teaching samples. The output is one signed integer; reversing the order changes the answer.'
visual: Native 161 and 162 CT instance counts enter a labeled follow-up-minus-baseline operation with a blank answer socket.
channels:
  baseline: [0.18, 0.18]
  followup: [0.72, 0.72]
  task: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Browse each examination on its own terms

```beat
id: browse
scene: browse
frames: 288
caption: Two independent native stack navigators
narration: 'For the lesion conditions, the agent must inspect both studies. Each rail here moves through real DICOM samples by original InstanceNumber in its own visit. Equal rail positions or equal numeric LPS z do not match anatomy: a saved equal-z pair showed mid-lung on one visit and near-apical anatomy on the other.'
visual: Real baseline and follow-up CT slices change at different rates, with separate 16-sample rails, native instance numbers and z labels; no connecting correspondence line or private marker.
channels:
  baseline: [0.18, 0.87]
  followup: [0.72, 0.31]
  task: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Specify the finding without inventing one

```beat
id: submit
scene: submit
frames: 264
caption: A lesion finding needs a follow-up viewer index and pixels
narration: 'ABRA asks for a new-lesion finding on the follow-up series: a zero-based viewer slice index and pixel x and y. The multiple-lesion variant submits each finding, then a completion call. The fields stay blank because no agent answer was retained; the viewer index to native SOP mapping is not verified here.'
visual: Empty source-defined submission fields, then the multiple-finding completion field; no patient point, submitted answer or score.
channels:
  baseline: [0.87, 0.87]
  followup: [0.31, 0.31]
  task: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Reveal source references separately

```beat
id: reference
scene: reference
frames: 264
caption: Reader-only arithmetic and an unbound pixel point
narration: 'After an explicit reader reveal, the pinned source expected outcomes appear. The date and count values are metadata arithmetic. The private lesion point names a zero-based viewer index, but no source check maps that index to a DICOM SOP. It is therefore drawn only on an abstract pixel grid, never on a CT image.'
visual: Covered reference opens to the arithmetic values and an abstract 512-by-512 pixel grid with a source point; no patient-image overlay.
channels:
  baseline: [0.87, 0.87]
  followup: [0.31, 0.31]
  task: [1, 1]
  reference: [0, 1]
cut: intentional-cut
```

## Mark the evidence limits

```beat
id: limits
scene: limits
frames: 216
caption: Real input does not establish a new lesion or model result
narration: 'Both complete CT studies and the ABRA task contract are retained. There is no saved agent submission or score. The studies are unregistered, the viewer index to SOP mapping remains open, and the source point is a benchmark reference rather than independent clinical adjudication of newness.'
visual: Recovered source, unresolved correspondence and missing output cards; official acquisition route remains visible.
channels:
  baseline: [0.87, 0.87]
  followup: [0.31, 0.31]
  task: [1, 1]
  reference: [0, 0]
cut: intentional-cut
```
