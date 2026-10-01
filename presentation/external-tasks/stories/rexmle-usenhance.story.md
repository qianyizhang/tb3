---
schema: 2
id: rexmle-usenhance
title: "Pair ultrasound helpers without inventing enhancement"
locale: en
purpose: "Explain missing native pairs, source partition rules and an unsubmitted enhancement artifact."
scope: "Symbolic source protocol only; native pair/split/patient correspondence absent; no clinical result."
recipe: rex-usenhance-v1
asset_pack: symbolic-rex-usenhance-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-usenhance.md
- presentation/external-tasks/sources/rexmle-usenhance-resolution.json
- scripts/build_rex_usenhance_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Paired PNGs absent \u00b7 ultrasoundenhance2023.grand-challenge.org"
narration: "The exact native low/high pairs and prepared split are absent. Empty sockets illustrate source roles, not ultrasound anatomy, enhanced pixels, patient correspondence or a model result."
visual: "Symbolic paired-image sockets and source rule records; no image reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 288
caption: "Public train highs differ from private test highs"
narration: "Source preparation matches same-name PNGs within each organ, prefixes organ IDs and splits image IDs 80/20 at seed 42. Patient isolation, pair registration and exact split membership are unverified. Public training highs would be helpers; private test highs remain outside teaching."
visual: "Symbolic paired-image sockets and source rule records; no image reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 288
caption: "Follow pairing, training, inference and submission stages"
narration: "Canonical steps show source preparation and required workflow, with no preparer, model or inference executed. Declared patient/pair counts do not establish recovered samples or patient-level splitting."
visual: "Symbolic paired-image sockets and source rule records; no image reconstruction."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 288
caption: "CSV rows and enhanced PNGs remain unsubmitted"
narration: "Submit image_id and enhanced_image_path, plus each enhanced image. Source grade compares against private high geometry and may resize predictions; no native dimensions or clinical structure preservation have been verified."
visual: "Symbolic paired-image sockets and source rule records; no image reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 288
caption: "Reveal grading mechanics without a private image"
narration: "LNCC uses per-image normalization and valid local variance; SSIM and PSNR use joint range. Mean metrics are image-row units, while leaderboard ranks are submission units. Lower-better mean rank and fallback differ the prose composite. No metric, clinical accuracy or outcome is measured."
visual: "Symbolic paired-image sockets and source rule records; no image reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
