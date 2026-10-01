---
schema: 2
id: imaging101-xray-tooth-gridrec
title: Trace tooth counts without inventing a reconstructed cross-section
locale: en
purpose: "Explain native counts, flat/dark correction, centre geometry and reconstruction-reference boundaries."
scope: "Experimental count rows only; calibrated attenuation, truth and participant output absent."
recipe: imaging101-xray-tooth-gridrec-v1
asset_pack: retained-imaging101-xray-tooth-gridrec-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-xray-tooth-gridrec.md
- presentation/external-tasks/sources/imaging101-xray-tooth-gridrec-resolution.json
- scripts/build_imaging_tooth_gridrec_assets.py
---
# native-tooth-detector-counts

```beat
id: native-tooth-detector-counts
scene: input
frames: 168
caption: "Tooth counts; calibration / output gaps · Official Imaging101 acquisition"
narration: "Native experimental tooth counts retained; physical attenuation calibration, independent truth and participant output absent."
visual: "Native count rows and calibration profiles; authored correction rules; reference scope late, actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# flat-dark-transmission-rule

```beat
id: flat-dark-transmission-rule
scene: operation
frames: 168
caption: "Keep raw counts, correction and line integrals distinct"
narration: "Flat and dark frames correct transmission; source denominator fallback and one-sided log clipping remain explicit."
visual: "Native count rows and calibration profiles; authored correction rules; reference scope late, actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# native-row-and-calibration-views

```beat
id: native-row-and-calibration-views
scene: operation
frames: 168
caption: "Inspect both native detector rows and calibration frames"
narration: "Raw projection count pixels and first flat/dark frame profiles retain native cells; no correction or inverse performed."
visual: "Native count rows and calibration profiles; authored correction rules; reference scope late, actual output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# source-center-and-fbp-conventions

```beat
id: source-center-and-fbp-conventions
scene: operation
frames: 168
caption: "Distinguish source FBP from the gridrec baseline"
narration: "Centre correlation and variance-based search, ramp filtering and circular masking are pinned rules, not executed reconstruction."
visual: "Native count rows and calibration profiles; authored correction rules; reference scope late, actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# unsubmitted-two-slice-volume

```beat
id: unsubmitted-two-slice-volume
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Native count rows and calibration profiles; authored correction rules; reference scope late, actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# late-baseline-reference-scope

```beat
id: late-baseline-reference-scope
scene: reference
frames: 168
caption: "Reveal equal references but different metric scopes"
narration: "Saved reconstruction equals solver-visible baseline; source first-slice denominator differs from generic two-slice scope."
visual: "Native count rows and calibration profiles; authored correction rules; reference scope late, actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# unresolved-calibration-and-truth

```beat
id: unresolved-calibration-and-truth
scene: limits
frames: 168
caption: "Resolve spacing, calibration, runtime and independent truth"
narration: "No new reconstruction, physical attenuation calibration, independent truth, clinical anatomy or metric."
visual: "Native count rows and calibration profiles; authored correction rules; reference scope late, actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
