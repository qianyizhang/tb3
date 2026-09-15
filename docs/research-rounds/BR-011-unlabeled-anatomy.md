# BR-011 — Identify anatomy, then separate unusual anatomy from errors

**Status: author screen complete; 17-object unlabeled prototype built; no model
trials.** The unusual-anatomy/error condition remains a design and curation plan.
The clean interview submission and historical task snapshots are unchanged.

## User decision and provenance

On 2026-09-15 the user accepted the [BR-010 recommendation](BR-010-mask-only-anatomy.md)
to pursue intact-mask identity consistency and screen simple geometric solutions.
They added “give unlabeled 3d representations ... infer their labels” and an
ultimate condition with “unlabelled 3d objects and with potentential mistake OR
rare disease.” The accepted annotation refers to message
`msg_02eac9aa6376934c016aa90af8b16c87d0b89f28f4b80bdf3d`.
The follow-up user message is retained in this conversation; its separate ID
was not captured. These requests authorize this follow-up; closed historical
documents do not supply that authorization.

## Three distinct hypotheses

| Candidate | Solver input and deliverable | Hypothesis and interpretation |
| --- | --- | --- |
| BR011-I1: identity audit | Intact 3-D instances with proposed labels; return corrected instance identities | Supplied plausible names may anchor judgment; a complete relation check may expose coordinated misidentification. Extends BR010-M01. |
| BR011-I2: identity inference | The same kind of intact instances with anonymous IDs; assign anatomical labels | Removing proposed names tests recognition from shape, spatial relationships and global arrangement. A pass where I1 fails could suggest anchoring, not weaker anatomical knowledge. |
| BR011-I3: identity plus quality | Anonymous objects, some containing substantial errors, in typical or verified unusual anatomy; assign identities and judge annotation quality separately | A solver may normalize valid unusual anatomy into a familiar template, or excuse an error because the case is unusual. These are untested hypotheses. |

I1/I2 require matched geometry, vocabulary, orientation and viewing support for
a useful comparison. I3 changes geometry/clinical context and is a separate
contrast. Complexity should come from the required relationships; adding many
objects or removing necessary context would confound the experiment.

## Completed author screen

The [reproducible script](../../probes/revisions/br011/authoring/screen_and_export.py)
uses the **unmodified source arrays**, not the prior injected defects, for eight
retained BR-004 patients. Methods were not tuned after seeing their scores.
This is an exploratory author screen, not a frozen model experiment.

### I1: simple ordering is already sufficient in most groups

Descending physical superior-coordinate centroids recover the source identities
for **23/24 groups**, covering L1–L5 and left/right ribs 5–10 in each patient.
The baseline receives the group and proposed-label multiset, as an I1 task would.
It does not solve unknown family membership or infer unseen vertebral counts.

All eight lumbar groups are solved. The one exception is the left rib group in
limited-coverage case 74: ribs 8/9 reverse centroid order. That exception is not
evidence of a valid hard task. It needs anatomical and coverage review.
Ordinary whole-instance label permutations on the solved groups are screened
out as difficulty leads. No model trial was spent on them.

### I2: a simple organ classifier supplies a useful baseline

A leave-one-patient-out nearest-template classifier gets **109/131 nonempty
organ identities** correct. Features are scan-normalized centroid coordinates,
log physical volume and three log bounding-box extents; each class template is
the coordinate-wise median from the seven other patients. Training-set standard
deviations scale the distance. There is no parameter search or one-to-one
assignment step. Missing source structures are not included as objects.

| Source patient | Correct / available identities |
| --- | --- |
| 19 | 14/16 |
| 28 | 16/17 |
| 32 | 16/17 |
| 46 | 14/16 |
| 61 | 13/17 |
| 74 | 8/16 |
| 83 | 14/15 |
| 95 | 14/17 |

No complete scene passes this weak classifier. Its errors do not establish
Sol/Terra difficulty or clinical truth. It has labeled training examples that
the prototype solver does not receive. The 131 instances are clustered within
eight patients, not independent benchmark trials. Case 74's partial coverage is
a likely limitation of scan-normalized features, not a reason to prefer it.

Both screens and the prototype export took **2.009 seconds** in the retained
run; this is author-script wall time, not solver time or verifier time. The
[receipt](../evidence/br011-author-screen.json) records inputs, methods, every
prediction, source hashes, script hash and exported-file hashes.
An independent rerun to a separate output directory reproduced both baseline
results and every public-file hash exactly.

## Concrete I2 prototype

The public example at `runs/br011-mask-identification/public/` contains:

- `objects.npz`: anonymous instance values, original 3 mm occupancy and LPS affine;
  no CT intensities or clean identity map.
- Seventeen generic-ID PLY surface point clouds in shared physical coordinates.
- `scene.json`, full 117-name vocabulary, a brief instruction, attribution and licenses.

All selected source voxels are preserved exactly. PLY coordinates were read back
and checked against the volume/affine. Object IDs, order and values are shuffled;
PLY filenames and geometry metadata contain no anatomical names. This is not a
claim of resistance to recognition of a public source scan.

The source identity key and reviewer preview are outside the public packet,
under `runs/br011-mask-identification/author/`. The interactive conversation
preview includes a source-identity reveal for human review and **must not be
given to a model as a blind task viewer**.

The selected source patient is 32; the prior small kidney extension is absent.
The baseline labels 16/17 objects correctly, confusing spleen with stomach.
This example demonstrates the representation, not a selected difficulty lead.
Source labels and mask-only inferability have not been independently adjudicated.

The [identity scorer](../../probes/revisions/br011/authoring/grade_identity.py)
checks exact object-to-label assignment and reports missing, extra and wrong
identities. All [eight scoring controls](../evidence/br011-grader-controls.json)
passed their intended outcomes: source key and reordered key pass; empty,
missing, duplicate, extra, wrong and malformed assignments fail. These checks
establish scorer behavior, not semantic validity or clinical fairness.

## Representation contract

Keep the volume authoritative. Use meshes as a convenient view of the same
surface, with conversion tolerance and topology checked. Surface points are
suitable for this prototype's shape inspection; they do not encode mesh faces
or establish network connectivity. The sparse conversation preview is not the
data used for scoring.

Keep shared position, orientation and millimetre scale. Do not rotate, reflect,
resize or center each object independently: that removes the pairwise evidence
the hypothesis is intended to test. Neutral IDs and colors must not encode
semantic identity. Supply a ready viewer and tested volume loader in a future
trial package. Do not make learning a file format the conceptual crux.

## I3: anatomy and annotation quality are separate axes

An unusual or diseased organ can be correctly annotated, and an annotation error
can coexist with unusual anatomy. Construct four conditions before testing:

| Anatomy | Faithful annotation | Deliberate annotation error |
| --- | --- | --- |
| Typical | Specificity control | Ordinary error control |
| Verified unusual anatomy | Preservation control | Combined challenge |

Each condition is its own task, with one fresh attempt per model/configuration;
do not turn all four into one long audit. Matched authoring controls may derive
from one subject, but solver contexts and artifacts must remain separate. Keep
matched-subject and cross-subject contrasts distinct.

The proposed answer separates:

1. `identities`: object ID to anatomical label, or label set for a genuinely
   merged object when that defect type is explicitly within scope.
2. `annotation_findings`: affected object IDs, defined structural error types,
   and an optional coarse geometric/graph witness.
3. `anatomy_pattern`: an observable structural pattern or `indeterminate` when
   the permitted evidence cannot establish a unique interpretation.

A named rare disease should be required only when verified source data and
the solver-visible evidence support that diagnosis. Prefer a clearly observable
structural pattern for a geometry task. Do not infer a clinical cause from a
shape alone or claim that an anatomical variant is necessarily a disease.

### Admission and grading

- Use verified source histories/annotations for unusual cases. Do not label the
  earlier BR-004 unusual patients as confirmed postoperative or rare-disease cases.
- A reviewer receiving **only the solver's inputs** must be able to establish
  the scored identities and defects. Author access to CT or an edit log cannot
  compensate for information withheld from the solver.
- Reject underdetermined boundary-loss or abnormal-shape cases from a binary
  error test. Alternatively, explicitly test justified indeterminacy with a
  pre-adjudicated key; do not make blanket abstention pass identifiable cases.
- Prefer wrong mergers, substantial misplaced pieces or wrong branch relations
  only when the visible context rules out valid anatomical alternatives.
  Their clinical-looking appearance alone is not sufficient evidence.
- Avoid one-voxel bridges, mesh-conversion scars and tiny surface deviations.
  Validate meaningful physical margins and representation invariance.
- Grade identity, error detection and preservation of valid anatomy separately,
  plus overall task success. Accept equivalent witnesses and valid synonymous
  labels; freeze the mapping and admissible alternatives before any model run.

## Source candidates, not yet acquired or admitted

[VerSe's official repository](https://github.com/anjany/verse) documents masks,
centroids, variant label conventions including T13/L6, and a fracture-grading
dataset reference. It is a concrete starting point for structural variants and
pathology with documented provenance. Its data license is CC BY-SA 4.0, distinct
from the repository's MIT code license. No VerSe data were downloaded here.

The [VerSe 2020 data paper](https://arxiv.org/abs/2103.06360) describes anatomical
variant ratings. The [VERIDAH preprint](https://arxiv.org/abs/2601.14066) reports
enumeration-aware labeling results and motivates checking the labeling convention
carefully. Neither paper establishes that its diagnoses are inferable from masks
alone, nor that Sol/Terra fail our proposed conditions. Published source tasks
remain calibration references rather than original submissions.

## Next execution boundary

The approved direction has produced a baseline screen and a concrete I2 example.
I1 requires a case with a meaningful relation crux beyond the successful ordering
baseline. I2 requires blind identity/ambiguity review. I3 requires verified
source context and mask-only adjudication. No candidate is yet admitted for a
model trial; no new Sol/Terra success or failure is claimed.

After admission, preserve one trial per task/model configuration, normal time
allowances and exact frozen inputs. Record success, identity accuracy, missed
errors, false repairs, time, output/uncached-input tokens and verifier time.
Keep author-screen costs separate. Do not select a rare-looking source solely
because a cheap baseline fails on it.

## Local reproduction

```sh
.venv-br003/bin/python probes/revisions/br011/authoring/screen_and_export.py \
  --output runs/br011-reproduction \
  --evidence runs/br011-reproduction/author-screen.json
.venv-br003/bin/python probes/revisions/br011/authoring/grade_identity.py \
  --expected runs/br011-reproduction/author/expected.json --controls
```

Requires existing local BR-004 source arrays and NumPy. It does not install
dependencies, execute models, alter historical inputs or write the submission.
