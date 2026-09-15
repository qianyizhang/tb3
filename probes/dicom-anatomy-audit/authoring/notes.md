# BR-004/A01 — Local anatomical annotation audit

## Frozen intent

The user explicitly requested a genuinely difficult, potentially subtle test set
with easy, unambiguous evaluation, followed by one fresh Terra/**max** attempt.
This revision changes the deliverable from a reusable checker to a fixed JSON
review report. The solver may use inspection or code. The intended unknown is
which patient-specific annotations are wrong and where; no anatomy rules,
reference masks, defect counts, mutation procedures, or diagnostic recipes are
provided to the solver. A geometry-only loader removes incidental DICOM plumbing.

The new `dicom-anatomy-audit` package has its own identity. The retired BR-003
`dicom-label-audit` bytes and trial remain intact. This remains a diagnostic,
not a demonstrated hard task until a valid new model attempt is evaluated.

## Cohort and case admission

Eight distinct subjects from the licensed TotalSegmentator small v2.0.1 dataset
were fetched using bounded ZIP reads (source URL/version/CRC/SHA-256 receipts
remain local). CTs and all 117 source masks are sampled at 3 mm and encoded as
new CT and sparse BINARY SEG objects. Synthetic patient fields and research
UIDs replace identity fields. Focus labels are confined to reviewed structures.

| Case | Source subject | Condition | Graded altered labels |
| --- | --- | --- | --- |
| case-74 | s0965 | Unchanged; limited coverage | None |
| case-19 | s1127 | Unchanged; marked thoracic abnormality | None |
| case-83 | s0629 | Superior kidney-pole cap omitted | kidney_left |
| case-46 | s0885 | Unchanged; source pathology | None |
| case-28 | s1233 | Local exchange of adjacent right-rib labels | rib_right_7, rib_right_8 |
| case-61 | s0915 | Inferior heart-apex cap omitted | heart |
| case-95 | s0344 | Unchanged; source pathology | None |
| case-32 | s1336 | Small kidney-label extension into adjacent fat/muscle | kidney_left |

There are four clean packets, four corrupted packets, **five graded altered
labels**, and 86 focus-label decisions. No clean and altered version of one
patient is supplied together. The cases are fixed and inspectable; do not
interpret the result as unseen-patient generalization.

The absence of a spleen mask in s0629/s0885 and unusual lung-lobe masks in some
sources were not accepted as proof of surgery or automatically labeled as source
errors. Spleen is excluded from the focus list for those two cases; lung lobes
are outside this cohort's focus list. No confirmed postoperative history was
found. These are coverage/pathology controls, **not certified postoperative
controls**. The proposed postoperative discrimination hypothesis remains untested.

Source review was by the task author using CT contacts, mask bounds and
orthogonal overlays; no specialist clinical adjudication is claimed. Source
contours inherit the dataset's annotation conventions. The final result must be
inspected for real source defects alleged by the solver before any model failure
is classified as genuine.

## Changes and ambiguity exclusions

`build.py` constructs truth before DICOM serialization. The kidney/heart
omissions remove 4% of their masks through a curved, tilted cap. They retain
Dice approximately 0.980. The adjacent-rib swap affects one local segment and
retains Dice approximately 0.851–0.864. The kidney extension retains Dice
approximately 0.994. Foreground, laterality and tissue-level averages alone do
not identify these errors.

Pretrial review changed the heart cap from the superior great-vessel junction
to the inferior apex, where omission is clearer. The muscle mask affected by
the kidney extension loses 20 voxels, all within a narrow boundary band; that
muscle label was removed from all focus lists rather than graded as a definite
omission. The kidney extension itself extends beyond the allowed 3-mm contour
band. The two cap defects include voxels remaining after multiple 3-mm-grid
interior erosions. These are source/contract admission adjustments made before
model execution, not post-result difficulty tuning. Draft receipts are retained
locally in `runs/br004-v1/build/`.

## Evaluation and controls

The grader reads only `findings.json`, without executing solver code. Each case
must have exactly its affected focus labels, one finding per label. Every point
must be within **3 mm** of an actual discrepancy-voxel center for that label,
computed directly from the private original/changed arrays and source affine.
There are no category-precedence arguments or prose judgments. Clean cases
require empty findings. Missing, extra and badly located findings are reported
separately; exact-case success and label-level denominators are retained.

Pretrial geometry validation caught a legacy filename-permutation collision on
a slice count divisible by 53. This revision uses seeded bijections for filenames
and instance numbers. The first failing author-validation log is retained; it
was not a model trial.

The source-reference highdicom round trip checks every serialized label voxel.
The public loader is separately compared with source CT, class IDs and affine.
An independent scalar affine formulation validates every retained discrepancy
coordinate. None of these geometry checks certifies clinical source truth.

Author controls include the reference report, no findings, every focus label,
correct labels with wrong points, omission of each individual true finding,
duplicate cases, nonfinite coordinates and the spatial tolerance boundary.
The reference report is derived from known edits; its oracle run establishes
that the expected artifact passes the grader, not that a general independent
anatomical detector was built. A replay of the old saved checker is a separately
reported baseline, never a fresh model attempt.

## Trial protocol

One fresh `openai/gpt-5.6-terra` attempt, `reasoning_effort=max`, using Harbor
0.14.0/Codex and local Docker. The explicit user request overrides the earlier
Terra/high diagnostic default. Retain the normal 1800-second budget, image/tool
access, public network policy and no additional answer guidance. Harbor 0.18.0
oracle/nop controls must pass on the same frozen package before this attempt.
No trial is hidden or repeated to manufacture a miss. Infrastructure or source
ambiguity is excluded from genuine failure; a healthy pass retires the snapshot.
A separate verifier receives the artifact and private evidence; neither the
reference report nor private evidence is included in the agent image.

Commands and hashes belong in the BR-004 execution freeze and final receipt.
Raw scans, renderings, logs and trajectories remain local. Required derived
input archives and their licenses remain task inputs under artifact governance.
