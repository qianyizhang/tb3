---
schema: 2
id: longitudinal-links
title: Match identity before describing change
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: Abstract candidate objects, not patient lesions. Candidates are supplied in this teaching fixture; the comprehensive candidate task also supplies no locations and still requires detection.
recipe: longitudinal-v1
asset_pack: longitudinal-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-ct-candidates.md
---

# Match identity before describing change

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. visits

```beat
id: visits
frames: 120
caption: Two visits contain different observations.
narration: Do not assume that row order, position or size establishes identity.
visual: Show candidates with visit-local IDs; keep colors neutral before matching.
channels:
  visits:
  - 0.0
  - 1.0
  links:
  - 0.0
  - 0.0
  coverage:
  - 0.0
  - 0.0
```

## 2. matches

```beat
id: matches
frames: 168
caption: Link the same object even when its size changes.
narration: A0 links to A1 despite a changed radius. Identity and size are different fields.
visual: Draw the two declared links and update the table from the same link records.
channels:
  visits:
  - 1.0
  - 1.0
  links:
  - 0.0
  - 1.0
  coverage:
  - 0.0
  - 0.0
```

## 3. coverage

```beat
id: coverage
frames: 168
caption: Not observed is not automatically disappeared.
narration: C0 falls outside the follow-up field of view. The correct teaching state is unknown outside coverage.
visual: Show the coverage crop; mark the unmatched C0 without a false disappearance arrow.
channels:
  visits:
  - 1.0
  - 1.0
  links:
  - 1.0
  - 1.0
  coverage:
  - 0.0
  - 1.0
```

## 4. new

```beat
id: new
frames: 120
caption: A new observation needs a separate relation.
narration: D1 is new within the observed field in this constructed example.
visual: Show a null-source relation; no nearest-neighbor forced match.
channels:
  visits:
  - 1.0
  - 1.0
  links:
  - 1.0
  - 1.0
  coverage:
  - 1.0
  - 1.0
```

## 5. boundary

```beat
id: boundary
frames: 96
caption: Do not turn this into a response measurement.
narration: No patient finding, clinical threshold or therapy response is demonstrated.
visual: Hold all relations and the scope.
channels:
  visits:
  - 1.0
  - 1.0
  links:
  - 1.0
  - 1.0
  coverage:
  - 1.0
  - 1.0
```
