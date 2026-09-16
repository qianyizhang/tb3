# BR-026 — vessel repair feasibility results

The two fresh Terra/high diagnostics completed normally. The synthetic gap
passes: 198 of 200 removed voxels recovered, the tested connection restored,
and no collateral edits. The unchanged case fails the frozen preservation
limits after 244 additions, while preserving the absent right Pcom. Its added
region follows visible MRA signal beside the left anterior cerebral artery;
reference disagreement is established, but an anatomical error is not.

A simple public-input image-guided baseline passes both cases. Retain the gap
as calibration and hold the unchanged-case disagreement for independent
adjudication. This experiment does not establish a clean hard-task candidate.

[Predeclared plan](BR-026-vessel-repair-experiment.md) ·
[Source curation](BR-025-vessel-connectivity.md) ·
[Frozen tasks and author controls](../evidence/br026-freeze.json) ·
[Result receipt](../evidence/br026-results.json) ·
[Trace audit](../evidence/br026-trace-audit.json)

| Condition | Terra/high result | Agent time | Delivered change |
| --- | --- | --- | --- |
| V01: synthetic right-Pcom gap | Pass | 300.8 s | 198 of 200 deleted voxels recovered; no other edits |
| V02: unchanged asymmetric mask | Fail: preservation limits | 646.2 s | 244 added voxels (12.903 mm³); absent right Pcom preserved |

## What was tested

Each task supplies one native-grid MRA crop, a proposed binary vessel mask and
a broad editable Circle of Willis region. It asks for a corrected mask and
allows returning the original mask if no supported connectivity defect exists.
The task does not disclose which condition it contains. Source class labels,
graph nodes, reference masks, author code and verifier inputs are excluded
from the agent image. The source notice and public network access remain.

- **V01 / MRA 007:** bilateral posterior communicating arteries (Pcom), with
  a spherical 1.8 mm-radius deletion in the right Pcom. It removes 200 voxels
  (10.576 mm³); image intensities are unchanged. This is a synthetic defect,
  not a segmentation-model prediction.
- **V02 / MRA 012:** unchanged reference mask with left Pcom present and right
  Pcom annotated absent. This checks preservation of an acceptable asymmetric
  mask; the annotation does not independently prove congenital absence.

Both image crops preserve the original stored samples, affine, spacing and
NIfTI scaling. Reloaded intensities equal the source crop exactly. The source
data come from [TopCoW](https://zenodo.org/records/15692630), with
[derived graph/node annotations](https://zenodo.org/records/17358162).
The latter are derived from the masks, not independent anatomical truth.

The local verifier checks connection routes, physically weighted centerline
coverage, local reference overlap, absent-branch preservation and unintended
changes. A globally connected foreground mask can still contain the Pcom gap;
whole-volume connected-component count cannot resolve this task. The delivered
unchanged V01 mask has 99.845% whole-mask Dice while its local route is broken.

## Gap result

Terra/high completed V01 normally in 300.8 seconds. Its output adds 198 voxels,
all belonging to the 200-voxel authored deletion. It removes no original
foreground. The local Dice is 0.99733, both tested Pcom centerlines have 100%
coverage, and all preservation checks pass.

![Native axial section: source, proposed mask, Terra repair and reference](../../runs/br026-vessel-repair/terra-gap-result.png)

The trace shows MRA projections, slice montages and orthogonal image review,
followed by intensity-component analysis and testing for distinct contacts
with the existing mask. No external source-answer retrieval or private
reference access was observed in the retained trajectory. This establishes
observed image use; no image-ablation experiment establishes its necessity.

## Unchanged-case failure and reference disagreement

V02 completed normally in 646.2 seconds. Its output adds 244 voxels and deletes
none. Added volume is 12.903 mm³ versus the 2 mm³ preservation allowance;
9.307 mm³ lies more than 0.6 mm from reference foreground versus the 1 mm³
allowance. These are the only failed checks. The present left Pcom retains
100% centerline coverage, the absent right Pcom stays absent, and all voxels
outside the editable region remain unchanged. Whole-mask Dice is still 99.814%.

The trace shows substantial image review, followed by addition of an unmasked
component above intensity 160 containing crop voxel `(97, 31, 35)`. No source
answer retrieval was observed. The source-label review finds contacts only
with label 12, the left anterior cerebral artery. It does not find a new
right-Pcom connection. Ordinary errors in agent-created analysis code were
recovered; this is a completed score failure, not a timeout or infrastructure
exclusion.

![Orthogonal image sections through the added region](../../runs/br026-vessel-repair/terra-unchanged-result.png)

The added component has median signal 201 versus 84 in the nearby unmasked
neighborhood. Its visible signal matters: source-mask disagreement alone
does not establish that the structure is anatomically false. We have not
independently adjudicated a false connection versus an unlabelled vessel or
annotation-scope mismatch. Retain the exact failed score, but do not count it
as confirmed anatomical reasoning failure. See the
[post-outcome discrepancy receipt](../evidence/br026-discrepancy-review.json)
and [manual trace review](../evidence/br026-trace-review.json).

## Baselines and validity checks

| Public-input method | Synthetic gap | Unchanged mask |
| --- | --- | --- |
| Deliver proposed mask unchanged | Fail: broken local route | Pass |
| Skeleton endpoints plus local mask closing | Fail: local Dice 0.718; route broken | Pass |
| Skeleton endpoints plus local image threshold | Pass: local Dice 0.925; 100% centerline coverage | Pass |

The image baseline sees only the same public input files. It detects nearby
skeleton endpoints, uses surrounding vessel signal to choose a local
threshold, and adds 284 voxels. It is calibrated on these development cases;
its success does not estimate unseen-case accuracy. The original 1 mm³
collateral allowance was increased to 2 mm³ before freeze because that
plausible repair added 1.216 mm³ of nearby boundary foreground. The separate
1 mm³ cap on distant foreground remains. Neither threshold is clinically
validated, and neither was adjusted to a model output.

The frozen author controls comprise 20 observations. They include acceptable
non-identical repairs, delivered unchanged masks, broad closing, erasure,
present-branch deletion, thin bridges, collateral damage, missing output,
wrong affine and nonbinary values. Nop creates no output and must fail both
tasks; it is distinct from delivering the original mask for V02.

Each condition received matched Docker oracle/nop controls and one fresh
Codex `openai/gpt-5.6-terra` attempt at `high`, with 1800 seconds available and
automatic retries disabled. Harbor 0.18.0 runs the controls and 0.14.0 runs
the agent. Runtime trace labels are checked against the requested model and
effort; this is not provider-side attestation. Delivered artifacts are scored
again independently, and each task's checksum must match across its controls
and agent run.

All four Docker controls returned their expected outcomes: oracle 1 and nop 0
for each task. Both delivered masks reproduce the recorded verifier checks on
independent replay. All frozen task files and recorded authoring-file hashes
remain unchanged. No automatic retry or second-model run was launched.

Freeze SHA-256:
`563b6336e756ca1cfc37a86ffb7646012b346333efae591b38300939436ba60e`.
The [receipt](../evidence/br026-results.json) contains local raw-result paths,
answer hashes, replay outcomes, timing and usage metadata. Raw data and masks
remain under ignored `runs/`; those links require this local workspace.

## Interpretation and limits

This is an annotation-backed engineering feasibility test with one passing
repair and one preservation failure carrying unresolved reference ambiguity.
It does not establish a hard agent task, natural segmentation-error repair,
clinical correctness or repair of a real false connection. The two conditions use
different patients; they are not matched image-ablation controls. One fresh
attempt per condition cannot estimate a general success rate.

Do not enlarge the synthetic cut or tighten tolerances to manufacture a
failure. A future difficulty claim needs a separately admitted, image-resolvable
error from a frozen segmentation prediction, with retained model/preprocessing
provenance and training-source overlap. That work was not part of these two
diagnostics, and no further trial is automatically queued.
