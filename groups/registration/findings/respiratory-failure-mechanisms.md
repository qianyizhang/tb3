# Different correspondence defects survive composition repair

The selected case-one miss contains a real composition defect, but fixing it does
not rescue the retained pipeline. Search support and patch similarity explain
different queries. The two predeclared fresh attempts split: one fails and one passes.

## Measured evidence

| Comparison | RMS / maximum, mm | Supported interpretation |
| --- | --- | --- |
| Selected original Terra/high | 12.641 / 23.796 | Retrospectively selected miss |
| Same transforms, direct B, seed 17, ±9 mm | 12.410 / 23.786 | Minimal composition repair does not rescue this pipeline |
| Original mapping, seed 17, ±30 mm | 19.989 / 34.662 | Including every target does not ensure optimizer success |
| Direct B, seed 17, ±30 mm | 13.799 / 32.156 | Wider support also fails after minimal repair |
| Fresh Terra/high repeat 2 | 24.905 / 34.165 | Normal completed failure |
| Fresh Terra/high repeat 3 | 2.021 / 4.646 | Normal completed pass; counters stable difficulty |

The frozen gate is **RMS ≤ 3 mm AND maximum ≤ 5 mm over eight points**. Exact
unrounded grades remain in [the original results](../../../docs/evidence/br022-results.json)
and [analysis receipt](../../../docs/evidence/br022-solver-analysis.json).
All 12 primary mapping/bounds/seed combinations and both secondary refits fail.
Matched oracle/no-op rewards are 1/0. No original score has been changed.

## Task and reference fitness

- **Solver context:** one complete 171 × 118 exhalation section, complete target
  CT (192 × 192 × 208), eight fractional-pixel queries and known source pose.
  Target spacing is 1.75 × 1.25 × 1.75 mm; source spacing is 1.25 mm. There is no
  full source volume. Return ordered target XYZ rows in dataset-world millimetres.
- **Reference boundary:** manual target points and reference-centred image samples
  are postmortem author inputs. Fresh agents received the same frozen public task,
  with no postmortem hints, prior code or prior answers. The reference comes from
  Learn2Reg LungCT case one; archive/manual-coordinate provenance and preprocessing
  are retained in [the respiratory source audit](../../../presentation/task-explorer/respiratory/manifest.json).
- **Fitness checks:** all 15 frozen task files match; query IDs and scorer output
  shape align. Oracle success and an independent fresh pass oppose a blanket
  impossibility or broken-grader explanation. Neither proves every correspondence
  is unique or independently clinically adjudicated. Affine prealignment, cropped
  coverage and public annotation exposure limit generalization.

## Replay and consequential code

**Numerical fidelity:** recovered original trace steps 12–19 reproduce the eight
final coordinates with maximum drift **6.3006320465 × 10⁻⁹ mm**. Saved intermediate
stages are reconstructed, not original trace-time dumps. The original image was
removed; the historical replay used an identical-Dockerfile retained image, pinned
packages and identical public files, with network disabled and no GT mounts.
This explanation reads saved artifacts; it performs no new historical replay.

**Composition defect:** in the recovered `reg2d.py`, lines 10–14 always fit against
the original moving image. Line 19 computes `movaff`, but line 22 does not use it
when fitting B. Line 33 then applies `A(B(x))`. The minimal consistent mapping uses
the unchanged fitted B directly. A separate structural intervention refits B
against the A-resampled image before applying A(B(x)); it is not a swap of transform
order. SimpleITK defines the composite queue as [A(B(x))](https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1CompositeTransform.html)
and registration maps [fixed physical points to moving physical points](https://simpleitk.readthedocs.io/en/master/registrationOverview.html).

The selected original trajectory is
`runs/br021-deform-2d-terra-high-v1-20260916/deform-2d__YR5xbbH/agent/trajectory.json`.
Recovered code is `runs/br022-registration-postmortem/recovered/reg2d.py`.
Steps 20–21 visualize, step 22 explores other patch sizes without replacing the
submitted coordinates, and step 23 writes the step-19 result. Code and trajectory
hashes are in the source pack manifest.

## Different query mechanisms

- **q04: excluded search support.** In the saved orthonormal basis the manual
  target requires offsets **(−9.115, −27.270, +14.194) mm**. Its Euclidean distance
  from the original ±9 mm cube is **18.994 mm**, already above the 5 mm maximum
  gate. Even the eight-point best possible RMS inside those boxes is 6.78 mm
  (6.67 after minimal repair). The paired projections retain a full 3D distance;
  neither projection alone is the error. At ±30 mm all manual targets are inside.
  The same finite optimizer budget is not an exhaustive search, so continued
  failure then does not establish geometric impossibility.
- **q01/q06: objective disagreement within support.** Both targets lie in the
  original box, yet errors are 16.334 and 8.638 mm. For q01 the saved objective is
  0.269 at the manual target, 0.588 at the submission and 0.485 at the best point
  found by a privileged finite search within 3 mm of the manual target. q06 has
  the same ordering (0.521, 0.669, 0.620). This supports a mismatch between this
  fixed local appearance objective and these manual correspondences. It is not
  proof of a global optimum, a universal NCC cutoff, or a bad manual annotation.
- **q02: counterexample to a single-cause explanation.** Its target is 2.65 mm
  outside the box, which does not itself preclude a point within the 5 mm gate.
  A searched near-reference point scores 0.722 versus 0.599 at the submission.
  This differs from q01/q06 and leaves initialization/optimization relevant.

**Actual visual inspection:** the complete source section and q01/q06 source,
manual-target and submitted patches were opened at useful scale. All six patches
are derived from the frozen HU arrays on the recorded 21 × 21 sampling grid, using
0.8 mm steps and saved target axes. They show comparable coarse local structures;
appearance alone does not adjudicate the manual targets. These panels are
independently centred for appearance comparison, not a shared-frame displacement
view. The grayscale window (−1000 to 200 HU) is for display; the objective uses
original HU, 0.4 raw NCC plus 0.6 high-pass NCC with sigma 1.6 samples.

The animated objective is 101 recorded evaluations along the straight segment
from manual target to submitted point. It is a diagnostic interpolation, never
the optimizer trajectory. The asset builder independently reproduces all **808**
curve samples with maximum difference **0**, all **112** query-to-box distances,
14 counterfactual grades, four author-control grades and the saved stage grades.
The [source notice](../../../presentation/task-explorer/registration-analysis/NOTICE.md)
and canonical [story](../presentation/stories/registration-failure-analysis.story.md)
provide the pixel derivation, labels and reader-only reveals.

## Context control and successful counterexample

| Author patch model | Small context, 8/8/8 mm | Multiscale, 25/16/10 mm |
| --- | --- | --- |
| Translation | 25.521 / 51.659, fail | 1.959 / 3.877, pass |
| Local affine | 24.689 / 44.873, fail | 2.309 / 4.456, pass |

Cells report RMS / maximum in mm. This is a **diagnostic 2 × 2 comparison** inside
a separate author pipeline with fixed broad nominal search, blur, optimizer and
candidate rules. Context helps there; extra local affine freedom does not. It
does not repair the original agent pipeline or isolate the cause of the fresh pass.
Independent per-query translations can form a globally nonrigid correspondence.

**Fresh repeat 3 uses small numerical patches too.** Its retained trajectory steps
15 and 19–22 show broader parallel-plane candidate search, visual candidate review,
patch-radius stability checks and continuous orientation refinement. Step 15 uses
15 × 15 samples at 1.25 mm, normal offsets ±30 mm and in-plane offsets ±35 mm;
step 20 tests 9 × 9 through 21 × 21 patches. Step 22 combines local translation
with 3D orientation. No single component’s causal contribution was isolated.
Trace locator: `runs/br022-deform-2d-terra-high-r3-v1-20260916/deform-2d__GsTbtot/agent/trajectory.json`.
The pinned record manifest identifies its exact hash. Retained traces show no
observed external annotation download; this cannot prove absence of all exposure.

## Comparability and limits

- **Matched fresh cohort:** exactly two predeclared independent Terra/high sessions,
  zero retries, identical task checksum, normal voluntary completion within 1800 s.
  The selected original is reported separately; do not pool it into a population rate.
- **Diagnostic interventions:** same saved original pipeline for primary repairs;
  secondary refits change the fitting stage. The author context control has its own
  pipeline. These are component studies, not additional autonomous attempts.
- **Failure attribution:** a reproduced composition defect and q04 support
  exclusion are direct technical observations. q01/q06 support objective
  disagreement under fixed axes. Reference ambiguity remains unresolved; no
  clinical correction is asserted. Infrastructure timeout does not explain the
  recorded normal completions. A sparse eight-point pass does not validate a field.
- **Decision:** the historical pass-retirement rule retires this exact snapshot
  as reliably difficult for Terra. Any new patient, difficulty condition or trial
  needs a separately authorized frozen study. None is launched by this explanation.

## Provenance

- [Finding](respiratory-failure-mechanisms.json), [record evidence manifest](evidence/respiratory-failure-mechanisms.json)
- [BR-022 protocol](../experiments/br022/protocol.md), [retained round account](../../../docs/research-rounds/BR-022-results.md)
- [Asset hashes and independent checks](../../../presentation/task-explorer/registration-analysis/manifest.json)
- [Import-safe asset builder](../../../scripts/build_registration_analysis_assets.py)
