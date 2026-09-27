---
schema: 2
id: segmentation-calibration
title: 'Box-to-mask calibration: what the prompt already supplies'
locale: en
purpose: Explain a retained direct SAM2 and LiteMedSAM calibration through source-derived
  prompt boxes, saved masks, scoring controls, cached inference timing and backend
  counterexamples.
scope: One public CT; fixed reference-derived slices and boxes; direct tools, no general
  agent; original saved masks and scores.
recipe: segmentation-calibration-v1
asset_pack: retained-segmentation-calibration-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-segmentation-calibration.md
- groups/anatomy-audit/presentation/sources/segmentation-calibration-audit.json
- groups/anatomy-audit/experiments/sam-litemedsam-slice-calibration/protocol.md
- groups/anatomy-audit/experiments/sam-litemedsam-slice-calibration/bench.py
- groups/anatomy-audit/findings/sam-litemedsam-slice-calibration.md
- groups/anatomy-audit/findings/evidence/sam-litemedsam-slice-calibration.json
- scripts/audit_segmentation_calibration_evidence.py
- scripts/build_segmentation_calibration_assets.py
---

# Retained box-to-mask calibration

## A full CT slice, a supplied location

```beat
id: inputs
scene: inputs
frames: 192
caption: A full CT slice, a supplied location
narration: This retained calibration compares SAM two point one Small with LiteMedSAM
  on one known public CT. Each model receives a complete native axial image and a
  supplied box. The displayed scan has no output or reference overlay. Localization
  is already supplied by the protocol; this is not an autonomous organ-finding task.
visual: Full native unannotated liver q50 slice, source grid and CT window, no predictions
  or dense reference.
channels:
  view:
  - 0
  - 0
  condition:
  - 0
  - 0
  box:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## Reference masks select the three fixed slices

```beat
id: sampling
scene: sampling
frames: 288
caption: Reference masks select the three fixed slices
narration: For each of six organs, the author selects the twenty-fifth, fiftieth and
  seventy-fifth percentiles of the nonempty slice-index list. These three pancreas
  views are discrete source slices, not an interpolated volume. Dense reference is
  now shown to explain this author operation. Eighteen correlated organ and slice
  pairs still come from just one patient.
visual: Three discrete full-field pancreas slices with author reference reveal, alongside
  all six organs and fixed native k indices.
channels:
  view:
  - 0
  - 1
  condition:
  - 0
  - 0
  box:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Expand the same reference rectangle by 3 or 15 mm

```beat
id: boxes
scene: boxes
frames: 288
caption: Expand the same reference rectangle by 3 or 15 mm
narration: Tight boxes add two pixels, or three millimetres, on each side of the reference
  bounding rectangle. Loose boxes add ten pixels, or fifteen millimetres. Coordinates
  remain in the native image and are clipped at its boundary. Both models get exactly
  the same box and full slice. The dense mask and the organ name are not model inputs.
visual: Actual pancreas q50 native tight and loose boxes side by side with reference
  contours and exact half-open xyxy coordinates.
channels:
  view:
  - 0
  - 0
  condition:
  - 0
  - 0
  box:
  - 1
  - 1
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Shared native prompt; different internal preprocessing

```beat
id: preprocess
scene: preprocess
frames: 288
caption: Shared native prompt; different internal preprocessing
narration: The supplied image and native box are identical, but the internal transforms
  differ. SAM two resizes to a thousand twenty-four squared and scales box coordinates
  in floating point. LiteMedSAM resizes to two hundred fifty-six squared and truncates
  scaled box coordinates to integers. Each image is encoded once; two cached box decodes
  return native-size masks. The benchmark adds no component cleanup.
visual: Source-derived tight/loose coordinate transforms switch discretely; explicit
  image-encode, cached-decode and native-mask steps.
channels:
  view:
  - 0
  - 0
  condition:
  - 0
  - 1
  box:
  - 1
  - 1
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect the saved masks before reference agreement

```beat
id: outputs
scene: outputs
frames: 240
caption: Inspect the saved masks before reference agreement
narration: Cyan is the original SAM two MPS mask and orange is LiteMedSAM on the same
  pancreas slice with the loose box. These masks are saved outputs, not newly generated
  predictions. The full supplied image appears beside the reader detail crops. Crops
  enclose every saved mask so that false-positive extent is not clipped. Reference
  and accuracy measurements remain hidden.
visual: Paired unchanged MPS loose-box pancreas masks plus full source context; no
  reference contours or agreement numbers.
channels:
  view:
  - 0
  - 0
  condition:
  - 1
  - 1
  box:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal agreement after the supplied localization

```beat
id: reference
scene: reference
frames: 288
caption: Reveal agreement after the supplied localization
narration: The dashed green reference now appears on the same native pixels. LiteMedSAM
  follows this selected pancreas reference more closely, while SAM two includes adjacent
  tissue. Dice measures overlap and HD ninety-five summarizes the tail of boundary
  distances. This is a prespecified middle-slice example; the overall comparison must
  include all eighteen samples.
visual: Same saved pancreas masks; dense reference and per-slice Dice/HD95 appear
  only after the explicit reveal.
channels:
  view:
  - 0
  - 0
  condition:
  - 1
  - 1
  box:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Keep the per-organ counterexamples visible

```beat
id: sensitivity
scene: sensitivity
frames: 576
caption: Keep the per-organ counterexamples visible
narration: Step through all six prespecified middle slices with loose boxes. The paired
  table uses all three fixed slices for that organ, under both box conditions.
  LiteMedSAM has higher overall mean agreement, but widening a box does not help every
  organ. Its gallbladder mean declines. The duodenum tight-box mean favors SAM two.
  Averages do not establish a universal winner.
visual: Six discrete q50 organ views, complete-mask crops and paired three-slice tight/loose
  mean Dice tables; original masks unchanged.
channels:
  view:
  - 0
  - 1
  condition:
  - 1
  - 1
  box:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Separated reference regions challenge the enclosing box

```beat
id: duodenum
scene: duodenum
frames: 336
caption: Separated reference regions challenge the enclosing box
narration: The middle duodenum slice contains separate reference regions. Switching
  from the tight to the loose prompt shows both wider-box masks including intervening
  or adjacent tissue. The means favor different tools under different box conditions.
  Separate component prompts or more slice context are possible follow-up hypotheses,
  but no correction or revised prompt was tested here.
visual: Discrete tight-to-loose comparison of both tools on fixed native duodenum
  k177, matching reference and prompt legends.
channels:
  view:
  - 0
  - 0
  condition:
  - 0
  - 1
  box:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Measure what the supplied rectangle already buys

```beat
id: controls
scene: controls
frames: 288
caption: Measure what the supplied rectangle already buys
narration: A filled prompt rectangle uses no learned segmenter. Across the eighteen
  samples it reaches mean Dice point five-two-six for tight boxes and point three-zero-nine
  for loose boxes. The displayed pancreas is one illustration; those means cover every
  sample. Exact-reference and empty masks give Dice one and zero. These controls keep
  the localization advantage explicit.
visual: Filled actual native rectangles with separate reference contours, all-sample
  control means and exact/empty endpoints.
channels:
  view:
  - 0
  - 0
  condition:
  - 0
  - 0
  box:
  - 1
  - 1
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Improved overlap need not reduce boundary error

```beat
id: metrics
scene: metrics
frames: 288
caption: Improved overlap need not reduce boundary error
narration: LiteMedSAM mean Dice rises with the wider box, while its mean HD ninety-five
  also rises, from six-point-four to seven-point-two-one millimetres. Better overlap
  does not guarantee a better tail boundary distance. The scorer pools both directions
  of two-dimensional surface distances before taking the ninety-fifth percentile.
  All original scores reproduce exactly from the saved masks.
visual: Exact original tight/loose mean Dice and HD95 tables, shared denominator18
  and explicit concatenated-direction 2D metric.
channels:
  view:
  - 0
  - 0
  condition:
  - 0
  - 0
  box:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Separate image encoding from cached box decoding

```beat
id: latency
scene: latency
frames: 336
caption: Separate image encoding from cached box decoding
narration: On this Apple M five Pro, LiteMedSAM encodes images in a median forty-two-point-five
  milliseconds, versus SAM two at a hundred thirty-four-point-five. Each complete
  run has eighteen unique encodes and thirty-six cached box decodes. Synchronization
  and CPU mask return are included. Disk input, model load and warmup are excluded.
  First measured SAM two encoding takes seven hundred eighty-six milliseconds. These
  medians do not estimate startup or sustained throughput.
visual: Retained encode/decode table with distinct denominators, first-encode outlier,
  setup and non-additive memory counters.
channels:
  view:
  - 0
  - 0
  condition:
  - 0
  - 0
  box:
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

## Backend agreement is a separate measurement

```beat
id: backend
scene: backend
frames: 480
caption: Backend agreement is a separate measurement
narration: 'The prespecified loose adrenal check exposes a SAM two CPU versus MPS
  discrepancy. A later full CPU diagnostic preserves those results. The second view
  is the worst pair, loose liver q25, selected after results: backend mask Dice is
  only point zero-five-four. Across thirty-six pairs the median is point nine-five-five.
  Four planned LiteMedSAM CPU/MPS masks match exactly. The numerical cause and general
  parity remain unresolved.'
visual: 'Two discrete exact SAM2 CPU/MPS pairs: planned adrenal q50 and post-result-selected
  liver q25 extreme; distinguish backend Dice from per-mask GT scores.'
channels:
  view:
  - 0
  - 1
  condition:
  - 1
  - 1
  box:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Retained tool calibration; untested agent capabilities

```beat
id: limits
scene: limits
frames: 288
caption: Retained tool calibration; untested agent capabilities
narration: The record contains seventy-two primary MPS predictions, eight planned
  CPU checks and thirty-six later SAM two CPU diagnostic predictions. One known public
  case and reference-derived localization do not test autonomous discovery, semantic
  naming, correction or three-dimensional propagation. Training overlap and clinical
  annotation intent remain unresolved. This explanation preserves original masks and
  scores and launches no new inference.
visual: Supported local measurements and untested claims, with 72+8+36 denominator
  accounting and source/reference limits.
channels:
  view:
  - 0
  - 0
  condition:
  - 0
  - 0
  box:
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
