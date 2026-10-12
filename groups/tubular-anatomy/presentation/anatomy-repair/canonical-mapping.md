# BR-026 native trace → canonical player

**Inspected 2026-10-12.** `tb3-vessel-connection-repair` currently uses the
synthetic `local-edit` / `local-edit-v1` story. Prototype commit `0e1d1a92`
supplies the native MRA six-phase retained-run explanation. Keep the binary-grid
invariant witness as an operation example; its intact control is not the real
BR-026 companion patient's disputed unchanged-case result.

## Evidence and local payload

Task root: `runs/br026-vessel-repair/tasks/vessel-v01/`.
Run root: `runs/br026-vessel-v01-terra-high-v1-20260916/vessel-v01__c6dKGRX/`.
Attempt `vessel-v01__c6dKGRX`: Terra/high, 32 steps, 300.813302 recorded seconds.
The source is TopCoW 2024 MRA case 007 with an authored 200-voxel deletion.
Paths below are relative to those roots; sizes are current local file bytes.

| Role | Exact source | Bytes / native contract |
| --- | --- | --- |
| Source MRA | task `environment/data/image.nii.gz` | 1,342,816; 187×132×53; complete oblique NIfTI RAS affine |
| Given mask / edit domain | task `environment/data/proposed_mask.nii.gz`, `editable_region.nii.gz` | 27,933 / 11,607; same native grid |
| Actual tools | run `agent/trajectory.json` | 875,935; selected calls, outputs and timestamps |
| Saved output | run `artifacts/app/answer/corrected_mask.nii.gz` | 27,983; original mask union the 198-voxel threshold-165 component |
| Private references / scorer | task `tests/truth.npz`, `tests/score.py` | 47,151 / 5,706; GT, corridors, anchors, labels, mask-derived centerlines |
| Frozen evaluation | run `verifier/metrics.json` | 1,066; all 12 checks reproduced exactly |

The [finding](../../findings/br026-gap-trace.md),
[workbench manifest](../../findings/evidence/br026-gap-trace.json) and
[derivation receipt](../../findings/evidence/br026-gap-visuals.json) pin sources.
`prepare.py` reads retained arrays and the reviewed guarded scorer; it must not
be imported as a general assembly library because its top level writes derivatives.

`.local/anatomy-pose/vessel/data.json` is **1,597,452 B**; standalone `index.html`
is **2,193,371 B**. Current payload has native display volume/mask/editable arrays
(each **1,308,252 decoded B**, gzip 770,115 / 12,761 / 3,817 B), exposed voxel
surface (**241,224 vertices**, little-endian float32, **2,894,688 decoded B**,
362,887 gzip B), nine candidate/contact index sets, saved additions, two residual
reference voxels, frozen/initial evaluations, MIP, 14 trace excerpts and **19**
delivered-image pointers. Delivered step sets are 10,11,13,15,19,22,24,27.

Payload state keys are `threshold, count, indices, contacts`; trace keys are
`step, time, call, output` (`call` is one joined string). Top-level compressed keys
are `volume, mask, editable, surface`; `surface_vertices` gives the vertex count.
Reference/score keys are `residual, frozen, initial`; output indices use `added`.
`delivered` items use `step, file`. Normalize these differences at assembly rather
than accepting two untyped payload shapes in the shared reader. All eleven source
pins and the recipe pin match current bytes; local `receipt.json` equals the
tracked derivation receipt. No stale pin was found. Generated data/media/HTML
are not output-hashed in this receipt; canonical packaging needs those hashes.

## Chapter / frame / control mapping

Initial canonical timing proposal: six discrete chapters, **144 frames per chapter, 192 for the third at
24 fps / 912 total**. Frames provide reading time; no growth animation should
imply recorded intermediate voxels between the nine retained thresholds.

| Frames | Chapter | Recorded steps | State and interaction |
| --- | --- | --- | --- |
| 0–143 | Receive inputs | 7, 9; images 10, 11 | Whole network + MRA; original mask only; source slice axis/index and orbit |
| 144–287 | Find missing signal | 12,14,17,18,20,21,23,25,26; images 13,15,19,22,24,27 | Local crop near seed `(66,76,15)`; candidate at 250; explain reviewed alternatives without implying largest component is correct |
| 288–479 | Scan thresholds | 28 | Nine discrete threshold states; candidate, slice overlay and exact count change together; start 250 |
| 480–623 | Test contacts | 29 | Threshold 165; amber patches contain 32 + 33 voxels; 26-neighbor candidate-to-mask contacts |
| 624–767 | Save bounded edit | 31 | Switch from reconstructed component to actual `saved & ~input`; 198 additions, zero removals/outside-domain edits |
| 768–911 | Reveal evaluation | 31 plus verifier | Explicit reference reveal: two missed voxels magenta, 198/200 authored gap recovered, 12/12 checks pass |

Threshold→count: **150→247; 160→212; 165→198; 170→186; 180→178;
190→170; 200→155; 220→122; 250→89**. These are deterministic native-intensity
reconstructions of step 28, not new agent attempts. Seed component is
`(image >= threshold) & ~mask & editable`, 26-connected. The displayed uint8
70..650 intensity mapping cannot be used to recalculate these thresholds.

Reader orbit/reset, whole/local focus, axis/index and before/after toggle remain
separate from recorded actions. ROI uses half-open native ranges
`[49:83,59:94,7:25]`; local clipping edges are display boundaries, not vessel ends.
Index flattening is C-order `(i*132+j)*53+k`; exposed corners are index ±0.5,
transformed by the complete affine. Slice panels retain native samples, nearest
neighbor and physical aspect ratio. Blue-gray input / teal candidate or saved
addition / amber contacts / magenta reference residuals require a matching legend.

## Shared contract and integration risks

- **Common native-trace envelope:** use the same identity, role-separated source
  hashes, dimensions/affine/convention, derivation, selected-asset closure,
  discrete chapter state, reference reveal and fallback contract as the CT mapping.
  Vessel adapter owns compressed native arrays, surface, index sets, slices and
  counts; shared reader owns timeline, accessible chapter controls and provenance.
- **Saved-output switch:** at save/evaluation phases always render `added`, not
  the reader-selected threshold state. Threshold alternatives must not change the
  frozen final answer, evaluation, or meaning of the teal legend.
- **Private role gating:** initial route metrics, gap count, residual indices and
  frozen checks are evaluator-derived; prevent them appearing as solver knowledge
  before reveal. Browser-embedded data is a reader package, not access isolation.
- **Coordinate identity:** CT uses LPS; this uses RAS. Carry the convention
  explicitly; do not reuse CT scene mapping as a patient-space conversion. Preserve
  obliquity, C-order indexing and half-open ROI bounds.
- **Selective packaging:** this payload exceeds the 1 MiB Git artifact boundary;
  keep generated arrays/media local and package per selected entry. Do not bundle
  every patient dataset with every catalogue reader. Include all 19 delivered
  files, source notice/data license and Three.js MIT attribution. Source permissions
  require TopCoW attribution; commercial use requires owner permission.
- **Scope gaps:** full original scan and continuous screen/optimizer history are
  absent. Global input Dice 0.9984509813033443 and one foreground component do
  not establish the local route. Local Dice 0.9973333333333333 and 100% centerline
  coverage within 0.45 mm are this frozen calibration's engineering checks.
  Companion unchanged patient remains a separate disputed condition; no population,
  image-necessity or clinical claim follows.

Retained `check.mts` / local `browser-check.json` cover phases, thresholds,
contacts, full affine, slices, keyboard, 390 px and no-WebGL. Canonical checks must
also cover selected asset closure, no reference leakage/reset, saved-output
independence from reader controls and chapter stability. Static fallback retains
real MRA slices, threshold/count controls and source links. This mapping leaves
historical scores and acceptance receipts intact.
