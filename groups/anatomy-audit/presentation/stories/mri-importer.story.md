---
schema: 2
id: mri-importer
title: Keep every MRI sample attached to its coordinates
locale: en
purpose: Explain actual frame association, logical versus actual labels, LPS geometry and the
  retained successful importer repair.
scope: Original synthetic metadata profile; one retained Terra/high attempt; 12 private acquisitions,
  three encodings each.
recipe: mri-importer-v1
asset_pack: retained-mri-importer-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-mri-importer.md
- groups/anatomy-audit/findings/mri-importer-calibration.md
- groups/anatomy-audit/presentation/sources/mri-importer-audit.json
- probes/mr-frame-association/instruction.md
- probes/mr-frame-association/authoring/notes.md
- docs/evidence/mr-pilot-freeze.json
- docs/evidence/mr-trial-summary.json
- scripts/audit_mri_importer_evidence.py
- scripts/build_mri_importer_assets.py
---

# Canonical MRI frame association

## Pixels travel with their metadata

```beat
id: inputs
scene: inputs
frames: 240
caption: Pixels travel with their metadata
narration: The shuffled public input contains twelve signed sample tiles, each paired with its
  own metadata. These exact synthetic numbers are not patient MRI. Frame order may change without
  changing the acquisition.
visual: All twelve actual shuffled public sample tiles, indexed by storage position.
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

## Logical ordinals differ from actual values

```beat
id: ordinals
scene: ordinals
frames: 336
caption: Logical ordinals differ from actual values
narration: Dimension descriptors define what each ordinal refers to. The task requires actual
  time and echo values in ascending order. A descriptor permutation must not permute the meaning
  of the output axes.
visual: Actual descriptor order and ordinal-to-value maps for the shuffled public example.
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

## Route intact tiles to canonical slots

```beat
id: association
scene: association
frames: 576
caption: Route intact tiles to canonical slots
narration: Each original frame moves conceptually to its time, echo and physical-slice slot. The
  highlighted traversal covers every frame once. Pixel samples remain unchanged. This is a teaching
  traversal of data, not an animated solver history.
visual: Storage and canonical grids with paired highlights for all twelve frame destinations.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Preserve the physical point of every sample

```beat
id: geometry
scene: geometry
frames: 384
caption: Preserve the physical point of every sample
narration: The affine maps column, row and slice indices into LPS millimetres. Row and column
  spacings differ in this oblique public fixture. Inspect all eight pixel-centre corners, including
  the far corner, using the original full-precision affine.
visual: Projected oblique pixel-centre corner diagram, affine and actual coordinate arithmetic.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Read geometry from either permitted location

```beat
id: placement
scene: placement
frames: 288
caption: Read geometry from either permitted location
narration: Orientation and pixel measures may be shared or repeated per frame. The saved repair
  supports both. Relocating the public geometry preserves samples and labels; tiny affine roundoff
  remains far below the specified physical tolerance.
visual: Shared/per-frame macro locations and replayed numerical relocation check.
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

## Return samples, labels and the LPS affine together

```beat
id: outputs
scene: outputs
frames: 288
caption: Return samples, labels and the LPS affine together
narration: Replay of the saved code returns the exact public samples, actual time and echo labels,
  and affine. Singleton axes stay present. The public expected outputs were supplied to the original
  solver; replay is not a new model run.
visual: Replayed public output shape, labels and an exact numerical sample tile.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the retained private batch result

```beat
id: reference
scene: reference
frames: 384
caption: Reveal the retained private batch result
narration: The retained Terra/high repair passes all 36 private fixtures. The oracle also passes
  all; the unchanged starter passes only twelve ordered encodings. Three encodings of each acquisition
  are correlated, so this is twelve acquisitions and one model attempt.
visual: Delayed private score matrix by encoding, distinct from public examples.
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

## Use complementary invariants to expose mistakes

```beat
id: controls
scene: controls
frames: 336
caption: Use complementary invariants to expose mistakes
narration: "Swapped spacings pass only the isotropic acquisition\u2019s three encodings. Logical\
  \ echo ordinals pass none. Storage reshape passes only ordered inputs. These diagnostics isolate\
  \ different errors and are separate from model attempts."
visual: Exact retained/replayed control counts and the invariant each checks.
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

## Separate exact equality from allowed roundoff

```beat
id: trace
scene: trace
frames: 288
caption: Separate exact equality from allowed roundoff
narration: The trace retains a failed exact dictionary comparison after moving geometry macros.
  The next inspection finds unchanged samples and labels, with a tiny affine difference. The numerical
  verifier later passes the complete private batch.
visual: Trace steps 16 and 17, exact mismatch and replayed corner error beside tolerance.
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

## A bounded pass; the study remains parked

```beat
id: limits
scene: limits
frames: 240
caption: A bounded pass; the study remains parked
narration: The repair succeeds on the declared synthetic profile. It does not establish full clinical
  DICOM conformance or robustness to missing slices, compression or multiple stacks. The user
  parked this study; this explanation launches no new trial.
visual: Observed result, declared scope and unresolved broader conditions.
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
