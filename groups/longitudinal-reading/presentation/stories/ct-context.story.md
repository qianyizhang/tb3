---
schema: 2
id: ct-context
title: What context can these CTs support?
locale: en
purpose: Connect native CT evidence to bounded context claims, justified unknowns
  and a separate source comparison.
scope: One retained Astra-medium CT-only context assessment; native source crops and
  saved-output diagnostics; no new model execution.
recipe: ct-context-v1
asset_pack: retained-ct-context-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/longitudinal-reading/presentation/briefs/tb3-ct-context-inference.md
- groups/longitudinal-reading/findings/longitudinal-ct-context-hypothesis.md
- groups/longitudinal-reading/presentation/sources/ct-context-audit.json
- groups/longitudinal-reading/methods/longitudinal-ct-context-v1/inference-instruction.md
- groups/longitudinal-reading/methods/longitudinal-ct-context-v1/protocol.md
- scripts/audit_ct_context.py
- scripts/build_ct_context_assets.py
---

# Canonical CT context explanation

## Two CT volumes, no clinical record

```beat
id: inputs
scene: inputs
frames: 288
caption: Two CT volumes, no clinical record
narration: The agent receives earlier and later full CT volumes and headers for one
  patient. These reader crops use the axial planes cited later in its answer. No diagnosis,
  demographic record, dates, points, masks or earlier output are supplied. The task
  is context assessment, not segmentation or treatment advice.
visual: Native CT pair shown without output markers. Selected crops are labeled; no
  reference facts.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## Geometry does not encode clinical history

```beat
id: headers
scene: headers
frames: 336
caption: Geometry does not encode clinical history
narration: The headers describe array dimensions, spacing and spatial coordinates.
  Descriptive fields are empty and there are no extensions. Acquisition dates, age
  and recorded sex are absent. Affine origins are spatial millimeters, not elapsed
  time. The two volumes are not registered, and file modification time cannot supply
  scan dates.
visual: Compare actual dimensions and header fields, then separate geometry from history.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## From appearance to a qualified inference

```beat
id: liver
scene: liver
frames: 384
caption: From appearance to a qualified inference
narration: Amber crosses locate the agent’s approximate liver evidence points. Its
  report describes low-attenuation abnormalities and greater later burden, then infers
  suspected metastatic malignancy with confidence 0.91. Specific primary diagnosis
  stays unknown. Melanoma is one compatible alternative; it is not identified histology.
  These coordinates are evidence citations, not segmentation boundaries or supplied
  hints.
visual: Native liver crops with submitted points; observed appearance leads to bounded
  inference.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## A scar-like appearance is not an operative record

```beat
id: surgery
scene: surgery
frames: 336
caption: A scar-like appearance is not an operative record
narration: Dashed amber boxes show the groin regions cited by the agent. It suggests
  probable prior local intervention with confidence 0.76. Procedure, indication and
  timing remain unestablished. Nonsurgical scarring, inflammation or lymphatic obstruction
  remain alternatives. No individual operative record is available to adjudicate this
  suggestion.
visual: Native groin pair with agent-cited regions and unresolved alternatives.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Give every field an evidence status

```beat
id: fields
scene: fields
frames: 1080
caption: Give every field an evidence status
narration: 'The retained answer contains two inferred fields and seven unknowns. Read
  each selected field with its reason: broad diagnosis is an inference; exact primary,
  age, recorded sex, interval, both ordering indications and systemic treatment remain
  unknown. Possible prior intervention is qualified. Each record has status, value,
  confidence, basis and alternatives. Unknown requires a null value. The reported
  confidence describes the assessment, including confidence that information is unavailable;
  it is not measured calibration. The companion report cites native coordinates and
  explains what missing records would resolve the unknowns.'
visual: Select all nine exact output fields in order, five seconds each; preserve
  confidence and unknown reasons.
channels:
  view:
  - 0
  - 1
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Compare with the correct source level

```beat
id: reference
scene: reference
frames: 384
caption: Compare with the correct source level
narration: The reader reveal separates patient CSV facts from cohort descriptions.
  Age 44, recorded sex female and interval 121 days are patient metadata. Melanoma,
  systemic therapy and staging or response assessment are cohort context, not individual
  clinical reports. Surgical history is unavailable. Agreement does not prove image-only
  identifiability. Seven unknowns and two inferences are not a two-out-of-nine accuracy
  score.
visual: Begin with metadata hidden, then reveal patient, cohort and unavailable columns
  at the midpoint.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Schema validity is not a scientific score

```beat
id: validator
scene: validator
frames: 360
caption: Schema validity is not a scientific score
narration: The saved validator reproduces the original result exactly. Author-created
  all-unknown output passes, as do unsupported invented assertions. An inconsistent
  unknown value and a missing report fail. The validator deliberately checks structure
  and returns no scientific score. These temporary saved-output diagnostics are not
  fresh model attempts; all original rewards remain unchanged.
visual: Show exact replay and four author schema diagnostics, clearly distinct from
  model runs.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Preserve useful inference and justified unknowns

```beat
id: limits
scene: limits
frames: 240
caption: Preserve useful inference and justified unknowns
narration: One retained Astra-medium session finished in three minutes twenty-seven
  seconds. Fourteen image observation blocks include montages, not fourteen native
  slices. This example supports a bounded explanation of evidence and abstention.
  It cannot establish diagnostic accuracy, exhaustive review, clinical adjudication
  or population confidence calibration.
visual: End with retained result, supported operation and unresolved limits.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```
