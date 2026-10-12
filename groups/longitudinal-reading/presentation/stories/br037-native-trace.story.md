---
schema: 2
id: br037-native-trace
title: Follow one longitudinal MRI inspection and its measurement definition
locale: en
purpose: Explain selected recorded native MRI operations, exact image deliveries
  and saved measurements, with a separate source-reference reveal.
scope: One retained BR-037 P03 neutral Terra/high attempt. Independent visit grids,
  component-box spans and mechanical success do not establish clinical accuracy.
recipe: native-trace-v1
manifest: groups/longitudinal-reading/presentation/native-mri-trace/native-trace.json
fps: 24
reference_policy: reader-reference-reveal
source_class: source-derived-teaching
source_locators:
- groups/longitudinal-reading/presentation/native-mri-trace/canonical-mapping.md
- groups/longitudinal-reading/presentation/native-mri-trace/README.md
- groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-mri.md
- groups/longitudinal-reading/presentation/sources/longitudinal-mri-audit.json
---

# Follow one longitudinal MRI inspection and its measurement definition

Canonical migration candidate, pending source-pinned visual review. Seven discrete 168-frame holds at
24 fps; 1,176 frames / 49 seconds. No invented continuous search, registration,
phase timing or point motion. All named findings are saved solver claims.

## 1. Receive both complete examinations

```beat
id: input
scene: input
frames: 168
caption: Two visits, 122 supplied volumes, two independent native frames.
narration: >-
  The solver received day-zero and day-thirty-four examinations: scouts, water and
  fat volumes, and eight dynamic grids per visit. Sixteen previews provide native
  context; the inventory retains all 122 volumes. Source targets and future outcomes
  were withheld. Visit positions are unregistered.
visual: Whole native grids with unmarked first-post posters. Each visit has its
  own affine and spacing; cross-examination positions are not registered.
state: input
trace_steps: [7, 9, 10, 11]
reference: false
```

## 2. Choose dynamic inspections

```beat
id: search
scene: search
frames: 168
caption: Early subtraction selects actual axial inspections.
narration: >-
  The solver inspected first-post minus baseline at four selected axial slices per
  visit, then baseline, late and peak-subtraction panels. These are recorded planes.
  Dynamic acquisition ordinals run zero through seven, but each separate three-
  dimensional file has citation phase zero.
visual: Exact step-15 delivery alongside its selected native k list and two grids.
  The coarse previews do not replace native-resolution delivered pixels.
state: dynamic
trace_steps: [13, 14, 15]
reference: false
```

## 3. Project and correct laterality

```beat
id: projection
scene: projection
frames: 168
caption: Preserve the delivered projection and its later correction.
narration: >-
  The solver projected early subtraction through a native slab. This delivered image
  has incorrect breast-side labels. Positive-R candidate locations and the
  subsequent code correction identify the right-breast focus. The corrected saved
  projection has separate provenance; no corrected projection delivery is recorded.
visual: Exact original step-18 PNG, explicit label-correction caveat, source slab
  bounds and native R/A/S orientation. Do not substitute the saved corrected file.
state: mip
trace_steps: [16, 17, 18, 19, 20]
reference: false
```

## 4. Inspect the selected focus

```beat
id: focus
scene: focus
frames: 168
caption: Phase panels retain each visit's actual inspection point.
narration: >-
  Recorded close-ups use separate native visit centres and ninety-one-by-ninety-one
  windows at ordinals zero, one, two, four and seven. Red crosses mark solver
  inspection points, not source truth. Saved citations differ by one voxel. Visit
  positions are unregistered; signal scales are uncalibrated.
visual: Exact step-22 phase panels, native focus windows and ordinal-to-series map.
  No inferred motion or registered correspondence connects the two centres.
state: focus
trace_steps: [20, 21, 22]
reference: false
```

## 5. Define a component span

```beat
id: measurement
scene: measurement
frames: 168
caption: The chosen threshold defines a component-box measurement.
narration: >-
  The saved method smooths early subtraction by one voxel, selects a connected
  component at thirty percent of local peak, and measures its largest voxel-edge
  bounding-box span. Saved values are 21.251 and 20.000 millimetres. These component
  spans are not adjudicated clinical diameters.
visual: Recorded local ROI bounds and saved inclusive extrema; convert maxima plus
  one to half-open bounds. Preserve rounded saved spans and reported values separately.
state: extent
trace_steps: [23, 24, 28, 29]
reference: false
```

## 6. Save the qualified account

```beat
id: output
scene: output
frames: 168
caption: Four citations support a qualified saved interpretation.
narration: >-
  The saved report claims persistent right-breast enhancement with minimal
  component-span decrease, while limiting diagnostic specificity and cross-visit
  signal comparisons. Its forecast is smaller, confidence 0.43, conditional on
  continued effective treatment. Format checks validate the contract, not the
  interpretation or forecast.
visual: Exact citations, reported 21.3 to 20.0 millimetres, report and conditional
  forecast. Step 29 printed the measurement summary before a git-not-found shell tail.
state: saved
trace_steps: [26, 27, 28, 29]
reference: false
```

## 7. Reveal source endpoints and limits

```beat
id: reference
scene: reference
frames: 168
caption: Source FTV, raw diameter and component span are different endpoints.
narration: >-
  The mechanical check passed while explicitly leaving clinical accuracy unscored.
  Earlier reproduction gives a 5.887666 percent component-span decrease. Source
  functional volume and raw diameter are different endpoints; diameter units remain
  unresolved. An always-smaller baseline also matches all three neutral future
  directions.
visual: Reader-only frozen contract, prior full-precision reproduction and source
  trajectories; saved state remains fixed. Source pCR and later visits were withheld
  from the solver. No score revision or clinical adjudication.
state: saved
trace_steps: [26, 29]
reference: true
```
