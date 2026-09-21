Source: `docs/research-rounds/BR-028-results.md`; original SHA-256: `6fb3f9d87a055601c9969bd3c3d80264ab3ac997b256c62ba4dcb7f8f19e1f15`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-028 — supply the full source CT

**Later user adjudication (2026-09-16): accepted visually.** The user reviewed
q06 and judged the worst case good enough. This retires the full-source
condition as a hard-task candidate, superseding the selection disposition
below while retaining the frozen numerical result. See the
session synthesis (repository source locator: `../research-registration-session.md`) and
adjudication record (repository source locator: `../evidence/br028-adjudication.json`).

Status at numerical closeout: complete. The full-source attempt improves substantially but still
misses one landmark. No further attempt is scheduled.

**Sol/xhigh finishes normally at 2.60 mm RMS / 6.41 mm maximum** with the full
source CT, compared with 12.73 / 32.20 mm for the earlier 2D-source attempt.
The RMS criterion now passes; q06 alone exceeds the unchanged 5 mm maximum.
The other seven points are within 2.2 mm.

The original failing case did **not** consist only of small 2D patches. Its
inputs were one complete 121×189 oblique exhale slice and a full 192×192×208
inhale CT. Small patches were extracted by the solver and by the review page.
The missing information was depth in the **source** acquisition. BR-028 adds
the full 192×192×208 exhale CT while retaining every earlier public data file.

## Matched inputs and evaluation

| Item | BR-024 | BR-028 |
| --- | --- | --- |
| Source image | One oblique 2D slice | Same slice plus full exhale CT |
| Target image | Full inhale CT | Byte-identical full inhale CT |
| Query locations | Eight fractional source pixels and plane frame | Byte-identical pixels and frame |
| Desired destination points | Eight private manual correspondences | Byte-identical reference answers |
| Acceptance | RMS ≤3 mm and maximum ≤5 mm | Identical grader and tolerance |
| Agent | Sol/xhigh, 1,800 seconds, four CPUs, 4 GiB | Same settings, fresh attempt |

Only the task name, prompt passages describing source availability, and one
new `reference_volume.npz` differ in the task snapshot. This is an information
addition, with the original view retained as an available solution route.
Source positions are still derived from public pixel/plane geometry, including
the original ≤0.35 mm off-plane approximation; hidden manual source coordinates
are not substituted.

The new NPZ contains only HU and voxel-to-world geometry and exactly matches
the retained source NIfTI. An independent interpolator reproduces all **22,869**
original view pixels within **0.000031 HU**. The actual initial task image has
exactly seven public files including the source notice, an empty answer
directory, and no private annotations, prior solver or earlier answer.

## Author methods and feasibility

| Fixed author method inside the new image | RMS / maximum | Outcome |
| --- | ---: | --- |
| Retained 2D translation-only method | **2.133 / 3.416 mm** | Pass; answer bytes identical to BR-024 |
| Supplementary local-affine 3D patch method | **7.403 / 19.459 mm** | Fail |

The 3D method derives its source queries from the public plane geometry and
runs the existing numerical matcher without new tuning. It recovers the two
points that dominated the earlier Sol failure: q02 is 2.16 mm away and q04
1.78 mm away. It makes new errors at q05 (19.46 mm) and q06 (6.74 mm).
This is a different method as well as a different information use; it does not
isolate a causal depth benefit.

The frozen protocol (repository source locator: `BR-028-registration-3d-source.md`) specifies the 3D author
method as supplementary rather than an admission gate. The unchanged passing
2D route remains available and proves permitted solvability of the enriched
task. No post-score rescue, threshold adjustment or label-based initialization
was performed.

## Fresh Sol attempt

Matched oracle/nop controls complete normally at 1/0 on the same task checksum.
The agent receives no previous code, outputs, failure analysis or hints. Its
recorded runtime is `gpt-5.6-sol`, `xhigh`, with the frozen instruction. It stops
voluntarily after **893.4 seconds (14m 53s)**, before the unchanged 30-minute
limit, with no exception. Independent host scoring matches exactly.

| Same patient and reference points | RMS | Maximum | Points beyond 5 mm | Outcome |
| --- | ---: | ---: | --- | --- |
| BR-024: 2D source slice + 3D target | 12.731 mm | 32.203 mm | q02, q04, q06 | Normal failure |
| BR-028: full source CT added | **2.604 mm** | **6.412 mm** | **q06 only** | Normal failure |

| Previously failing point | 2D-source attempt | Full-source attempt |
| --- | ---: | ---: |
| q02 | 14.780 mm | **1.891 mm** |
| q04 | 32.203 mm | **1.408 mm** |
| q06 | 5.821 mm | **6.412 mm** |

## How Sol used the added depth

The recorded code explicitly loads `reference_volume.npz` as the fixed/source
image and `volume.npz` as the moving/target image, preserving affine geometry.
It derives the same source-world positions from the unchanged pixel queries and
plane frame. It therefore uses the new 3D information, rather than simply
repeating the source slice into a thin slab as in BR-024.

Sol first runs full-volume multiresolution Diffeomorphic Demons and
FastSymmetricForces Demons through the preinstalled SimpleITK library. It
compares smoothing settings and histogram matching, then notices disagreement
between the resulting landmark positions. These four saved field candidates
all fail independently when scored afterward: RMS ranges from 9.62 to 19.36 mm.
A further full-volume B-spline candidate also fails. Library registration alone
does not solve this instance.

It then performs its own **broad 3D normalized-cross-correlation search** using
actual volumetric source patches at three sizes. This search starts at the
nominal public source coordinates, rather than being centered on an already
wrong dense-field estimate. The search offsets are [-22,12], [-24,16], [-12,18]
voxels along the three dataset axes. An offline geometry check confirms that
all eight manual destinations lie inside that search region. Sol follows with
SciPy Powell refinement, comparing translation and regularized local affine
models over spherical patches of radius 9, 13.5 and 18 mm, plus sensitivity and
image checks.

The final q06 coordinate, [219.3, 162.3, 150.2] mm, is the rounded local rigid
13.5 mm fit. The model's visible commentary treats its boundary candidate as
resolved, but it remains 6.41 mm from the reference. At least two of its earlier
Diffeomorphic Demons fields contained a better q06 estimate (1.02 and 2.40 mm
errors), while being wrong elsewhere. Those are posthoc scores of saved public-
input candidates, not oracle-picked submissions or new model attempts.
The remaining problem includes choosing which estimate to trust; merely
computing several candidates is insufficient.

The candidate-state evidence (repository source locator: `../evidence/br028-stage-analysis.json`) retains
all captured named candidate point arrays and the search-coverage calculation.
The trace shows preinstalled SimpleITK plus authored NumPy/SciPy/Pillow work;
no external installation, download or annotation lookup is observed. The final
coordinates are written manually after comparisons, so there is no single
executable rule fully specifying the model's selection across settings.
Work scripts deleted during the model's final cleanup were already preserved
in read-only capture snapshots.

## Interpretation

The enriched attempt removes the two large correspondence errors and leaves
one moderate boundary mismatch. Retain its exact snapshot as a single-attempt
failure candidate. This result does not establish repeatable difficulty, or
that full-volume input makes registration easy or hard in general.

One fresh attempt per condition does not separate the added information from
different strategy choices and model variability. Here both the information
and the selected strategy differ: broad volumetric patch matching replaces the
earlier narrow refinement around a wrong deformation. The passing retained 2D
author method already demonstrates that the original view is solvable by at
least one permitted method; depth was not logically necessary for that route.

Eight sparse point tolerances are engineering acceptance criteria, not validation
of a dense deformation field or clinical usefulness. Public annotations leave
possible training contamination despite initial-image and trace audits. Earlier
task freezes and results, concurrent cardiac/vessel experiments, the closed site
and the sibling submission remain unchanged.

## Evidence

- Interactive comparison (repository source locator: `../../runs/br028-registration-3d-source/review/index.html`):
  original source plane and three orthogonal source/target review planes.
- Fixed protocol (repository source locator: `BR-028-registration-3d-source.md`),
  plan (repository source locator: `../evidence/br028-plan.json`), task freeze (repository source locator: `../evidence/br028-freeze.json`),
  and author audit (repository source locator: `../evidence/br028-author-audit.json`).
- Completed trial receipt (repository source locator: `../evidence/br028-results.json`) and
  saved candidate scores (repository source locator: `../evidence/br028-stage-analysis.json`).
- Concise interpretation (repository source locator: `../evidence/br028-approach-analysis.json`).
- Authoring and reproduction (repository source locator: `../../probes/registration-deformation/authoring/br028_README.md`).
- Original BR-024 result and failure analysis (repository source locator: `BR-024-results.md`).

Source: Learn2Reg LungCT 1.11, Hering, Murphy and van Ginneken (2020), Radboud
University Medical Center, [CC BY 4.0](https://doi.org/10.5281/zenodo.3835682).
Native source data, model sessions, intermediate arrays and generated reports
remain local.
