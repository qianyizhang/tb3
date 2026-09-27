# Airway local-route pass and detached preservation controls

**The retained Terra/high pass is valid for the frozen local-route contract.** A01
joins its requested components; A02/A03 correctly preserve already connected
routes inside detached fragments. They do not establish parent-tree completeness.
This agent-authored audit reproduces the retained scope correction without changing
scores, historical source records or task bytes.

## Contract and assistance

The solver received CT, an unchanged released-model binary airway prediction,
editable region and ordered RAS+ mm anchors. Crops and requests were selected with
reference assistance. The natural omission was not injected. No deletions or edits
outside the region were allowed; already connected requests had to remain exactly
unchanged. Each of three requests required a mask, centerline and eight CPRs.
Private `reference.npz` held GT, core, path/tube and CT copies; it was mounted for
the verifier, not supplied as solver input. See the
[brief](../presentation/briefs/tb3-airway-repair.md) and frozen
[instruction](../../../runs/br033-airway-routing/tasks/airway-route-cpr/instruction.md).

## Original measures and independent scope audit

| Request | Added / removed voxels | Core coverage | Route p95, mm | Full-crop components before → after | Parent interpretation |
| --- | --- | --- | --- | --- | --- |
| A01 | 578 / 0 | 433/495 = 87.47% | 0.449146 | 7 → 6 | Requested components join; unrelated fragments remain |
| A02 | 0 / 0 | 64/64 = 100% | 0.701316 | 2 → 2 | Both anchors remain in one detached 89-voxel fragment |
| A03 | 0 / 0 | 266/266 = 100% | 0.405966 | 7 → 7 | Both anchors remain in one detached 348-voxel fragment |

All three original anatomy/CPR evaluations pass; original reward **1**, one
`openai/gpt-5.6-terra` high-effort attempt. The core is GT intersected with a 1.5 mm
reference-path tube and editable region; for preservation controls it is further
restricted to proposed foreground. The denominator is task-selected core, not
all airway tissue. The gate is coverage ≥0.80; route p95 ≤1.2 mm and reference
coverage ≥0.90. A01 CPR HU p99 error is **0.005699 HU** against ≤0.2 HU.

The full-crop 26-neighbour audit is separate from the frozen route-tube connection
check. A01 joins anchor components of 6018 and 348 voxels into 6944 voxels. A02/A03
remain outside the largest component. Corner contact counts under this technical
connectivity rule; branch identity and clinical interpretation are not adjudicated.
A01/A03 share identical image/mask/affine and are not independent patients.

A current [saved-output replay](evidence/airway-local-route-replay.json) of the frozen
scorer retains every pass/metric,
except A01's negligible CPR coordinate error changes from 5.684785957944772e−13 to
5.684341886080801e−13 mm. This is **saved-artifact replay**, not a fresh attempt.
The [new source audit](../presentation/sources/airway-repair-audit.json) independently
reproduces public-CT sampling for **131,560 saved CPR pixels**, maximum error
4.55e−13 HU. The larger frozen HU errors use the private unrounded affine; public
NIfTI sform storage differs by at most 7.63e−6 mm. Both measures are retained.

## Source, output and reference views

The [canonical story](../presentation/stories/airway-repair.story.md) starts with
public inputs. Blue is the proposed mask; orange marks anchors/editable regions;
green reveals saved added voxels, centerline and CPR sampling coordinates; pink
reveals the private core with a dashed reference path. Fixed physical display
rotations and one uniform fit per case preserve relative geometry. A01/A03 use the
same fit. Cases are not registered to one another.

Nine native sections around each public review centre retain original pixels,
physical aspect and a fixed −1000…200 HU window. Meshes derive from mask values;
padding creates artificial crop caps, not anatomical endpoints. CPRs are actual
submitted images with separate arc/offset axes. For display, saved HU is linearly interpolated along its slightly nonuniform arc
onto twice-dense uniform rows. Pixel centres retain physical calibration; no new
CT samples are generated, and the original row raster remains in the source pack. A moving route cursor and rotating
CPR display are reader inspection, not a solver trajectory or new medical result.
The historical [scope figure](../../../runs/br033-airway-routing/viewer-review-20260916/repair-and-unrepaired-controls.png)
was inspected alongside the actual delivered sagittal and axial CT montages.
A projection alone does not prove connectivity; numerical checks use the 3D arrays.

## Consequential trace actions

The retained [trajectory](../../../runs/br033-airway-cpr-terra-high-v1-20260916/airway-route-cpr__rJDn6xz/agent/trajectory.json)
contains 14 shell calls, two image inspections and two code patches.

- **Steps 9–15:** matplotlib was unavailable; the agent used installed Pillow,
  generated montages and viewed sagittal/axial A01 CT with prediction/edit context.
  This recovered local tool issue did not terminate the trial.
- **Steps 16–22:** CT threshold/component exploration led to a saved rule: if
  anchor components differ, select the CT <−700 HU editable non-mask component
  touching both. Independent calculation exactly reproduces the 578 added voxels.
  Connected anchors trigger no addition. A distance-to-boundary path cost and
  approximately 0.25 mm resampling produce the centerline and CPRs.
- **Steps 23–26:** a public-grid containment check exposed an A02 endpoint just
  outside a nominal array edge due to affine rounding. The patch used native voxel
  centres for endpoints; final endpoint differences are ≤7.63e−6 mm. The submitted
  mask additions remained 578/0/0. The saved final outputs are authoritative.

The retained command audit found no network/private-reference command matches.
That does not establish absence of pretraining exposure or make public annotations
secret. No agent authoring script was imported or rerun for this explanation.

## Fitness, comparisons and alternatives

- **Instruction/scorer alignment:** the explicit endpoint contract explains the
  preserved fragments. A parent-tree requirement cannot be retroactively imposed
  on this attempt. The retained user-triggered scope correction identifies a
  control-selection/presentation flaw, not model failure.
- **GT fitness:** AeroPath annotations combine semi-automated construction,
  manual engineering refinement and pulmonologist checking. The
  [source paper](https://doi.org/10.1371/journal.pone.0311416) also notes incomplete
  GT can label valid predicted branches as false positives. This audit verifies
  crop/grid provenance and selected technical measures; it does not clinically
  adjudicate airway completeness. No contrary evidence invalidates this local pass.
- **Matched frozen validation:** oracle passes; unchanged mask with oracle route
  geometry fails A01. Wrong-edit, route, arc and fabricated-HU controls fail. These
  are verifier diagnostics with reference exposure, not independent model trials.
- **Diagnostic development comparison:** mask-only and image baselines were
  author-built before freeze; image v2 was tuned after underfilling and passes.
  Postfreeze nearest-component and straight-anchor shortcuts fail A01. Selection,
  tuning and exposure differ; these results do not prove general difficulty.
- **Coverage:** three screened patients yielded three requests from two patients.
  A04 was excluded before the trial for boundary sensitivity. True absence,
  false connection and clinically intact parent-tree controls were not admitted.
  Reopening broader repair claims requires a new task revision and adjudicated
  controls; no such trial is authorized by this explainer work.

## Provenance and limits

The [evidence manifest](evidence/airway-local-route-scope.json) identifies the mixed
BR-033 experiment; only its airway pilot is interpreted here. The separate
TopBrain study has its own Explorer entry. The new builder verifies all **36 frozen
files**, nine retained dataset members, unchanged source crops, final answer hashes,
three connectivity audits and CT sampling. Model predictions remain retained
outputs of the official released Raidionics single-patch model, not a claim to
reproduce the paper's entire ensemble. No inference or new optimizer was run.

AeroPath [repository](https://github.com/raidionics/AeroPath) and
[dataset record](https://doi.org/10.5281/zenodo.10069289) identify provenance. The
retained dataset license.md and frozen data license say CC-BY-4.0; historical HF
card metadata said MIT. The mismatch remains recorded; code MIT is not a data
license substitution. The current web rendering did not independently resolve
that mismatch. See [asset terms and derivation](../../../presentation/task-explorer/airway-repair/NOTICE.md).
The portable HTML embeds private reader references and is not a solver packet.
