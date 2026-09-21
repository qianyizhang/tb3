Source: `docs/research-rounds/BR-024-harder-registration.md`; original SHA-256: `34e7e3a691087a4b5a379052c754735d8f39291194b50ad77f35677e69c91879`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-024 — harder real-deformation cases for Sol

Status: bounded curation and trial plan fixed before new candidate solving.

## Request and hypothesis

In the owning [research task](codex://threads/01a0a845-7c2d-7992-a662-24d52831af90),
the user asked: “for this kind of task, can you find more challenging cases for
sol to solve”. Exact message IDs are not exposed. This resumes research and
authorizes a bounded search, public-input feasibility work and fresh Sol/xhigh
trials on admitted cases. The closed site and sibling submission remain outside
scope.

BR-022/023 establish a concrete failure mechanism: locally plausible matches
and restricted search can select the wrong vessel branch; Sol recovered by
using broader anatomical context and a coherent regional displacement pattern.
The new hypothesis is that stronger nonuniform respiratory deformation on
different patients can challenge that strategy without changing tool access,
reasoning time, tolerance or output complexity. This is a candidate hypothesis,
not an established Sol failure or a population-difficulty claim.

## Data and selection fixed now

Use the two unused, already verified manual-landmark validation pairs 2 and 3
from the actual LungCT 1.11 release. Preserve the source and all previous task
bytes. These are distinct patients from the retired case 1. The same-pair
direction is exhale to inhale, with the nominal source frame supplied.

Generate near-coplanar oblique views using the BR-021 geometric constraints:
manual source landmarks ≤0.35 mm from the plane, ≥15-degree obliquity from
principal planes, source spans ≥70 mm in both image directions, image corners
inside the acquired volume, and 16 mm margins around query extrema. Keep
exactly eight queries; if a coplanar group is larger, select eight by deterministic
farthest-point sampling of source positions, seeded by its first source index.
No destination labels enter this subsampling step.

Require the privileged best global affine residual on the eight projected
source/manual destination points to exceed the earlier task's 3.5963 mm RMS.
Rank candidates within each patient by decreasing affine residual, then source
footprint and source-index tuple. Retain the three highest eligible distinct
query sets per patient for screening; do not keep searching until a model fails.
This uses annotations for deliberate curation, not for permitted solver inputs.
It does not establish image-matching difficulty by itself.

For each patient, admit the first ranked candidate that passes author image
visibility review and a public-input author feasibility solver. Retain every
screened candidate and outcome. Keep the prior NumPy/SciPy local-affine patch
baseline fixed for the first feasibility test. If it misses, a separately
recorded bounded public-input rescue method may be specified before its outcomes;
never label-init or optimize candidate selection with hidden scores. A candidate
without demonstrated public-input solvability is not admitted to model testing.

## Unchanged task and bounded model evaluation

Return eight corresponding destination-world points, using the same 3 mm RMS
and 5 mm maximum tolerances. Supply only the 2D view, its frame/query pixels,
destination CT, attribution and ordinary pinned numerical libraries. Exclude
the full exhale scan, annotations, baseline, prior agent code and all prior
analysis. Inspect actual source/manual-target patches for anatomical visibility;
this is author review, not expert clinical adjudication.

Admit at most two tasks, one per new patient. Freeze task bytes after public-input
isolation, independent interpolation/score checks and wrong-answer controls.
Run matched oracle/nop controls and exactly one fresh Sol/xhigh attempt per
admitted task, 1,800 seconds each, zero automatic retries, unchanged CPU/memory
and normal library/network access. No hints or follow-ups. Preserve provider,
execution and timeout problems separately from normal completed misses.

Audit the actual methods, external solver/annotation access and runtime context;
independently regrade outputs. A normal failure can establish a task-specific
candidate, but one selected case/attempt does not establish reliable difficulty.
Passes retire their exact snapshots. No extra repeated trials or stronger model
is automatically triggered in this round.

## Source review and ownership

The [official L2R evaluation repository](https://github.com/MDL-UzL/L2R) and
[Lung250M-4B project](https://github.com/multimodallearning/Lung250M-4B) distinguish
manual evaluation correspondences from algorithmic pseudo-labels and provide
registration benchmark context. The Learn2Reg dataset page returned HTTP 403
during this follow-up; the previously retained official release/metadata and
hash-verified arrays remain the source authority. No new access request or
unofficial mirror is needed for these two pairs.

New work uses `runs/br024-*`, `probes/registration-deformation/authoring/br024_*`,
`docs/research-rounds/BR-024-*` and `docs/evidence/br024-*`. Preserve BR-019 through
BR-023 plans, code, receipts, model sessions and generated evidence. Do not
change the closed interview site or sibling submission.
